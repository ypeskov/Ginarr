from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger.app_logger import log
from app.models.MemoryChunk import MemoryChunk
from app.services.memory.memory_errors import MemoryAddError
from app.services.embedding.embedding_service import generate_embeddings_from_memory_chunk
from app.services.embedding.embedding_errors import EmbeddingSaveError

ic.configureOutput(includeContext=True)


async def store_memory(db: AsyncSession, user_id: int, content: str) -> MemoryChunk:
    """
    Store a memory chunk for a given user
    Args:
        db: (AsyncSession) The database session
        user_id: (int) The ID of the user
        content: (str) The content of the memory chunk
    Returns:
        (MemoryChunk) The stored memory chunk
    """
    log.info(f"Storing memory chunk for user [{user_id}] with content [{content[:100]}...]")
    memory = MemoryChunk(user_id=user_id, content=content)

    try:
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        log.info(f"Memory chunk stored for user [{user_id}] with ID [{memory.id}]")
        try:
            # TODO: queue embedding job for async retry
            await generate_embeddings_from_memory_chunk(db, memory.id, content)
        except EmbeddingSaveError as e:
            log.error(f"Error generating embeddings for memory chunk [{memory.id}]: {str(e)}")
            raise MemoryAddError(f"Error generating embeddings for memory chunk [{memory.id}]: {str(e)}")
    except Exception as e:
        log.error(f"Error storing memory for user [{user_id}]: {str(e)}")
        raise MemoryAddError(f"Error storing memory for user [{user_id}]: {str(e)}")

    return memory
