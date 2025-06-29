from datetime import datetime
from enum import Enum

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, Text, func
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.db import Base
from app.models.User import User


class MemorySourceType(str, Enum):
    CHAT_MESSAGE = "chat_message"
    EMAIL = "email"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    SLACK = "slack"


class MemoryChunk(Base):
    __tablename__ = "memory_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped[User] = relationship("User", back_populates="memory_chunks")

    source_type: Mapped[MemorySourceType] = mapped_column(SqlAlchemyEnum(MemorySourceType), nullable=True)
    source_id: Mapped[int] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), onupdate=func.now(), server_default=func.now()
    )
