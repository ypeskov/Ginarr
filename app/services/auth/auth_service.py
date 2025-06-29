from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.auth_schema import ChangePassword, UserLogin, UserRegister
from app.config.settings import settings
from app.core.logger.app_logger import log
from app.models.User import User
from app.services.auth.errors import InvalidPassword, UserAlreadyExists

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


async def register_user(data: UserRegister, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar():
        raise UserAlreadyExists("Email already registered")

    user = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(data: UserLogin, db: AsyncSession) -> Optional[User]:
    try:
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(data.password, user.hashed_password):
            return None
    except Exception as e:
        log.error(f"Error authenticating user: {e}")
        return None
    return user


async def change_password(user: User, data: ChangePassword, db: AsyncSession) -> None:
    if not verify_password(data.old_password, user.hashed_password):
        raise InvalidPassword("Incorrect old password")
    user.hashed_password = hash_password(data.new_password)
    db.add(user)
    await db.commit()
