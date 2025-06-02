from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.settings import settings
from app.core.logger.app_logger import log
from app.core.database.db import get_db
from app.models.User import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get the current user from the database.
    Args:
        token: Annotated[str, Depends(oauth2_scheme)] - The JWT token.
        db: Annotated[AsyncSession, Depends(get_db)] - The database session.
    Returns:
        User: The current user.
    Raises:
        HTTPException: 401 - Unauthorized.
        JWTError: If the JWT token is invalid.
        SQLAlchemyError: If the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError as e:
        log.error(f"JWTError: {e}")
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user
