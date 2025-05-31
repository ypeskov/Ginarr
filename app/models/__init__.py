from app.models.User import User
from app.models.MemoryChunk import MemoryChunk
from sqlalchemy.orm import relationship

# add relationship to User model
User.memory_chunks = relationship(MemoryChunk, back_populates="user")
