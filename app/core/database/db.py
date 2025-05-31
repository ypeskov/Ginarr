from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config.settings import settings as s

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{s.DB_USER}:{s.DB_PASSWORD}@{s.DB_HOST}:{s.DB_PORT}/{s.DB_NAME}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)

SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():  # pragma: no cover
    async with SessionLocal() as db:
        yield db
