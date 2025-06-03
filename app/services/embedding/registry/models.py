from enum import Enum

from app.models.BaseEmbeddingModel import BaseEmbeddingModel
from app.models.OpenAIEmbedding import OpenAIEmbedding
from app.services.embedding.embedding_errors import EmbeddingModelNotFoundError


class AvailableEmbeddingModels(Enum):
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"


# supported embedding models
embedding_model_registry = {
    AvailableEmbeddingModels.TEXT_EMBEDDING_3_LARGE: OpenAIEmbedding,
    # "mistral": MistralEmbedding,
    # "gemini": GeminiEmbedding,
}


def get_embedding_model(embedding_model_name: AvailableEmbeddingModels) -> type[BaseEmbeddingModel]:
    """
    Get the embedding model class by name.
    Args:
        embedding_model_name: (str) name of the embedding model
    Returns:
        (type[BaseEmbeddingModel]) embedding model class
    Raises:
        (EmbeddingModelNotFoundError) if the embedding model is not found
    """
    embedding_model = embedding_model_registry.get(embedding_model_name)
    if not embedding_model:
        raise EmbeddingModelNotFoundError(f"Unknown embedding model: {embedding_model_name}")

    return embedding_model
