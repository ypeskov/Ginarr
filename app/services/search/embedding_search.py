from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, cast
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import array

from app.models.MemoryChunk import MemoryChunk
from app.models.OpenAIEmbedding import OpenAIEmbedding
from app.models.EmbeddingType import EmbeddingType
from app.services.embedding.embedding_service import get_embeddings


async def search_embeddings(
    db_session: AsyncSession,
    user_id: int,
    query: str,
    embedding_types: list[str],
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
):
    # Get query embedding
    query_vector = (await get_embeddings([query]))[0]

    # Resolve embedding_type_id for requested names
    result = await db_session.execute(
        select(EmbeddingType.id, EmbeddingType.name).where(EmbeddingType.name.in_(embedding_types))
    )
    type_map = {name: id_ for id_, name in result.all()}
    if not type_map:
        return []

    # Base vector similarity query
    stmt = (
        select(
            MemoryChunk,
            func.cosine_distance(OpenAIEmbedding.embedding, cast(array(query_vector), Vector)).label("score"),
        )
        .join(OpenAIEmbedding, OpenAIEmbedding.chunk_id == MemoryChunk.id)
        .where(MemoryChunk.user_id == user_id)
        .where(OpenAIEmbedding.embedding_type_id.in_(type_map.values()))
    )

    if from_date:
        stmt = stmt.where(MemoryChunk.created_at >= from_date)
    if to_date:
        stmt = stmt.where(MemoryChunk.created_at <= to_date)

    stmt = stmt.order_by("score")

    result = await db_session.execute(stmt)
    rows = result.all()

    # Attach score directly to chunk
    for chunk, score in rows:
        chunk.score = score

    return [chunk for chunk, _ in rows]
