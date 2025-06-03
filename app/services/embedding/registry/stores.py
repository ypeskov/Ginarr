from enum import Enum


class AvailableEmbeddingStores(Enum):
    POSTGRES_EMBEDDING_STORE = "postgres"
    QDRANT_EMBEDDING_STORE = "qdrant"
