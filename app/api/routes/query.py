from typing import Optional, List, Dict, Any
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import answer_query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["AI Query"])


class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Câu hỏi của người dùng")
    category: Optional[str] = Field(None, description="class, subject, topic, lesson, chunk, keyword, all")
    tag: Optional[str] = Field(None, description="Lọc theo keyword/tag")
    top_k: int = Field(8, ge=1, le=20, description="Số context lấy từ PG/KG")
    timeout_seconds: int = Field(30, ge=5, le=120, description="Timeout gọi AI")


class QueryResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    context_count: int
    model: Optional[str] = None
    finish_reason: Optional[str] = None


@router.post("", response_model=QueryResponse)
async def query_ai(request: QueryRequest):
    try:
        result = await answer_query(
            question=request.prompt,
            category=request.category,
            tag=request.tag,
            top_k=request.top_k,
            timeout_seconds=request.timeout_seconds,
        )
        return QueryResponse(**result)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("/api/query failed: %s", e)
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(e)}")
