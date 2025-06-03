from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.embedding.stores.embedding_base_store import EmbeddingBaseStore
from app.models.EmbeddingType import EmbeddingType, EmbeddingTypeName
from app.models.OpenAIEmbedding import OpenAIEmbedding
from app.core.logger.app_logger import log
from app.services.embedding.embedding_errors import EmbeddingSaveError


class EmbeddingPostgresStore(EmbeddingBaseStore):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_embedding_type_id_by_name(self, name: EmbeddingTypeName) -> int:
        """
        Get the ID of an embedding type by its name.
        Raises ValueError if not found.
        Args:
            name: (EmbeddingTypeName) The name of the embedding type
        Returns:
            (int) The ID of the embedding type
        """
        stmt = select(EmbeddingType.id).where(EmbeddingType.name == name)
        result = await self.session.scalar(stmt)

        if result is None:
            raise ValueError(f"EmbeddingType with name '{name}' not found in DB")

        return result

    async def save_embeddings(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        embedding_model_name: str,
        memory_chunk_id: int,
    ) -> bool:
        # we use only TEXT embedding type for now
        # TODO: add support for other embedding types
        embedding_type_id = await self.get_embedding_type_id_by_name(EmbeddingTypeName.TEXT)

        for chunk_text, vector in zip(chunks, embeddings):
            obj: OpenAIEmbedding = OpenAIEmbedding(
                chunk_id=memory_chunk_id,
                embedding=vector,
                embedding_model_name=embedding_model_name,
                embedding_type_id=embedding_type_id,
            )
            self.session.add(obj)

        try:
            await self.session.commit()
            log.info(f"Embeddings generated and saved for memory chunk [{memory_chunk_id}]")
            return True
        except EmbeddingSaveError as e:
            log.error(f"Error saving embeddings for memory chunk [{memory_chunk_id}]: {str(e)}")
            raise EmbeddingSaveError(f"Error saving embeddings for memory chunk [{memory_chunk_id}]: {str(e)}")
