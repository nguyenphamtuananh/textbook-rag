from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ---- Class ----
class ClassCreate(BaseModel):
    class_name: str
    mongo_id: Optional[str] = None

class ClassResponse(BaseModel):
    class_id: str
    class_name: str
    minio_url: Optional[str] = None
    mongo_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ---- Subject ----
class SubjectCreate(BaseModel):
    subject_name: str
    subject_type: str
    class_id: str
    mongo_id: Optional[str] = None

class SubjectResponse(BaseModel):
    subject_id: str
    subject_name: str
    subject_type: str
    class_id: str
    minio_url: Optional[str] = None
    mongo_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ---- Topic ----
class TopicCreate(BaseModel):
    topic_num: int
    topic_name: str
    subject_id: str
    mongo_id: Optional[str] = None

class TopicResponse(BaseModel):
    topic_id: str
    topic_num: int
    topic_name: str
    subject_id: str
    minio_url: Optional[str] = None
    mongo_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ---- Lesson ----
class LessonCreate(BaseModel):
    lesson_num: int
    lesson_name: str
    lesson_type: Optional[str] = None
    lesson_des: Optional[str] = None
    topic_id: str
    mongo_id: Optional[str] = None

class LessonResponse(BaseModel):
    lesson_id: str
    lesson_num: int
    lesson_name: str
    lesson_type: Optional[str] = None
    lesson_des: Optional[str] = None
    topic_id: str
    minio_url: Optional[str] = None
    mongo_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ---- Chunk ----
class ChunkCreate(BaseModel):
    chunk_num: int
    chunk_name: str
    chunk_des: Optional[str] = None
    lesson_id: str
    mongo_id: Optional[str] = None

class ChunkResponse(BaseModel):
    chunk_id: str
    chunk_num: int
    chunk_name: str
    chunk_des: Optional[str] = None
    lesson_id: str
    minio_url: Optional[str] = None
    mongo_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ---- Keyword ----
class KeywordCreate(BaseModel):
    keyword_name: str
    keyword_slug: Optional[str] = None  # sẽ tự sinh nếu để None
    mongo_id: Optional[str] = None

class KeywordResponse(BaseModel):
    keyword_id: str
    keyword_name: str
    keyword_slug: str
    mongo_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ---- ChunkKeyword ----
class ChunkKeywordLink(BaseModel):
    chunk_id: str
    keyword_id: str
    mongo_id: Optional[str] = None

class ChunkKeywordResponse(BaseModel):
    chunk_id: str
    keyword_id: str
    mongo_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
# ---- Search Response ----
class SearchResultItem(BaseModel):
    id: str
    name: str
    type: str
    parent_name: Optional[str] = None
    parent_id: Optional[str] = None

class SearchResponse(BaseModel):
    items: List[SearchResultItem]
    total: int
    page: int
    size: int