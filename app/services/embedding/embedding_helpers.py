from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.EmbeddingType import EmbeddingType, EmbeddingTypeName


async def get_embedding_type_id_by_name(
    session: AsyncSession,
    name: EmbeddingTypeName,
) -> int:
    """
    Get the ID of an embedding type by its name.
    Raises ValueError if not found.
    Args:
        session: (AsyncSession) The database session
        name: (EmbeddingTypeName) The name of the embedding type
    Returns:
        (int) The ID of the embedding type
    """
    stmt = select(EmbeddingType.id).where(EmbeddingType.name == name)
    result = await session.scalar(stmt)

    if result is None:
        raise ValueError(f"EmbeddingType with name '{name}' not found in DB")

    return result
