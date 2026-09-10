from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.search import SearchQuery, SearchResponse
from app.services.search import HybridSearchService

router = APIRouter()


@router.post("", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def search_post(
    payload: SearchQuery,
    db: AsyncSession = Depends(get_db),
):
    """
    Hybrid Search (POST): Search notes, formulas, circuits, PYQs, and AI conversations.
    """
    service = HybridSearchService(db)
    return await service.search(payload)


@router.get("", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def search_get(
    q: str = Query(...),
    category: str = Query("all"),
    subject_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Hybrid Search (GET query parameter mode).
    """
    query_obj = SearchQuery(query=q, category=category, subject_id=subject_id)
    service = HybridSearchService(db)
    return await service.search(query_obj)
