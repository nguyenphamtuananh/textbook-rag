from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_pg_pool

router = APIRouter(prefix="/chunk-keyword", tags=["Chunk-Keyword"])


class ChunkKeywordCreate(BaseModel):
    chunk_id: str
    keyword_id: str
    mongo_id: Optional[str] = None


@router.post("/")
async def link_chunk_keyword(data: ChunkKeywordCreate):
    pool = await get_pg_pool()

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO chunk_keyword (chunk_id, keyword_id, mongo_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (chunk_id, keyword_id)
                DO UPDATE SET mongo_id = EXCLUDED.mongo_id
                RETURNING chunk_id, keyword_id, mongo_id
                """,
                data.chunk_id,
                data.keyword_id,
                data.mongo_id
            )

        return {
            "message": "Chunk-keyword link created or already existed",
            "data": dict(row)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_all_chunk_keywords(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    offset = (page - 1) * size
    pool = await get_pg_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT 
                ck.chunk_id,
                ck.keyword_id,
                ck.mongo_id,
                c.content AS chunk_content,
                k.name AS keyword_name
            FROM chunk_keyword ck
            LEFT JOIN chunk c ON ck.chunk_id = c.id
            LEFT JOIN keyword k ON ck.keyword_id = k.id
            ORDER BY ck.chunk_id, ck.keyword_id
            LIMIT $1 OFFSET $2
            """,
            size,
            offset
        )

        total = await conn.fetchval(
            """
            SELECT COUNT(*) FROM chunk_keyword
            """
        )

    return {
        "page": page,
        "size": size,
        "total": total,
        "items": [dict(row) for row in rows]
    }


@router.get("/{chunk_id}/{keyword_id}")
async def get_chunk_keyword(chunk_id: str, keyword_id: str):
    pool = await get_pg_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT 
                ck.chunk_id,
                ck.keyword_id,
                ck.mongo_id,
                c.content AS chunk_content,
                k.name AS keyword_name
            FROM chunk_keyword ck
            LEFT JOIN chunk c ON ck.chunk_id = c.id
            LEFT JOIN keyword k ON ck.keyword_id = k.id
            WHERE ck.chunk_id = $1 AND ck.keyword_id = $2
            """,
            chunk_id,
            keyword_id
        )

    if not row:
        raise HTTPException(status_code=404, detail="Chunk-keyword link not found")

    return dict(row)


@router.delete("/{chunk_id}/{keyword_id}")
async def unlink_chunk_keyword(chunk_id: str, keyword_id: str):
    pool = await get_pg_pool()

    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            DELETE FROM chunk_keyword
            WHERE chunk_id = $1 AND keyword_id = $2
            """,
            chunk_id,
            keyword_id
        )

    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Chunk-keyword link not found")

    return {
        "message": "Chunk-keyword link deleted successfully",
        "chunk_id": chunk_id,
        "keyword_id": keyword_id
    }