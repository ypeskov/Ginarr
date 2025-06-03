from abc import ABC, abstractmethod


class EmbeddingBackend(ABC):
    @abstractmethod
    async def get_embeddings(self, texts: list[str], model: str) -> list[list[float]]:
        raise NotImplementedError

    @abstractmethod
    def split_text_into_chunks(self, text: str, max_tokens_per_chunk: int) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def save_embeddings(
        self,
        db_session,
        memory_chunk_id: int,
        embeddings: list[list[float]],
        model: str,
        embedding_type_id: int,
    ) -> bool:
        raise NotImplementedError
