from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config.settings import settings as s
from app.core.logger.app_logger import log

log.info(f"Connecting to database {s.DB_NAME} on {s.DB_HOST}:{s.DB_PORT}")
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{s.DB_USER}:{s.DB_PASSWORD}@{s.DB_HOST}:{s.DB_PORT}/{s.DB_NAME}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)

SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()
log.info("Database connected")


async def get_db():  # pragma: no cover
    async with SessionLocal() as db:
        yield db
