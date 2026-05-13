from fastapi import APIRouter, HTTPException, Depends
from asyncpg import Pool
from app.core import database
from app.models.schemas import KeywordCreate, KeywordResponse
from typing import List

router = APIRouter(prefix="/keyword", tags=["Keyword"])

async def get_pool() -> Pool:
    return database.pool

@router.post("/", response_model=KeywordResponse, status_code=201)
async def create_keyword(kw: KeywordCreate, pool: Pool = Depends(get_pool)):
    query = """
        INSERT INTO keyword (keyword_name, keyword_slug, mongo_id)
        VALUES ($1, $2, $3)
        RETURNING keyword_id, keyword_name, keyword_slug, mongo_id
    """
    # Nếu slug không được cung cấp, để trigger tự tạo; ta truyền None
    row = await pool.fetchrow(query, kw.keyword_name, kw.keyword_slug, kw.mongo_id)
    return KeywordResponse(**dict(row))

@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(keyword_id: str, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("SELECT * FROM keyword WHERE keyword_id = $1", keyword_id)
    if not row:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return KeywordResponse(**dict(row))

@router.get("/", response_model=List[KeywordResponse])
async def list_keywords(pool: Pool = Depends(get_pool)):
    rows = await pool.fetch("SELECT * FROM keyword")
    return [KeywordResponse(**dict(r)) for r in rows]

@router.delete("/{keyword_id}", response_model=dict)
async def delete_keyword(keyword_id: str, pool: Pool = Depends(get_pool)):
    await pool.execute("DELETE FROM keyword WHERE keyword_id = $1", keyword_id)
    return {"detail": "Keyword deleted"}