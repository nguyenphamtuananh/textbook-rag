from fastapi import APIRouter, HTTPException, Depends
from asyncpg import Pool
from app.core.database import pg_pool
from app.models.schemas import LessonCreate, LessonResponse
from typing import List

router = APIRouter(prefix="/lesson", tags=["Lesson"])

async def get_pool():
    return pg_pool

@router.post("/", response_model=LessonResponse, status_code=201)
async def create_lesson(l: LessonCreate, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("""
        INSERT INTO lesson (lesson_num, lesson_name, lesson_type, lesson_des, topic_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING lesson_id, lesson_num, lesson_name, lesson_type, lesson_des, topic_id, minio_url, mongo_id
    """, l.lesson_num, l.lesson_name, l.lesson_type, l.lesson_des, l.topic_id)
    return LessonResponse(**dict(row))

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: str, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("SELECT * FROM lesson WHERE lesson_id=$1", lesson_id)
    if not row:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonResponse(**dict(row))

@router.get("/", response_model=List[LessonResponse])
async def list_lessons(pool: Pool = Depends(get_pool)):
    rows = await pool.fetch("SELECT * FROM lesson")
    return [LessonResponse(**dict(r)) for r in rows]

@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(lesson_id: str, l: LessonCreate, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("""
        UPDATE lesson SET lesson_num=$1, lesson_name=$2, lesson_type=$3, lesson_des=$4, topic_id=$5
        WHERE lesson_id=$6 RETURNING *
    """, l.lesson_num, l.lesson_name, l.lesson_type, l.lesson_des, l.topic_id, lesson_id)
    if not row:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonResponse(**dict(row))

@router.delete("/{lesson_id}")
async def delete_lesson(lesson_id: str, pool: Pool = Depends(get_pool)):
    await pool.execute("DELETE FROM lesson WHERE lesson_id=$1", lesson_id)
    return {"detail": "Lesson deleted"}