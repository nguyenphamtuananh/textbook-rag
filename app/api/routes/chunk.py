from fastapi import APIRouter, HTTPException, Depends
from asyncpg import Pool
from app.core.database import pg_pool
from app.models.schemas import ChunkCreate, ChunkResponse
from typing import List

router = APIRouter(prefix="/chunk", tags=["Chunk"])

async def get_pool():
    return pg_pool

@router.post("/", response_model=ChunkResponse, status_code=201)
async def create_chunk(c: ChunkCreate, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("""
        INSERT INTO chunk (chunk_num, chunk_name, chunk_des, lesson_id)
        VALUES ($1, $2, $3, $4)
        RETURNING chunk_id, chunk_num, chunk_name, chunk_des, lesson_id, minio_url, mongo_id
    """, c.chunk_num, c.chunk_name, c.chunk_des, c.lesson_id)
    return ChunkResponse(**dict(row))

@router.get("/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(chunk_id: str, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("SELECT * FROM chunk WHERE chunk_id=$1", chunk_id)
    if not row:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return ChunkResponse(**dict(row))

@router.get("/", response_model=List[ChunkResponse])
async def list_chunks(pool: Pool = Depends(get_pool)):
    rows = await pool.fetch("SELECT * FROM chunk")
    return [ChunkResponse(**dict(r)) for r in rows]

@router.put("/{chunk_id}", response_model=ChunkResponse)
async def update_chunk(chunk_id: str, c: ChunkCreate, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("""
        UPDATE chunk SET chunk_num=$1, chunk_name=$2, chunk_des=$3, lesson_id=$4
        WHERE chunk_id=$5 RETURNING *
    """, c.chunk_num, c.chunk_name, c.chunk_des, c.lesson_id, chunk_id)
    if not row:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return ChunkResponse(**dict(row))

@router.delete("/{chunk_id}")
async def delete_chunk(chunk_id: str, pool: Pool = Depends(get_pool)):
    await pool.execute("DELETE FROM chunk WHERE chunk_id=$1", chunk_id)
    return {"detail": "Chunk deleted"}