from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger.app_logger import log
from app.api.v1.schemas.search_schema import SearchQuerySchema, SearchResultSchema
from app.core.database.db import get_db
from app.dependencies.auth import get_current_user
from app.services.search.embedding_search import search_embeddings
from app.models.User import User
from app.ginarr.ginarr_errors import GinarrGraphCompilationError
from app.models.MemoryChunk import MemoryChunk

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/")
async def search_chunks(
    payload: SearchQuerySchema, db_session: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
) -> list[SearchResultSchema]:
    try:
        search_results: list[MemoryChunk] = await search_embeddings(
            db_session=db_session,
            user_id=user.id,
            query=payload.query,
            embedding_types=payload.content_types,
            from_date=payload.from_date[0] if payload.from_date else None,
            to_date=payload.to_date[0] if payload.to_date else None,
        )
    except GinarrGraphCompilationError as e:
        log.error(f"Error compiling Ginarr graph: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        log.error(f"Error searching embeddings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return [SearchResultSchema.model_validate(chunk) for chunk in search_results]
