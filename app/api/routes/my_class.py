from fastapi import APIRouter, HTTPException, Depends
from asyncpg import Pool
from app.core.database import pg_pool
from app.models.schemas import ClassCreate, ClassResponse
from typing import List

router = APIRouter(prefix="/class", tags=["Class"])

async def get_pool() -> Pool:
    return pg_pool

@router.post("/", response_model=ClassResponse, status_code=201)
async def create_class(cls: ClassCreate, pool: Pool = Depends(get_pool)):
    query = """
        INSERT INTO "class" (class_name, minio_url, mongo_id)
        VALUES ($1, NULL, $2)
        RETURNING class_id, class_name, minio_url, mongo_id
    """
    row = await pool.fetchrow(query, cls.class_name, cls.mongo_id)
    return ClassResponse(**dict(row))

@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(class_id: str, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow('SELECT * FROM "class" WHERE class_id = $1', class_id)
    if not row:
        raise HTTPException(status_code=404, detail="Class not found")
    return ClassResponse(**dict(row))

@router.get("/", response_model=List[ClassResponse])
async def list_classes(pool: Pool = Depends(get_pool)):
    rows = await pool.fetch('SELECT * FROM "class"')
    return [ClassResponse(**dict(r)) for r in rows]

@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(class_id: str, cls: ClassCreate, pool: Pool = Depends(get_pool)):
    row = await pool.fetchrow(
        'UPDATE "class" SET class_name = $1, mongo_id = $2 WHERE class_id = $3 RETURNING *',
        cls.class_name, cls.mongo_id, class_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Class not found")
    return ClassResponse(**dict(row))

@router.delete("/{class_id}", response_model=dict)
async def delete_class(class_id: str, pool: Pool = Depends(get_pool)):
    await pool.execute('DELETE FROM "class" WHERE class_id = $1', class_id)
    return {"detail": "Class deleted"}