from typing import Any, Dict, Iterable, Optional

from app.core.database import get_pg_pool, get_neo4j_driver


def row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row)


def pick(row: Dict[str, Any], candidates: Iterable[str], default: Any = None) -> Any:
    """
    Lấy giá trị theo nhiều tên cột khác nhau để tránh lệch schema.
    Ví dụ: id có thể là class_id hoặc id.
    """
    for key in candidates:
        if key in row and row[key] is not None:
            return row[key]
    return default


async def fetch_all(pool, table_name: str):
    """
    Fetch toàn bộ dữ liệu từ một bảng PostgreSQL.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(f'SELECT * FROM "{table_name}"')
    return [row_to_dict(row) for row in rows]


async def create_constraints(session):
    """
    Tạo constraint unique id cho các node chính.
    Dùng IF NOT EXISTS nên chạy nhiều lần không sao.
    """
    constraints = [
        "CREATE CONSTRAINT class_id IF NOT EXISTS FOR (n:Class) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT subject_id IF NOT EXISTS FOR (n:Subject) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT topic_id IF NOT EXISTS FOR (n:Topic) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT lesson_id IF NOT EXISTS FOR (n:Lesson) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (n:Chunk) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT keyword_id IF NOT EXISTS FOR (n:Keyword) REQUIRE n.id IS UNIQUE",
    ]

    for cypher in constraints:
        await session.run(cypher)


async def sync_classes(session, classes):
    for row in classes:
        node_id = pick(row, ["class_id", "id"])
        name = pick(row, ["class_name", "name", "title"], node_id)
        minio_url = pick(row, ["minio_url", "file_url", "url"])

        if not node_id:
            continue

        await session.run(
            """
            MERGE (c:Class {id: $id})
            SET c.name = $name,
                c.minio_url = $minio_url
            """,
            id=node_id,
            name=name,
            minio_url=minio_url,
        )


async def sync_subjects(session, subjects):
    for row in subjects:
        node_id = pick(row, ["subject_id", "id"])
        name = pick(row, ["subject_name", "name", "title"], node_id)
        class_id = pick(row, ["class_id"])
        minio_url = pick(row, ["minio_url", "file_url", "url"])

        if not node_id:
            continue

        await session.run(
            """
            MERGE (s:Subject {id: $id})
            SET s.name = $name,
                s.class_id = $class_id,
                s.minio_url = $minio_url
            """,
            id=node_id,
            name=name,
            class_id=class_id,
            minio_url=minio_url,
        )

        if class_id:
            await session.run(
                """
                MATCH (c:Class {id: $class_id})
                MATCH (s:Subject {id: $subject_id})
                MERGE (c)-[:HAS_SUBJECT]->(s)
                """,
                class_id=class_id,
                subject_id=node_id,
            )


async def sync_topics(session, topics):
    for row in topics:
        node_id = pick(row, ["topic_id", "id"])
        name = pick(row, ["topic_name", "name", "title"], node_id)
        subject_id = pick(row, ["subject_id"])
        topic_num = pick(row, ["topic_num", "num", "order"])
        description = pick(row, ["topic_des", "description", "des"])
        minio_url = pick(row, ["minio_url", "file_url", "url"])

        if not node_id:
            continue

        await session.run(
            """
            MERGE (t:Topic {id: $id})
            SET t.name = $name,
                t.subject_id = $subject_id,
                t.topic_num = $topic_num,
                t.description = $description,
                t.minio_url = $minio_url
            """,
            id=node_id,
            name=name,
            subject_id=subject_id,
            topic_num=topic_num,
            description=description,
            minio_url=minio_url,
        )

        if subject_id:
            await session.run(
                """
                MATCH (s:Subject {id: $subject_id})
                MATCH (t:Topic {id: $topic_id})
                MERGE (s)-[:HAS_TOPIC]->(t)
                """,
                subject_id=subject_id,
                topic_id=node_id,
            )


async def sync_lessons(session, lessons):
    for row in lessons:
        node_id = pick(row, ["lesson_id", "id"])
        name = pick(row, ["lesson_name", "name", "title"], node_id)
        topic_id = pick(row, ["topic_id"])
        lesson_num = pick(row, ["lesson_num", "num", "order"])
        lesson_type = pick(row, ["lesson_type", "type"])
        description = pick(row, ["lesson_des", "description", "des"])
        minio_url = pick(row, ["minio_url", "file_url", "url"])

        if not node_id:
            continue

        await session.run(
            """
            MERGE (l:Lesson {id: $id})
            SET l.name = $name,
                l.topic_id = $topic_id,
                l.lesson_num = $lesson_num,
                l.lesson_type = $lesson_type,
                l.description = $description,
                l.minio_url = $minio_url
            """,
            id=node_id,
            name=name,
            topic_id=topic_id,
            lesson_num=lesson_num,
            lesson_type=lesson_type,
            description=description,
            minio_url=minio_url,
        )

        if topic_id:
            await session.run(
                """
                MATCH (t:Topic {id: $topic_id})
                MATCH (l:Lesson {id: $lesson_id})
                MERGE (t)-[:HAS_LESSON]->(l)
                """,
                topic_id=topic_id,
                lesson_id=node_id,
            )


async def sync_chunks(session, chunks):
    for row in chunks:
        node_id = pick(row, ["chunk_id", "id"])
        lesson_id = pick(row, ["lesson_id"])
        content = pick(row, ["content", "chunk_content", "text"], "")
        chunk_index = pick(row, ["chunk_index", "index", "chunk_num", "num"])
        minio_url = pick(row, ["minio_url", "file_url", "url"])

        if not node_id:
            continue

        await session.run(
            """
            MERGE (ch:Chunk {id: $id})
            SET ch.lesson_id = $lesson_id,
                ch.content = $content,
                ch.chunk_index = $chunk_index,
                ch.minio_url = $minio_url
            """,
            id=node_id,
            lesson_id=lesson_id,
            content=content,
            chunk_index=chunk_index,
            minio_url=minio_url,
        )

        if lesson_id:
            await session.run(
                """
                MATCH (l:Lesson {id: $lesson_id})
                MATCH (ch:Chunk {id: $chunk_id})
                MERGE (l)-[:HAS_CHUNK]->(ch)
                """,
                lesson_id=lesson_id,
                chunk_id=node_id,
            )


async def sync_keywords(session, keywords):
    for row in keywords:
        node_id = pick(row, ["keyword_id", "id"])
        name = pick(row, ["keyword_name", "name"], node_id)

        if not node_id:
            continue

        await session.run(
            """
            MERGE (k:Keyword {id: $id})
            SET k.name = $name
            """,
            id=node_id,
            name=name,
        )


async def sync_chunk_keywords(session, chunk_keywords):
    for row in chunk_keywords:
        chunk_id = pick(row, ["chunk_id"])
        keyword_id = pick(row, ["keyword_id"])

        if not chunk_id or not keyword_id:
            continue

        await session.run(
            """
            MATCH (ch:Chunk {id: $chunk_id})
            MATCH (k:Keyword {id: $keyword_id})
            MERGE (ch)-[:HAS_KEYWORD]->(k)
            """,
            chunk_id=chunk_id,
            keyword_id=keyword_id,
        )


async def sync_all():
    """
    Đồng bộ dữ liệu từ PostgreSQL sang Neo4j.
    API /api/sync/neo4j sẽ gọi hàm này.
    """
    pg_pool = await get_pg_pool()
    neo4j_driver = await get_neo4j_driver()
    classes = await fetch_all(pg_pool, "class")
    subjects = await fetch_all(pg_pool, "subject")
    topics = await fetch_all(pg_pool, "topic")
    lessons = await fetch_all(pg_pool, "lesson")
    chunks = await fetch_all(pg_pool, "chunk")
    keywords = await fetch_all(pg_pool, "keyword")
    chunk_keywords = await fetch_all(pg_pool, "chunk_keyword")

    async with neo4j_driver.session() as session:
        await create_constraints(session)

        # Node test để kiểm tra Neo4j kết nối được
        await session.run(
            """
            MERGE (t:Thing {id: 'thing'})
            ON CREATE SET t.name = 'Thing'
            """
        )

        await sync_classes(session, classes)
        await sync_subjects(session, subjects)
        await sync_topics(session, topics)
        await sync_lessons(session, lessons)
        await sync_chunks(session, chunks)
        await sync_keywords(session, keywords)
        await sync_chunk_keywords(session, chunk_keywords)

    return {
        "message": "Synced PostgreSQL to Neo4j successfully",
        "counts": {
            "classes": len(classes),
            "subjects": len(subjects),
            "topics": len(topics),
            "lessons": len(lessons),
            "chunks": len(chunks),
            "keywords": len(keywords),
            "chunk_keywords": len(chunk_keywords),
        },
    }