-- =========================================================
-- Indexes hỗ trợ JOIN / FILTER
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_subject_class_id ON subject(class_id);
CREATE INDEX IF NOT EXISTS idx_topic_subject_id ON topic(subject_id);
CREATE INDEX IF NOT EXISTS idx_lesson_topic_id ON lesson(topic_id);
CREATE INDEX IF NOT EXISTS idx_chunk_lesson_id ON chunk(lesson_id);

CREATE INDEX IF NOT EXISTS idx_keyword_slug ON keyword(keyword_slug);
CREATE INDEX IF NOT EXISTS idx_chunk_keyword_keyword_id ON chunk_keyword(keyword_id);

CREATE INDEX IF NOT EXISTS idx_user_username ON "user"(username);

-- =========================================================
-- Vector index (HNSW cho topic_embedding)
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_topic_embedding_hnsw
ON topic_embedding USING hnsw (embedding vector_cosine_ops);