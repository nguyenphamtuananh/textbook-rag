from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.search_service import search_entities

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def search(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    category: Optional[str] = Query(None, description="class, subject, topic, lesson, chunk, keyword, all"),
    tag: Optional[str] = Query(None, description="Lọc theo tag/keyword_name"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD hoặc ISO datetime"),
    date_to: Optional[str] = Query(None, description="YYYY-MM-DD hoặc ISO datetime"),
):
    try:
        return await search_entities(
            query=q,
            category=category,
            tag=tag,
            page=page,
            size=size,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
