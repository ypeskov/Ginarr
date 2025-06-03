from app.services.embedding.backends.base import EmbeddingBackend
from app.services.embedding.backends.openai_embedding import OpenAIEmbeddingBackend
from app.config.settings import settings

_EMBEDDING_PROVIDERS = {
    "openai": OpenAIEmbeddingBackend,
}


def provide_embedding_backend(embedding_provider: str = settings.EMBEDDING_PROVIDER) -> EmbeddingBackend:
    if embedding_provider in _EMBEDDING_PROVIDERS:
        return OpenAIEmbeddingBackend()
    else:
        raise ValueError(f"Unsupported embedding provider: [{embedding_provider}]")
