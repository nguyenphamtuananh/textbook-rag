from typing import Any, Dict, List, Optional

from app.services.ai_service import gemini_service
from app.services.search_service import search_entities


def _build_context(items: List[Dict[str, Any]]) -> str:
    lines = []
    for idx, item in enumerate(items, start=1):
        title = item.get("name") or "Không có tiêu đề"
        typ = item.get("type") or "unknown"
        parent = item.get("parent_name") or ""
        desc = item.get("description") or ""
        source = item.get("minio_url") or item.get("id") or ""
        lines.append(
            f"[S{idx}] type={typ}; title={title}; parent={parent}; source={source}\n"
            f"content={desc}"
        )
    return "\n\n".join(lines)


def _build_citations(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    citations = []
    for idx, item in enumerate(items, start=1):
        citations.append({
            "ref": f"S{idx}",
            "id": item.get("id"),
            "type": item.get("type"),
            "title": item.get("name"),
            "parent_id": item.get("parent_id"),
            "parent_name": item.get("parent_name"),
            "url": item.get("minio_url"),
            "source": item.get("source"),
        })
    return citations


async def answer_query(
    question: str,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    top_k: int = 8,
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    """
    RAG đơn giản:
    1. Search PostgreSQL + Neo4j lấy context liên quan.
    2. Nhét context vào prompt.
    3. Gemini trả lời có citation [S1], [S2]...
    """
    search_result = await search_entities(
        query=question,
        category=category or "all",
        tag=tag,
        page=1,
        size=top_k,
    )
    context_items = search_result.get("items", [])[:top_k]
    citations = _build_citations(context_items)

    if not context_items:
        return {
            "answer": "Không tìm thấy nội dung liên quan trong tài liệu nội bộ để trả lời câu hỏi này.",
            "citations": [],
            "context_count": 0,
            "model": None,
        }

    context = _build_context(context_items)
    prompt = f"""
Bạn là trợ lý AI tra cứu tài liệu nội bộ.
Chỉ trả lời dựa trên CONTEXT bên dưới. Nếu context không đủ, hãy nói rõ là chưa đủ dữ liệu.
Khi dùng thông tin từ nguồn nào, hãy gắn citation dạng [S1], [S2] ở cuối câu.
Trả lời bằng tiếng Việt, rõ ràng, ngắn gọn, đúng trọng tâm.

QUESTION:
{question}

CONTEXT:
{context}

YÊU CẦU OUTPUT:
- Trả lời trực tiếp câu hỏi.
- Có citation [Sx] cho các ý quan trọng.
- Không bịa thông tin ngoài context.
""".strip()

    ai_result = await gemini_service.query(prompt, timeout_seconds=timeout_seconds)
    return {
        "answer": ai_result.get("text", ""),
        "citations": citations,
        "context_count": len(context_items),
        "model": ai_result.get("model"),
        "finish_reason": ai_result.get("finish_reason"),
    }
