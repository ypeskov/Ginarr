from datetime import datetime

from sqlalchemy import Integer, String, Enum, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.db import Base
import enum


class EmbeddingTypeName(str, enum.Enum):
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    URL = "url"
    PDF = "pdf"
    DOCUMENT = "document"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    CSV = "csv"
    JSON = "json"
    XML = "xml"


class EmbeddingType(Base):
    __tablename__ = "embedding_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[EmbeddingTypeName] = mapped_column(
        Enum(EmbeddingTypeName), unique=True, nullable=False, default=EmbeddingTypeName.TEXT
    )
    description: Mapped[str] = mapped_column(String(length=255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<EmbeddingType(id={self.id}, name='{self.name}')>"
