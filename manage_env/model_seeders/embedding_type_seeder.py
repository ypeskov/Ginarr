from pathlib import Path
import sys
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# add app/ to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.core.logger.app_logger import log  # noqa: E402
from app.models.EmbeddingType import EmbeddingType, EmbeddingTypeName  # noqa: E402
from app.core.database.db import SessionLocal  # noqa: E402


async def seed_embedding_types(db_session: AsyncSession) -> None:
    log.info("🌱 Seeding embedding types...")
    for type_name in EmbeddingTypeName:
        exists = await db_session.execute(select(EmbeddingType).where(EmbeddingType.name == type_name))
        if not exists.scalars().first():
            db_session.add(EmbeddingType(name=type_name, description=f"{type_name} content"))
    await db_session.commit()
    log.info("✅ Embedding types seeded")


if __name__ == "__main__":
    db = SessionLocal()
    asyncio.run(seed_embedding_types(db))
