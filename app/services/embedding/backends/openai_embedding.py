import tiktoken
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.embedding.embedding_errors import EmbeddingGetError
from app.config.settings import settings
from app.core.logger.app_logger import log
from app.services.embedding.backends.base import EmbeddingBackend


class OpenAIEmbeddingBackend(EmbeddingBackend):
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())

    async def get_embeddings(self, texts: list[str], model: str = settings.OPENAI_EMBEDDING_MODEL) -> list[list[float]]:
        """
        Call OpenAI API to get embeddings for a list of texts
        Args:
            texts: (list[str]) The list of texts to get embeddings for
            model: (str) The model to use for generating embeddings
        Returns:
            (list[list[float]]) The list of embeddings
        """
        log.info(f"Getting embeddings for [{len(texts)}] texts")

        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=model,
            )
            log.info(f"Embeddings generated for [{len(texts)}] texts")
            return [e.embedding for e in response.data]
        except EmbeddingGetError as e:
            log.error(f"Failed to get embeddings: {str(e)}")
            raise EmbeddingGetError(f"Failed to get embeddings: {str(e)}")

    def split_text_into_chunks(
        self, text: str, max_tokens_per_chunk: int = settings.OPENAI_EMBEDDING_MAX_CHUNK_SIZE
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
        enc = tiktoken.encoding_for_model(settings.OPENAI_EMBEDDING_MODEL)
        tokens = enc.encode(text)

        chunks = []
        for i in range(0, len(tokens), max_tokens_per_chunk):
            chunk_tokens = tokens[i : i + max_tokens_per_chunk]
            chunk_text = enc.decode(chunk_tokens)
            chunks.append(chunk_text)

        return chunks

    async def save_embeddings(
        self,
        db_session: AsyncSession,
        memory_chunk_id: int,
        embeddings: list[list[float]],
        model: str,
        embedding_type_id: int,
    ) -> bool:
        return True
