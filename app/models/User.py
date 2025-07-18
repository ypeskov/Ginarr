from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.db import Base

if TYPE_CHECKING:
    from app.models.ChatMessage import ChatMessage


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    chat_messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="user")

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now, server_default=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, email={self.email}, first_name={self.first_name}, "
            f"last_name={self.last_name}, is_active={self.is_active}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )


from app.models.ChatMessage import ChatMessage  # noqa: E402
from app.models.MemoryChunk import MemoryChunk  # noqa: E402

User.chat_messages = relationship(ChatMessage, back_populates="user")
User.memory_chunks = relationship(MemoryChunk, back_populates="user")
