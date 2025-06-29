from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped


class BaseEmbeddingModel:
    embedding: Mapped[Vector]
    chunk_id: Mapped[int]
    embedding_type_id: Mapped[int]
