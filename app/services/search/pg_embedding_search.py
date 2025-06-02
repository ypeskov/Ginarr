from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, cast, Result, desc
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import array
from icecream import ic

from app.core.logger.app_logger import log
from app.models.MemoryChunk import MemoryChunk
from app.models.BaseEmbeddingModel import BaseEmbeddingModel
from app.models.EmbeddingType import EmbeddingType, EmbeddingTypeName
from app.services.embedding.embedding_service import get_embeddings
from app.services.embedding.embedding_errors import EmbeddingGetError, EmbeddingModelNotFoundError
from app.services.embedding.embedding_registry import embedding_model_registry

ic.configureOutput(includeContext=True)


def get_embedding_model(embedding_model_name: str) -> type[BaseEmbeddingModel]:
    embedding_model = embedding_model_registry.get(embedding_model_name)
    if not embedding_model:
        raise EmbeddingModelNotFoundError(f"Unknown embedding model: {embedding_model_name}")

    return embedding_model


async def search_embeddings(
    db_session: AsyncSession,
    user_id: int,
    query: str,
    embedding_types: list[str],
    embedding_model_name: str = "text-embedding-3-large",
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
):
    embedding_model: type[BaseEmbeddingModel] = get_embedding_model(embedding_model_name)
    # Get query embedding
    try:
        query_vector = (await get_embeddings([query]))[0]
    except EmbeddingGetError as e:
        log.error(f"Failed to get embeddings: {str(e)}")
        raise EmbeddingGetError(f"Failed to get embeddings: {str(e)}")

    # Resolve embedding_type_id for requested names
    result = await get_embedding_types_by_id(db_session, embedding_types)
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


async def get_embedding_types_by_id(
    db_session: AsyncSession, embedding_types: list[str]
) -> Result[tuple[int, EmbeddingTypeName]]:
    try:
        result = await db_session.execute(
            select(EmbeddingType.id, EmbeddingType.name).where(EmbeddingType.name.in_(embedding_types))
        )
        ic(result)
    except EmbeddingGetError as e:
        log.error(f"Failed to get embedding types: {e}")
        raise EmbeddingGetError(f"Failed to get embedding types: {e}")

    return result
