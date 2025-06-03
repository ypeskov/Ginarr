from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.logger.app_logger import log
from app.services.embedding.embedding_errors import EmbeddingSaveError, EmbeddingGetError
from app.services.embedding.stores.embedding_postgres_store import EmbeddingPostgresStore
from app.services.embedding.backends.base import EmbeddingBackend
from app.services.embedding.backends.provider import provide_embedding_backend
from app.services.embedding.stores.embedding_base_store import EmbeddingBaseStore


def get_embedding_provider(provider: str = settings.EMBEDDING_PROVIDER) -> EmbeddingBackend:
    return provide_embedding_backend(provider)


async def generate_embeddings_from_memory_chunk(
    db: AsyncSession,
    memory_chunk_id: int,
    text: str,
    embedding_store: EmbeddingBaseStore | None = None,
    model: str = settings.OPENAI_EMBEDDING_MODEL,
    embedding_provider_name: str = settings.EMBEDDING_PROVIDER,
    max_tokens_per_chunk: int = settings.OPENAI_EMBEDDING_MAX_CHUNK_SIZE,
) -> bool:
    """
    Generate and save OpenAI embeddings for a given memory chunk
    Args:
        db: (AsyncSession) The database session
        memory_chunk_id: (int) The ID of the memory chunk
        text: (str) The text to generate embeddings for
        model: (str) The model to use for generating embeddings
        max_chunk_size: (int) The maximum size of a chunk
    Returns:
        (list[OpenAIEmbedding]) The list of generated embeddings
    """
    if embedding_store is None:
        embedding_store = EmbeddingPostgresStore(db)

    embedding_provider: EmbeddingBackend = get_embedding_provider(provider=embedding_provider_name)

    chunks = embedding_provider.split_text_into_chunks(text, max_tokens_per_chunk=max_tokens_per_chunk)
    try:
        embeddings = await embedding_provider.get_embeddings(chunks, model=model)
    except EmbeddingGetError as e:
        log.error(f"Error getting embeddings for memory chunk [{memory_chunk_id}]: {str(e)}")
        raise EmbeddingGetError(f"Error getting embeddings for memory chunk [{memory_chunk_id}]: {str(e)}")

    try:
        saved: bool = await embedding_store.save_embeddings(
            chunks=chunks,
            embeddings=embeddings,
            embedding_model_name=model,
            memory_chunk_id=memory_chunk_id,
        )
    except EmbeddingSaveError as e:
        log.error(f"Error saving embeddings for memory chunk [{memory_chunk_id}]: {str(e)}")
        raise EmbeddingSaveError(f"Error saving embeddings for memory chunk [{memory_chunk_id}]: {str(e)}")

    return saved
