import asyncpg
from app.core.config import settings

async def get_pg_pool():
    pool = await asyncpg.create_pool(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        min_size=5,
        max_size=20
    )
    return pool

# Singleton pool
pg_pool: asyncpg.Pool = None

async def init_pg():
    global pg_pool
    pg_pool = await get_pg_pool()

async def close_pg():
    global pg_pool
    if pg_pool:
        await pg_pool.close()