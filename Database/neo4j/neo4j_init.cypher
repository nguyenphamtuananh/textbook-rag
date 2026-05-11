// =========================================================
// Neo4j Init Script - chạy khi khởi tạo database
// Sử dụng với docker-compose hoặc thủ công
// =========================================================

// -------- Constraints (khóa duy nhất) --------
CREATE CONSTRAINT thing_id_unique IF NOT EXISTS
FOR (t:Thing) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT class_id_unique IF NOT EXISTS
FOR (c:Class) REQUIRE c.class_id IS UNIQUE;

CREATE CONSTRAINT subject_id_unique IF NOT EXISTS
FOR (s:Subject) REQUIRE s.subject_id IS UNIQUE;

CREATE CONSTRAINT topic_id_unique IF NOT EXISTS
FOR (t:Topic) REQUIRE t.topic_id IS UNIQUE;

CREATE CONSTRAINT lesson_id_unique IF NOT EXISTS
FOR (l:Lesson) REQUIRE l.lesson_id IS UNIQUE;

CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
FOR (c:Chunk) REQUIRE c.chunk_id IS UNIQUE;

CREATE CONSTRAINT keyword_key_unique IF NOT EXISTS
FOR (k:Keyword) REQUIRE k.keyword_key IS UNIQUE;

// -------- Vector index cho embedding topic --------
CREATE VECTOR INDEX topic_embedding_idx IF NOT EXISTS
FOR (n:Topic) ON (n.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 768,
  `vector.similarity_function`: 'cosine'
}};

// -------- Node gốc bắt buộc --------
MERGE (:Thing {id: 'thing'})
ON CREATE SET name = 'Thing';