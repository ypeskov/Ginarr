from datetime import datetime
from typing import Optional

from icecream import ic
from pgvector.sqlalchemy import Vector
from sqlalchemy import Result, cast, desc, func, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.logger.app_logger import log
from app.models.BaseEmbeddingModel import BaseEmbeddingModel
from app.models.EmbeddingType import EmbeddingType, EmbeddingTypeName
from app.models.MemoryChunk import MemoryChunk
from app.models.OpenAIEmbedding import OpenAIEmbedding
from app.services.embedding.backends.base import EmbeddingBackend
from app.services.embedding.embedding_errors import (
    EmbeddingGetError,
    EmbeddingModelNotFoundError,
)
from app.services.embedding.embedding_service import get_embedding_provider
from app.services.embedding.registry.models import AvailableEmbeddingModels

ic.configureOutput(includeContext=True)


# supported embedding models
embedding_model_registry = {
    AvailableEmbeddingModels.TEXT_EMBEDDING_3_LARGE: OpenAIEmbedding,
    AvailableEmbeddingModels.TEXT_EMBEDDING_3_SMALL: OpenAIEmbedding,
    # "mistral": MistralEmbedding,
    # "gemini": GeminiEmbedding,
}


def get_embedding_model(embedding_model_name: AvailableEmbeddingModels) -> type[BaseEmbeddingModel]:
    """
    Get the embedding model class by name.
    Args:
        embedding_model_name: (str) name of the embedding model
    Returns:
        (type[BaseEmbeddingModel]) embedding model class
    Raises:
        (EmbeddingModelNotFoundError) if the embedding model is not found
    """
    embedding_model = embedding_model_registry.get(embedding_model_name)
    if not embedding_model:
        raise EmbeddingModelNotFoundError(f"Unknown embedding model: {embedding_model_name}")

    return embedding_model


async def search_embeddings(
    db_session: AsyncSession,
    user_id: int,
    query: str,
    embedding_types: list[str],
    embedding_model_name: AvailableEmbeddingModels = AvailableEmbeddingModels.TEXT_EMBEDDING_3_LARGE,
    embedding_provider_name: str = settings.EMBEDDING_PROVIDER,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> list[MemoryChunk]:
    embedding_model: type[BaseEmbeddingModel] = get_embedding_model(embedding_model_name)
    # Get query embedding
    provider: EmbeddingBackend = get_embedding_provider(provider=embedding_provider_name)
    try:
        query_vector = (await provider.get_embeddings([query], model=embedding_model_name.value))[0]
    except EmbeddingGetError as e:
        log.error(f"Failed to get embeddings: {str(e)}")
        raise EmbeddingGetError(f"Failed to get embeddings: {str(e)}")

    # Resolve embedding_type_id for requested names
    result = await get_embedding_types_by_name(db_session, embedding_types)
    type_map = {name: id_ for id_, name in result.all()}
    if not type_map:
        return []

    # Base cosine similarity query
    score_expr = (1 - func.cosine_distance(embedding_model.embedding, cast(array(query_vector), Vector))).label("score")
    stmt = (
        select(MemoryChunk, score_expr)
        .join(embedding_model, embedding_model.chunk_id == MemoryChunk.id)
        .where(MemoryChunk.user_id == user_id)
        .where(embedding_model.embedding_type_id.in_(type_map.values()))
    )

    if from_date:
        stmt = stmt.where(MemoryChunk.created_at >= from_date)
    if to_date:
        stmt = stmt.where(MemoryChunk.created_at <= to_date)

    stmt = stmt.order_by(desc(score_expr))

    result = await db_session.execute(stmt)
    rows = result.all()

    # Attach score directly to chunk
    for chunk, score in rows:
        chunk.score = score

    return [chunk for chunk, _ in rows]


async def get_embedding_types_by_name(
    db_session: AsyncSession, embedding_types: list[str]
) -> Result[tuple[int, EmbeddingTypeName]]:
    """
    Get embedding types by name.
    Args:
        db_session: (AsyncSession) database session
        embedding_types: (list[str]) list of embedding type names
    Returns:
        (Result[tuple[int, EmbeddingTypeName]]) result of the query
    Raises:
        (EmbeddingGetError) if the query fails
    """
    try:
        result = await db_session.execute(
            select(EmbeddingType.id, EmbeddingType.name).where(EmbeddingType.name.in_(embedding_types))
        )
    except EmbeddingGetError as e:
        log.error(f"Failed to get embedding types: {e}")
        raise EmbeddingGetError(f"Failed to get embedding types: {e}")

    return result
