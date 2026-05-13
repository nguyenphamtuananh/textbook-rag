from fastapi import APIRouter, HTTPException, Depends
from asyncpg import Pool
from app.core import database
from app.models.schemas import LessonCreate, LessonResponse
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lesson", tags=["Lesson"])

# Khớp schema Database/postgres/02_schema.sql (không có created_at/updated_at trên bảng)
_LESSON_COLUMNS = """
    lesson_id, topic_id, lesson_num, lesson_name, lesson_type, lesson_des, minio_url, mongo_id
"""

async def get_pool() -> Pool:
    if database.pool is None:
        raise HTTPException(status_code=503, detail="Database not ready")
    return database.pool

@router.post("/", response_model=LessonResponse, status_code=201)
async def create_lesson(l: LessonCreate, db: Pool = Depends(get_pool)):
    row = await db.fetchrow("""
        INSERT INTO lesson (lesson_num, lesson_name, lesson_type, lesson_des, topic_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING lesson_id, lesson_num, lesson_name, lesson_type, lesson_des, topic_id, minio_url, mongo_id
    """, l.lesson_num, l.lesson_name, l.lesson_type, l.lesson_des, l.topic_id)
    return LessonResponse(**dict(row))

# List phải khai báo TRƯỚC /{lesson_id} để không bị coi "lesson_id" rỗng / nhầm path
@router.get("", response_model=List[LessonResponse])
@router.get("/", response_model=List[LessonResponse])
async def list_lessons(db: Pool = Depends(get_pool)):
    try:
        rows = await db.fetch(
            f"SELECT {_LESSON_COLUMNS} FROM lesson ORDER BY topic_id, lesson_num"
        )
        return [LessonResponse(**dict(r)) for r in rows]
    except Exception as e:
        logger.exception("GET /api/lesson list failed (DB hoặc validation)")
        raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách bài học: {str(e)}")

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: str, db: Pool = Depends(get_pool)):
    row = await db.fetchrow(
        f"SELECT {_LESSON_COLUMNS} FROM lesson WHERE lesson_id = $1",
        lesson_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonResponse(**dict(row))

@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(lesson_id: str, l: LessonCreate, db: Pool = Depends(get_pool)):
    row = await db.fetchrow("""
        UPDATE lesson SET lesson_num=$1, lesson_name=$2, lesson_type=$3, lesson_des=$4, topic_id=$5
        WHERE lesson_id=$6 RETURNING *
    """, l.lesson_num, l.lesson_name, l.lesson_type, l.lesson_des, l.topic_id, lesson_id)
    if not row:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonResponse(**dict(row))

@router.delete("/{lesson_id}")
async def delete_lesson(lesson_id: str, db: Pool = Depends(get_pool)):
    await db.execute("DELETE FROM lesson WHERE lesson_id=$1", lesson_id)
    return {"detail": "Lesson deleted"}