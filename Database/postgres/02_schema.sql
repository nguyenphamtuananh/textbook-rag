-- =========================================================
-- CLASS
-- =========================================================
CREATE TABLE IF NOT EXISTS "class" (
    class_id    text PRIMARY KEY,
    class_name  text NOT NULL,
    minio_url   text,       -- file PDF chính của lớp (nếu có)
    mongo_id    text UNIQUE
);

-- =========================================================
-- SUBJECT
-- =========================================================
CREATE TABLE IF NOT EXISTS subject (
    subject_id    text PRIMARY KEY,
    class_id      text NOT NULL REFERENCES "class"(class_id) ON DELETE CASCADE,
    subject_name  text NOT NULL,
    subject_type  text NOT NULL,
    minio_url     text,
    mongo_id      text UNIQUE
);

-- =========================================================
-- TOPIC
-- =========================================================
CREATE TABLE IF NOT EXISTS topic (
    topic_id    text PRIMARY KEY,
    subject_id  text NOT NULL REFERENCES subject(subject_id) ON DELETE CASCADE,
    topic_num   integer NOT NULL,
    topic_name  text NOT NULL,
    minio_url   text,
    mongo_id    text UNIQUE
);

-- =========================================================
-- LESSON
-- =========================================================
CREATE TABLE IF NOT EXISTS lesson (
    lesson_id    text PRIMARY KEY,
    topic_id     text NOT NULL REFERENCES topic(topic_id) ON DELETE CASCADE,
    lesson_num   integer NOT NULL,
    lesson_name  text NOT NULL,
    lesson_des   text,
    lesson_type  text,
    minio_url    text,
    mongo_id     text UNIQUE
);

-- =========================================================
-- CHUNK
-- =========================================================
CREATE TABLE IF NOT EXISTS chunk (
    chunk_id    text PRIMARY KEY,
    lesson_id   text NOT NULL REFERENCES lesson(lesson_id) ON DELETE CASCADE,
    chunk_num   integer NOT NULL,
    chunk_name  text NOT NULL,
    chunk_des   text,
    minio_url   text,
    mongo_id    text UNIQUE
);

-- =========================================================
-- KEYWORD
-- =========================================================
CREATE TABLE IF NOT EXISTS keyword (
    keyword_id    text PRIMARY KEY,
    keyword_name  text NOT NULL UNIQUE,
    keyword_slug  text NOT NULL,
    mongo_id      text UNIQUE
);

-- =========================================================
-- CHUNK_KEYWORD
-- =========================================================
CREATE TABLE IF NOT EXISTS chunk_keyword (
    chunk_id    text NOT NULL REFERENCES chunk(chunk_id) ON DELETE CASCADE,
    keyword_id  text NOT NULL REFERENCES keyword(keyword_id) ON DELETE CASCADE,
    mongo_id    text UNIQUE,
    PRIMARY KEY (chunk_id, keyword_id)
);

-- =========================================================
-- USER
-- =========================================================
CREATE TABLE IF NOT EXISTS "user" (
    user_id   text PRIMARY KEY,
    username  text NOT NULL UNIQUE,
    password  text NOT NULL,
    user_role text NOT NULL CHECK (user_role IN ('admin','user')),
    is_active boolean NOT NULL DEFAULT true,
    mongo_id  text UNIQUE
);

-- =========================================================
-- TOPIC EMBEDDING (pgvector)
-- =========================================================
CREATE TABLE IF NOT EXISTS topic_embedding (
    topic_id   text PRIMARY KEY REFERENCES topic(topic_id) ON DELETE CASCADE,
    embedding  vector(768) NOT NULL,
    model_name text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);