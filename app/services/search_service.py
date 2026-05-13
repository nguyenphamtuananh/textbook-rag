from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from app.core import database

VALID_CATEGORIES = {
    "class",
    "subject",
    "topic",
    "lesson",
    "chunk",
    "keyword",
    "all",
    None,
}


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(
            f"Ngày không hợp lệ: {value}. Dùng định dạng YYYY-MM-DD hoặc ISO datetime."
        ) from exc


def _date_filter(
    alias: str,
    start_index: int,
    date_from: Optional[datetime],
    date_to: Optional[datetime],
) -> Tuple[str, List[Any]]:
    clauses: List[str] = []
    params: List[Any] = []
    index = start_index

    if date_from:
        clauses.append(f"{alias}.created_at >= ${index}")
        params.append(date_from)
        index += 1

    if date_to:
        clauses.append(f"{alias}.created_at <= ${index}")
        params.append(date_to)
        index += 1

    if not clauses:
        return "", []

    return " AND " + " AND ".join(clauses), params


async def _search_pg(
    query: str,
    category: Optional[str],
    tag: Optional[str],
    page: int,
    size: int,
    date_from: Optional[datetime],
    date_to: Optional[datetime],
) -> Tuple[List[Dict[str, Any]], int]:
    pool = await database.get_pg_pool()
    offset = (page - 1) * size
    keyword = f"%{query}%"

    async with pool.acquire() as conn:
        base_params: List[Any] = [keyword]

        tag_join = ""
        tag_where = ""

        if tag:
            tag_join = """
                LEFT JOIN chunk_keyword ck_filter ON ck_filter.chunk_id = c.chunk_id
                LEFT JOIN keyword k_filter ON k_filter.keyword_id = ck_filter.keyword_id
            """
            tag_where = f" AND k_filter.keyword_name ILIKE ${len(base_params) + 1}"
            base_params.append(f"%{tag}%")

        selects: List[Tuple[str, List[Any]]] = []

        # CLASS
        if category in (None, "all", "class") and not tag:
            where_date, date_params = _date_filter(
                "c",
                len(base_params) + 1,
                date_from,
                date_to,
            )

            sql = """
                SELECT 
                    c.class_id AS id,
                    c.class_name AS name,
                    'class' AS type,
                    NULL::text AS parent_id,
                    NULL::text AS parent_name,
                    c.minio_url,
                    NULL::text AS description,
                    c.created_at,
                    c.updated_at
                FROM "class" c
                WHERE c.class_name ILIKE $1
            """ + where_date

            selects.append((sql, base_params + date_params))

        # SUBJECT
        if category in (None, "all", "subject") and not tag:
            where_date, date_params = _date_filter(
                "s",
                len(base_params) + 1,
                date_from,
                date_to,
            )

            sql = """
                SELECT 
                    s.subject_id AS id,
                    s.subject_name AS name,
                    'subject' AS type,
                    s.class_id AS parent_id,
                    c.class_name AS parent_name,
                    s.minio_url,
                    s.subject_type AS description,
                    s.created_at,
                    s.updated_at
                FROM subject s
                JOIN "class" c ON s.class_id = c.class_id
                WHERE s.subject_name ILIKE $1
            """ + where_date

            selects.append((sql, base_params + date_params))

        # TOPIC
        if category in (None, "all", "topic") and not tag:
            where_date, date_params = _date_filter(
                "t",
                len(base_params) + 1,
                date_from,
                date_to,
            )

            sql = """
                SELECT 
                    t.topic_id AS id,
                    t.topic_name AS name,
                    'topic' AS type,
                    t.subject_id AS parent_id,
                    s.subject_name AS parent_name,
                    t.minio_url,
                    NULL::text AS description,
                    t.created_at,
                    t.updated_at
                FROM topic t
                JOIN subject s ON t.subject_id = s.subject_id
                WHERE t.topic_name ILIKE $1
            """ + where_date

            selects.append((sql, base_params + date_params))

        # LESSON
        if category in (None, "all", "lesson"):
            where_date, date_params = _date_filter(
                "l",
                len(base_params) + 1,
                date_from,
                date_to,
            )

            if tag:
                sql = """
                    SELECT DISTINCT
                        l.lesson_id AS id,
                        l.lesson_name AS name,
                        'lesson' AS type,
                        l.topic_id AS parent_id,
                        t.topic_name AS parent_name,
                        l.minio_url,
                        l.lesson_des AS description,
                        l.created_at,
                        l.updated_at
                    FROM lesson l
                    JOIN topic t ON l.topic_id = t.topic_id
                    JOIN chunk c ON c.lesson_id = l.lesson_id
                    LEFT JOIN chunk_keyword ck_filter ON ck_filter.chunk_id = c.chunk_id
                    LEFT JOIN keyword k_filter ON k_filter.keyword_id = ck_filter.keyword_id
                    WHERE l.lesson_name ILIKE $1
                """ + tag_where + where_date
            else:
                sql = """
                    SELECT
                        l.lesson_id AS id,
                        l.lesson_name AS name,
                        'lesson' AS type,
                        l.topic_id AS parent_id,
                        t.topic_name AS parent_name,
                        l.minio_url,
                        l.lesson_des AS description,
                        l.created_at,
                        l.updated_at
                    FROM lesson l
                    JOIN topic t ON l.topic_id = t.topic_id
                    WHERE l.lesson_name ILIKE $1
                """ + where_date

            selects.append((sql, base_params + date_params))

        # CHUNK
        if category in (None, "all", "chunk"):
            where_date, date_params = _date_filter(
                "c",
                len(base_params) + 1,
                date_from,
                date_to,
            )

            sql = f"""
                SELECT DISTINCT
                    c.chunk_id AS id,
                    c.chunk_name AS name,
                    'chunk' AS type,
                    c.lesson_id AS parent_id,
                    l.lesson_name AS parent_name,
                    c.minio_url,
                    c.chunk_des AS description,
                    c.created_at,
                    c.updated_at
                FROM chunk c
                JOIN lesson l ON c.lesson_id = l.lesson_id
                {tag_join}
                WHERE (
                    c.chunk_name ILIKE $1
                    OR c.chunk_des ILIKE $1
                )
                {tag_where}
                {where_date}
            """

            selects.append((sql, base_params + date_params))

        # KEYWORD
        if category in (None, "all", "keyword"):
            keyword_params: List[Any] = [keyword]

            where_date, date_params = _date_filter(
                "k",
                len(keyword_params) + 1,
                date_from,
                date_to,
            )

            if tag:
                keyword_params.append(f"%{tag}%")
                sql = """
                    SELECT
                        k.keyword_id AS id,
                        k.keyword_name AS name,
                        'keyword' AS type,
                        NULL::text AS parent_id,
                        NULL::text AS parent_name,
                        NULL::text AS minio_url,
                        k.keyword_slug AS description,
                        k.created_at,
                        k.updated_at
                    FROM keyword k
                    WHERE k.keyword_name ILIKE $1
                      AND k.keyword_name ILIKE $2
                """ + where_date
            else:
                sql = """
                    SELECT
                        k.keyword_id AS id,
                        k.keyword_name AS name,
                        'keyword' AS type,
                        NULL::text AS parent_id,
                        NULL::text AS parent_name,
                        NULL::text AS minio_url,
                        k.keyword_slug AS description,
                        k.created_at,
                        k.updated_at
                    FROM keyword k
                    WHERE k.keyword_name ILIKE $1
                """ + where_date

            selects.append((sql, keyword_params + date_params))

        if not selects:
            return [], 0

        rows: List[Dict[str, Any]] = []

        for sql, params in selects:
            fetched = await conn.fetch(sql, *params)
            rows.extend(dict(row) for row in fetched)

        seen: Dict[str, Dict[str, Any]] = {}

        for row in rows:
            row_id = row.get("id")
            if row_id and row_id not in seen:
                seen[row_id] = row

        all_items = list(seen.values())
        all_items.sort(
            key=lambda item: (
                item.get("type") or "",
                item.get("name") or "",
            )
        )

        total = len(all_items)

        return all_items[offset: offset + size], total


async def _search_neo4j(
    query: str,
    category: Optional[str],
    tag: Optional[str],
    page: int,
    size: int,
) -> List[Dict[str, Any]]:
    try:
        driver = await database.get_neo4j_driver()
    except RuntimeError:
        return []

    offset = (page - 1) * size

    label_map = {
        "class": "Class",
        "subject": "Subject",
        "topic": "Topic",
        "lesson": "Lesson",
        "chunk": "Chunk",
        "keyword": "Keyword",
    }

    label_filter = ""

    if category and category != "all":
        label = label_map.get(category)
        if label:
            label_filter = f"n:{label} AND"

    tag_match = ""
    tag_where = ""

    if tag:
        tag_match = "OPTIONAL MATCH (n)-[*0..2]-(kw:Keyword)"
        tag_where = """
          AND (
                toLower(coalesce(kw.name, '')) CONTAINS toLower($tag_text)
                OR toLower(coalesce(kw.keyword_name, '')) CONTAINS toLower($tag_text)
                OR toLower(coalesce(kw.id, '')) CONTAINS toLower($tag_text)
              )
        """

    cypher = f"""
        MATCH (n)
        {tag_match}
        WHERE {label_filter}
              (
                n:Class
                OR n:Subject
                OR n:Topic
                OR n:Lesson
                OR n:Chunk
                OR n:Keyword
              )
          AND any(
                prop IN keys(n)
                WHERE toLower(toString(n[prop])) CONTAINS toLower($search_text)
              )
          {tag_where}
        RETURN DISTINCT
            coalesce(
                n.id,
                n.class_id,
                n.subject_id,
                n.topic_id,
                n.lesson_id,
                n.chunk_id,
                n.keyword_id,
                n.keyword_key
            ) AS id,
            coalesce(
                n.name,
                n.class_name,
                n.subject_name,
                n.topic_name,
                n.lesson_name,
                n.chunk_name,
                n.keyword_name
            ) AS name,
            toLower(head(labels(n))) AS type,
            n.minio_url AS minio_url,
            coalesce(
                n.description,
                n.lesson_des,
                n.chunk_des,
                n.subject_type,
                n.content
            ) AS description
        SKIP $offset
        LIMIT $size
    """

    async with driver.session() as session:
        result = await session.run(
            cypher,
            search_text=query,
            tag_text=tag or "",
            offset=offset,
            size=size,
        )

        return [dict(record) async for record in result]


async def search_entities(
    query: str,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Dict[str, Any]:
    if category not in VALID_CATEGORIES:
        raise ValueError(
            "category không hợp lệ. Chỉ nhận: class, subject, topic, lesson, chunk, keyword, all"
        )

    parsed_date_from = _parse_date(date_from)
    parsed_date_to = _parse_date(date_to)

    pg_items, pg_total = await _search_pg(
        query=query,
        category=category,
        tag=tag,
        page=page,
        size=size,
        date_from=parsed_date_from,
        date_to=parsed_date_to,
    )

    neo4j_items = await _search_neo4j(
        query=query,
        category=category,
        tag=tag,
        page=page,
        size=size,
    )

    combined: Dict[str, Dict[str, Any]] = {}

    for item in pg_items:
        item["source"] = "postgres"
        item_id = item.get("id")

        if item_id:
            combined[item_id] = item

    for item in neo4j_items:
        item_id = item.get("id")

        if item_id and item_id not in combined:
            item["source"] = "neo4j"
            combined[item_id] = item

    final_items = list(combined.values())

    return {
        "items": final_items,
        "total": pg_total if pg_total >= len(final_items) else len(final_items),
        "page": page,
        "size": size,
        "filters": {
            "q": query,
            "category": category or "all",
            "tag": tag,
            "date_from": date_from,
            "date_to": date_to,
        },
    }