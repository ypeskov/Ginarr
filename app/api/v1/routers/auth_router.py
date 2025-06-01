from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.auth_schema import UserRegister, UserLogin, ChangePassword
from app.services.auth import auth_service
from app.core.database.db import get_db
from app.services.auth.errors import UserAlreadyExists, InvalidPassword
from app.models.User import User
from app.dependencies.auth import get_current_user
from app.core.logger.app_logger import log

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.register_user(data, db)
    except UserAlreadyExists:
        log.info(f"User already exists: {data.email}")
        raise HTTPException(status_code=409, detail="User already exists")
    return {"email": user.email, "message": "User registered"}


@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.authenticate_user(data, db)
        if not user:
            log.warning(f"Invalid credentials: {data.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = auth_service.create_access_token({"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        log.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during login")


@router.post("/change-password")
async def change_password(
    data: ChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await auth_service.change_password(current_user, data, db)
    except InvalidPassword:
        log.warning(f"Invalid password: {current_user.email}")
        raise HTTPException(status_code=400, detail="Incorrect password")
    except Exception as e:
        log.error(f"Password change error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during password change")
    return {"message": "Password changed successfully"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    log.info(f"Getting current user: {current_user}")
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
    }
