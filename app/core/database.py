from contextlib import asynccontextmanager
import logging
import asyncpg
from neo4j import AsyncGraphDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)

pool = None
neo4j_driver = None


async def init_pg():
    global pool
    try:
        pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            min_size=5,
            max_size=20,
        )
        logger.info("Kết nối Postgres thành công!")
    except Exception as e:
        logger.exception(f"LỖI KẾT NỐI POSTGRES: {e}")
        raise


async def close_pg():
    global pool
    if pool:
        await pool.close()
        pool = None


async def init_neo4j():
    global neo4j_driver
    try:
        neo4j_driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        await neo4j_driver.verify_connectivity()
        logger.info("Kết nối Neo4j thành công!")
    except Exception as e:
        logger.exception(f"LỖI KẾT NỐI NEO4J: {e}")
        # Không raise để app vẫn chạy được các API PostgreSQL khi Neo4j lỗi.
        neo4j_driver = None


async def close_neo4j():
    global neo4j_driver
    if neo4j_driver:
        await neo4j_driver.close()
        neo4j_driver = None


async def get_pg_pool():
    if pool is None:
        raise RuntimeError("PostgreSQL pool is not initialized")
    return pool


async def get_neo4j_driver():
    if neo4j_driver is None:
        raise RuntimeError("Neo4j driver is not initialized")
    return neo4j_driver


@asynccontextmanager
async def lifespan(app):
    await init_pg()
    await init_neo4j()
    try:
        yield
    finally:
        await close_neo4j()
        await close_pg()
