# Bổ sung Pha 2 - Truy vấn T5-6

Các file đã được bổ sung/sửa:

- `app/api/routes/query.py`
- `app/api/routes/search.py`
- `app/services/ai_service.py`
- `app/services/search_service.py`
- `app/services/rag_service.py`
- `app/core/database.py`
- `Database/postgres/06_search_rag_migration.sql`
- `docker-compose.yml`
- `.env.example`

## Đã đáp ứng task

### BE-1
- `POST /api/query`
- Gọi AI Gemini có retry
- Có timeout
- Có xử lý lỗi 400/500/504
- Có search context từ PostgreSQL + Neo4j trước khi AI trả lời
- Response có `answer`, `citations`, `context_count`, `model`

### BE-2
- `GET /api/search`
- Query PostgreSQL + Neo4j
- Có phân trang `page`, `size`
- Có lọc `category`
- Có lọc `tag`
- Có lọc ngày `date_from`, `date_to` theo `created_at`

## Chạy migration nếu database đã tồn tại

Nếu bạn đã từng chạy Docker trước đó, file init SQL mới sẽ không tự chạy lại vì volume Postgres đã tồn tại. Có 2 cách:

### Cách 1: Reset database dev

```bash
docker compose down -v
docker compose up -d --build
```

### Cách 2: Chạy migration thủ công, không xóa data

```bash
docker exec -i edu_postgres psql -U edu_user -d edu_db < Database/postgres/06_search_rag_migration.sql
```

## Test API

### Search

```bash
curl "http://localhost:8000/api/search?q=toán&page=1&size=10"
```

```bash
curl "http://localhost:8000/api/search?q=hình&category=chunk&tag=tam giác&page=1&size=10"
```

```bash
curl "http://localhost:8000/api/search?q=bài&date_from=2026-01-01&date_to=2026-12-31"
```

### Query RAG

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Nội dung bài học nói về gì?","top_k":8,"timeout_seconds":30}'
```

Response mẫu:

```json
{
  "answer": "... [S1]",
  "citations": [
    {
      "ref": "S1",
      "id": "...",
      "type": "chunk",
      "title": "...",
      "url": "...",
      "source": "postgres"
    }
  ],
  "context_count": 1,
  "model": "gemini-2.0-flash",
  "finish_reason": "..."
}
```

## Lưu ý bảo mật

Không upload file `.env` thật lên mạng hoặc ChatGPT. Chỉ gửi `.env.example`.
