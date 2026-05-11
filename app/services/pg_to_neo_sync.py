import asyncio
from asyncpg import create_pool
from neo4j import AsyncGraphDatabase
from app.core.config import settings
from datetime import datetime

async def sync_all():
    pg_pool = await create_pool(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        min_size=2,
        max_size=5
    )
    neo4j_driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )

    async with neo4j_driver.session() as session:
        # 1. Node gốc
        await session.run("MERGE (:Thing {id: 'thing'}) ON CREATE SET name = 'Thing'")

        # 2. Classes
        classes = await pg_pool.fetch('SELECT class_id, class_name, minio_url FROM "class"')
        for c in classes:
            await session.run("""
                MERGE (c:Class {class_id: $cid})
                ON CREATE SET c.class_name = $name, c.minio_url = $url, c.updated_at = $now
                ON MATCH SET c.class_name = $name, c.minio_url = $url, c.updated_at = $now
                WITH c
                MATCH (t:Thing {id: 'thing'})
                MERGE (t)-[:HAS_CLASS]->(c)
            """, cid=c['class_id'], name=c['class_name'], url=c['minio_url'], now=datetime.utcnow())

        # 3. Subjects
        subjects = await pg_pool.fetch('SELECT subject_id, subject_name, minio_url, class_id FROM subject')
        for s in subjects:
            await session.run("""
                MERGE (s:Subject {subject_id: $sid})
                ON CREATE SET s.subject_name = $name, s.minio_url = $url, s.updated_at = $now
                ON MATCH SET s.subject_name = $name, s.minio_url = $url, s.updated_at = $now
                WITH s
                MATCH (c:Class {class_id: $cid})
                MERGE (c)-[:HAS_SUBJECT]->(s)
            """, sid=s['subject_id'], name=s['subject_name'], url=s['minio_url'],
                cid=s['class_id'], now=datetime.utcnow())

        # 4. Topics
        topics = await pg_pool.fetch('SELECT topic_id, topic_name, topic_num, minio_url, subject_id FROM topic')
        for t in topics:
            await session.run("""
                MERGE (t:Topic {topic_id: $tid})
                ON CREATE SET t.topic_name = $name, t.topic_num = $num, t.minio_url = $url, t.updated_at = $now
                ON MATCH SET t.topic_name = $name, t.topic_num = $num, t.minio_url = $url, t.updated_at = $now
                WITH t
                MATCH (s:Subject {subject_id: $sid})
                MERGE (s)-[:HAS_TOPIC]->(t)
            """, tid=t['topic_id'], name=t['topic_name'], num=t['topic_num'],
                url=t['minio_url'], sid=t['subject_id'], now=datetime.utcnow())

        # 5. Lessons
        lessons = await pg_pool.fetch('SELECT lesson_id, lesson_name, lesson_num, minio_url, topic_id FROM lesson')
        for l in lessons:
            await session.run("""
                MERGE (l:Lesson {lesson_id: $lid})
                ON CREATE SET l.lesson_name = $name, l.lesson_num = $num, l.minio_url = $url, l.updated_at = $now
                ON MATCH SET l.lesson_name = $name, l.lesson_num = $num, l.minio_url = $url, l.updated_at = $now
                WITH l
                MATCH (t:Topic {topic_id: $tid})
                MERGE (t)-[:HAS_LESSON]->(l)
            """, lid=l['lesson_id'], name=l['lesson_name'], num=l['lesson_num'],
                url=l['minio_url'], tid=l['topic_id'], now=datetime.utcnow())

        # 6. Chunks
        chunks = await pg_pool.fetch('SELECT chunk_id, chunk_name, chunk_num, minio_url, lesson_id FROM chunk')
        for ch in chunks:
            await session.run("""
                MERGE (c:Chunk {chunk_id: $cid})
                ON CREATE SET c.chunk_name = $name, c.chunk_num = $num, c.minio_url = $url, c.updated_at = $now
                ON MATCH SET c.chunk_name = $name, c.chunk_num = $num, c.minio_url = $url, c.updated_at = $now
                WITH c
                MATCH (l:Lesson {lesson_id: $lid})
                MERGE (l)-[:HAS_CHUNK]->(c)
            """, cid=ch['chunk_id'], name=ch['chunk_name'], num=ch['chunk_num'],
                url=ch['minio_url'], lid=ch['lesson_id'], now=datetime.utcnow())

        # 7. Keywords (from chunk_keyword + keyword tables)
        keywords = await pg_pool.fetch("""
            SELECT ck.chunk_id, k.keyword_name
            FROM chunk_keyword ck JOIN keyword k ON ck.keyword_id = k.keyword_id
        """)
        for kw in keywords:
            key = f"{kw['chunk_id']}::{kw['keyword_name']}"
            await session.run("""
                MERGE (k:Keyword {keyword_key: $key})
                ON CREATE SET k.keyword_name = $name, k.chunk_id = $chunk_id, k.updated_at = $now
                ON MATCH SET k.keyword_name = $name, k.chunk_id = $chunk_id, k.updated_at = $now
                WITH k
                MATCH (c:Chunk {chunk_id: $chunk_id})
                MERGE (c)-[:HAS_KEYWORD]->(k)
            """, key=key, name=kw['keyword_name'], chunk_id=kw['chunk_id'], now=datetime.utcnow())

        # 8. (Option) Embeddings sẽ sync riêng nếu cần, có thể bỏ qua hiện tại
        print("Neo4j sync completed.")

    await pg_pool.close()
    await neo4j_driver.close()