from fastapi import APIRouter, HTTPException, Depends
from asyncpg import Pool
from app.core import database
from app.models.schemas import SubjectCreate, SubjectResponse
from typing import List

router = APIRouter(prefix="/subject", tags=["Subject"])

async def get_pool() -> Pool:
    return database.pool
@router.post("/", response_model=SubjectResponse, status_code=201)
async def create_subject(sub: SubjectCreate, pool: Pool = Depends(get_pool)):
    query = """
        INSERT INTO subject (subject_name, subject_type, class_id, minio_url, mongo_id)
        VALUES ($1, $2, $3, NULL, $4)
        RETURNING subject_id, subject_name, subject_type, class_id, minio_url, mongo_id
    """
    row = await pool.fetchrow(query, sub.subject_name, sub.subject_type, sub.class_id, sub.mongo_id)
    return SubjectResponse(**dict(row))

@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(subject_id: str, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("SELECT * FROM subject WHERE subject_id = $1", subject_id)
    if not row:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectResponse(**dict(row))

@router.get("/", response_model=List[SubjectResponse])
async def list_subjects(pool: Pool = Depends(get_pool)):
    rows = await pool.fetch("SELECT * FROM subject")
    return [SubjectResponse(**dict(r)) for r in rows]

@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(subject_id: str, sub: SubjectCreate, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow("""
        UPDATE subject SET subject_name = $1, subject_type = $2, class_id = $3, mongo_id = $4
        WHERE subject_id = $5 RETURNING *
    """, sub.subject_name, sub.subject_type, sub.class_id, sub.mongo_id, subject_id)
    if not row:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectResponse(**dict(row))

@router.delete("/{subject_id}", response_model=dict)
async def delete_subject(subject_id: str, pool: Pool = Depends(get_pool)):
    await pool.execute("DELETE FROM subject WHERE subject_id = $1", subject_id)
    return {"detail": "Subject deleted"}