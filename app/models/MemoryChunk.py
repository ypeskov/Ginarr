from datetime import datetime

from sqlalchemy import ForeignKey, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.db import Base
from app.models.User import User


class MemoryChunk(Base):
    __tablename__ = "memory_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped[User] = relationship("User", back_populates="memory_chunks")

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), onupdate=func.now(), server_default=func.now()
    )
