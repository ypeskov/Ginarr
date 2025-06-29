from abc import ABC, abstractmethod

from app.models.EmbeddingType import EmbeddingTypeName


class EmbeddingBaseStore(ABC):
    @abstractmethod
    async def get_embedding_type_id_by_name(self, name: EmbeddingTypeName) -> int:
        raise NotImplementedError

    @abstractmethod
    async def save_embeddings(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        embedding_model_name: str,
        memory_chunk_id: int,
    ) -> bool:
        raise NotImplementedError
