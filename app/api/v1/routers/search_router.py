from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.search_schema import SearchQuery
from app.core.database.db import get_db
from app.dependencies.auth import get_current_user
from app.services.search.embedding_search import search_embeddings

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/")
async def search_chunks(
    payload: SearchQuery, db_session: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    return await search_embeddings(
        db_session=db_session,
        user_id=user.id,
        query=payload.query,
        embedding_types=payload.content_types,
        from_date=payload.from_date[0] if payload.from_date else None,
        to_date=payload.to_date[0] if payload.to_date else None,
    )
