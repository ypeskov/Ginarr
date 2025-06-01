import tiktoken
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.config.settings import settings
from app.models.OpenAIEmbedding import OpenAIEmbedding
from app.models.EmbeddingType import EmbeddingTypeName
from app.core.logger.app_logger import log
from app.services.embedding.embedding_errors import EmbeddingGetError, EmbeddingSaveError
from app.services.embedding.embedding_helpers import get_embedding_type_id_by_name


async def generate_embeddings_from_memory_chunk(
    db: AsyncSession,
    memory_chunk_id: int,
    text: str,
    model: str = settings.OPENAI_EMBEDDING_MODEL,
    max_tokens_per_chunk: int = settings.OPENAI_EMBEDDING_MAX_CHUNK_SIZE,
) -> list[OpenAIEmbedding]:
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
    chunks = split_text_into_chunks(text, max_tokens_per_chunk=max_tokens_per_chunk)
    embeddings = await get_embeddings(chunks, model=model)

    results = []
    # we use only TEXT embedding type for now
    # TODO: add support for other embedding types
    embedding_type_id = await get_embedding_type_id_by_name(db, EmbeddingTypeName.TEXT)
    for chunk_text, vector in zip(chunks, embeddings):
        obj: OpenAIEmbedding = OpenAIEmbedding(
            chunk_id=memory_chunk_id,
            embedding=vector,
            embedding_model_name=model,
            embedding_type_id=embedding_type_id,
        )
        db.add(obj)
        results.append(obj)

    try:
        await db.commit()
        log.info(f"Embeddings generated and saved for memory chunk [{memory_chunk_id}]")
    except EmbeddingSaveError as e:
        log.error(f"Error saving embeddings for memory chunk [{memory_chunk_id}]: {str(e)}")
        raise EmbeddingSaveError(f"Error saving embeddings for memory chunk [{memory_chunk_id}]: {str(e)}")

    return results


def split_text_into_chunks(
    text: str,
    max_tokens_per_chunk: int = settings.OPENAI_EMBEDDING_MAX_CHUNK_SIZE,
    model: str = settings.OPENAI_EMBEDDING_MODEL,
) -> list[str]:
    """
    Split text into chunks based on token count, respecting max_tokens_per_chunk
    Args:
        text: (str) The text to split into chunks
        max_tokens_per_chunk: (int) The maximum number of tokens per chunk
        model: (str) The model to use for tokenization
    Returns:
        (list[str]) The list of chunks
    """
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)

    chunks = []
    for i in range(0, len(tokens), max_tokens_per_chunk):
        chunk_tokens = tokens[i : i + max_tokens_per_chunk]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)

    return chunks


async def get_embeddings(texts: list[str], model: str = settings.OPENAI_EMBEDDING_MODEL) -> list[list[float]]:
    """
    Call OpenAI API to get embeddings for a list of texts
    Args:
        texts: (list[str]) The list of texts to get embeddings for
        model: (str) The model to use for generating embeddings
    Returns:
        (list[list[float]]) The list of embeddings
    """
    log.info(f"Getting embeddings for {len(texts)} texts")
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = await client.embeddings.create(
            input=texts,
            model=model,
        )
        log.info(f"Embeddings generated for {len(texts)} texts")
        return [e.embedding for e in response.data]
    except EmbeddingGetError as e:
        log.error(f"Failed to get embeddings: {str(e)}")
        raise EmbeddingGetError(f"Failed to get embeddings: {str(e)}")
