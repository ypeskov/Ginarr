from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import TIMESTAMP, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.db import Base
from app.models.BaseEmbeddingModel import BaseEmbeddingModel
from app.models.EmbeddingType import EmbeddingType

# --- CONSTANTS FOR CLARITY ---
OPENAI_EMBEDDING_MODEL_ID = "text-embedding-3-large"
OPENAI_EMBEDDING_DIMENSION = 3072
# -----------------------------


class OpenAIEmbedding(Base, BaseEmbeddingModel):
    __tablename__ = "openai_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True)
    chunk_id: Mapped[int] = mapped_column(ForeignKey("memory_chunks.id", ondelete="CASCADE"), nullable=False)
    embedding: Mapped[Vector] = mapped_column(Vector(OPENAI_EMBEDDING_DIMENSION), nullable=False)
    embedding_model_name: Mapped[str] = mapped_column(
        String(length=100), default=OPENAI_EMBEDDING_MODEL_ID, nullable=False
    )

    embedding_type_id: Mapped[int] = mapped_column(ForeignKey("embedding_types.id"), nullable=False, default=1)
    embedding_type: Mapped[EmbeddingType] = relationship("EmbeddingType")

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), onupdate=func.now(), server_default=func.now()
    )
