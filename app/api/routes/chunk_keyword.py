from fastapi import APIRouter, HTTPException, Depends
from asyncpg import Pool
from app.core.database import pg_pool
from app.models.schemas import ChunkKeywordLink, ChunkKeywordResponse
from typing import List

router = APIRouter(prefix="/chunk-keyword", tags=["Chunk-Keyword"])

async def get_pool():
    return pg_pool

@router.post("/", response_model=ChunkKeywordResponse, status_code=201)
async def link_chunk_keyword(link: ChunkKeywordLink, pool: Pool = Depends(get_pool)):
    query = """
        INSERT INTO chunk_keyword (chunk_id, keyword_id, mongo_id)
        VALUES ($1, $2, $3)
        RETURNING chunk_id, keyword_id, mongo_id
    """
    try:
        row = await pool.fetchrow(query, link.chunk_id, link.keyword_id, link.mongo_id)
        return ChunkKeywordResponse(**dict(row))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{chunk_id}/{keyword_id}", response_model=ChunkKeywordResponse)
async def get_link(chunk_id: str, keyword_id: str, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow(
        "SELECT * FROM chunk_keyword WHERE chunk_id = $1 AND keyword_id = $2",
        chunk_id, keyword_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Link not found")
    return ChunkKeywordResponse(**dict(row))

@router.delete("/{chunk_id}/{keyword_id}", response_model=dict)
async def unlink(chunk_id: str, keyword_id: str, pool: Pool = Depends(get_pool)):
    await pool.execute("DELETE FROM chunk_keyword WHERE chunk_id = $1 AND keyword_id = $2", chunk_id, keyword_id)
    return {"detail": "Link removed"}