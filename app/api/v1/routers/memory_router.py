from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from icecream import ic

from app.api.v1.schemas.memory_schema import MemoryCreate, MemoryOut
from app.core.database.db import get_db
from app.core.logger.app_logger import log
from app.dependencies.auth import get_current_user
from app.models.User import User
from app.services.memory.memory_errors import MemoryAddError
from app.services.memory.memory_service import store_memory

ic.configureOutput(includeContext=True)

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/", response_model=MemoryOut, status_code=status.HTTP_201_CREATED)
async def store_memory_endpoint(
    memory_in: MemoryCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MemoryOut:
    log.info(f"Storing memory chunk for user [{user.id}] with content [{memory_in.content[:100]}...]")
    try:
        return await store_memory(db, user_id=user.id, content=memory_in.content)
    except MemoryAddError as e:
        log.error(f"Error storing memory for user [{user.id}]: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        log.error(f"Error storing memory for user [{user.id}]: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
