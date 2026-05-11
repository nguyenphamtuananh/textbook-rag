from fastapi import APIRouter, HTTPException, Depends
from asyncpg import Pool
from app.core.database import pg_pool
from app.models.schemas import TopicCreate, TopicResponse
from typing import List

router = APIRouter(prefix="/topic", tags=["Topic"])

async def get_pool():
    return pg_pool

@router.post("/", response_model=TopicResponse, status_code=201)
async def create_topic(t: TopicCreate, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("""
        INSERT INTO topic (topic_num, topic_name, subject_id)
        VALUES ($1, $2, $3)
        RETURNING topic_id, topic_num, topic_name, subject_id, minio_url, mongo_id
    """, t.topic_num, t.topic_name, t.subject_id)
    return TopicResponse(**dict(row))

@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: str, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("SELECT * FROM topic WHERE topic_id = $1", topic_id)
    if not row:
        raise HTTPException(status_code=404, detail="Topic not found")
    return TopicResponse(**dict(row))

@router.get("/", response_model=List[TopicResponse])
async def list_topics(pool: Pool = Depends(get_pool)):
    rows = await pool.fetch("SELECT * FROM topic")
    return [TopicResponse(**dict(r)) for r in rows]

@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(topic_id: str, t: TopicCreate, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("""
        UPDATE topic SET topic_num=$1, topic_name=$2, subject_id=$3
        WHERE topic_id=$4 RETURNING *
    """, t.topic_num, t.topic_name, t.subject_id, topic_id)
    if not row:
        raise HTTPException(status_code=404, detail="Topic not found")
    return TopicResponse(**dict(row))

@router.delete("/{topic_id}")
async def delete_topic(topic_id: str, pool: Pool = Depends(get_pool)):
    await pool.execute("DELETE FROM topic WHERE topic_id=$1", topic_id)
    return {"detail": "Topic deleted"}