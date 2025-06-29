from datetime import datetime
from enum import Enum

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.db import Base
from app.models.User import User


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    MEMORY = "memory"


class PreservedBy(str, Enum):
    MANUAL = "manual"
    MODE = "mode"
    SUGGESTED = "suggested"


class AnswerGeneratedBy(str, Enum):
    LLM = "llm"
    WEB_SEARCH = "web_search"
    TOOL = "tool"
    MEMORY = "memory"
    USER_INPUT = "user_input"


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    role: Mapped[ChatRole] = mapped_column(
        SqlAlchemyEnum(ChatRole, name="chat_message_role", native_enum=True), nullable=False
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    answer_generated_by: Mapped[AnswerGeneratedBy] = mapped_column(
        SqlAlchemyEnum(AnswerGeneratedBy, name="answer_generated_by", native_enum=True), nullable=True
    )
    langgraph_thread_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    preserved: Mapped[bool] = mapped_column(Boolean, default=False)
    preserved_by: Mapped[PreservedBy] = mapped_column(
        SqlAlchemyEnum(PreservedBy, name="chat_message_preserved_by", native_enum=True), nullable=True
    )

    user: Mapped[User] = relationship("User", back_populates="chat_messages")

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"ChatMessage(id={self.id}, user_id={self.user_id}, role={self.role}, "
            f"content={self.content}, langgraph_thread_id={self.langgraph_thread_id}, "
            f"preserved={self.preserved}, preserved_by={self.preserved_by}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )
