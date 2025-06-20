from pathlib import Path
import sys
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

# add app/ to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.core.logger.app_logger import log  # noqa: E402
from app.core.database.db import SessionLocal  # noqa: E402
from manage_env.model_seeders.embedding_type_seeder import seed_embedding_types  # noqa: E402


async def main() -> None:
    db_session: AsyncSession = SessionLocal()
    log.info("🌱 Starting database seeding...")
    log.info("--------------------------------")

    await seed_embedding_types(db_session=db_session)

    log.info("--------------------------------")
    log.info("✅ Database seeding completed")


if __name__ == "__main__":
    asyncio.run(main())
