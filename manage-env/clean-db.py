import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.core.database.db import engine  # noqa: E402
from app.core.logger.app_logger import log  # noqa: E402


async def clean_db():
    log.info("🧹 Cleaning DB...")
    async with engine.connect() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.commit()
    log.info("✅ DB fully wiped and public schema recreated")


if __name__ == "__main__":
    asyncio.run(clean_db())
