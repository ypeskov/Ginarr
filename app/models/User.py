from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    memory_chunks: Mapped[list["MemoryChunk"]] = relationship("MemoryChunk", back_populates="user")

    def __repr__(self):
        return (
            f"User(id={self.id}, email={self.email}, first_name={self.first_name}, "
            f"last_name={self.last_name}, is_active={self.is_active})"
        )
