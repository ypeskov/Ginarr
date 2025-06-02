from sqlalchemy.orm import Mapped
from pgvector.sqlalchemy import Vector


class BaseEmbeddingModel:
    embedding: Mapped[Vector]
    chunk_id: Mapped[int]
    embedding_type_id: Mapped[int]
