CREATE EXTENSION IF NOT EXISTS unaccent;

-- Hàm slugify tiếng Việt
CREATE OR REPLACE FUNCTION slugify_vi(input_text text)
RETURNS text
LANGUAGE plpgsql IMMUTABLE AS $$
BEGIN
    RETURN trim(both '-' from regexp_replace(
        regexp_replace(
            lower(replace(replace(unaccent(coalesce(input_text,'')),'đ','d'),'Đ','d')),
            '[^a-z0-9]+','-','g'
        ), '(^-+|-+$)', '', 'g'
    ));
END;
$$;

-- Class
CREATE TABLE "class" (
    class_id   text PRIMARY KEY,
    class_name text NOT NULL,
    minio_url  text,              -- File PDF SGK lớp (nếu có)
    mongo_id   text UNIQUE
);

-- Subject
CREATE TABLE subject (
    subject_id   text PRIMARY KEY,
    class_id     text NOT NULL REFERENCES "class"(class_id) ON DELETE CASCADE,
    subject_name text NOT NULL,
    subject_type text NOT NULL,   -- Ví dụ: 'Kết nối tri thức'
    minio_url    text,            -- File PDF môn học
    mongo_id     text UNIQUE
);

-- Topic
CREATE TABLE topic (
    topic_id   text PRIMARY KEY,
    subject_id text NOT NULL REFERENCES subject(subject_id) ON DELETE CASCADE,
    topic_num  integer NOT NULL,
    topic_name text NOT NULL,
    minio_url  text,              -- File PDF chủ đề
    mongo_id   text UNIQUE
);

-- Lesson
CREATE TABLE lesson (
    lesson_id   text PRIMARY KEY,
    topic_id    text NOT NULL REFERENCES topic(topic_id) ON DELETE CASCADE,
    lesson_num  integer NOT NULL,
    lesson_name text NOT NULL,
    lesson_type text,             -- 'ly thuyet', 'bai tap', ...
    lesson_des  text,
    minio_url   text,             -- File PDF bài học
    mongo_id    text UNIQUE
);

-- Chunk
CREATE TABLE chunk (
    chunk_id   text PRIMARY KEY,
    lesson_id  text NOT NULL REFERENCES lesson(lesson_id) ON DELETE CASCADE,
    chunk_num  integer NOT NULL,
    chunk_name text NOT NULL,
    chunk_des  text,
    minio_url  text,              -- File PDF phân đoạn
    mongo_id   text UNIQUE
);

-- Keyword
CREATE TABLE keyword (
    keyword_id   text PRIMARY KEY,
    keyword_name text NOT NULL UNIQUE,
    keyword_slug text NOT NULL,
    mongo_id     text UNIQUE
);

-- Chunk - Keyword (N-N)
CREATE TABLE chunk_keyword (
    chunk_id   text NOT NULL REFERENCES chunk(chunk_id) ON DELETE CASCADE,
    keyword_id text NOT NULL REFERENCES keyword(keyword_id) ON DELETE CASCADE,
    mongo_id   text UNIQUE,
    PRIMARY KEY (chunk_id, keyword_id)
);

-- User (đơn giản hóa)
CREATE TABLE "user" (
    user_id   text PRIMARY KEY,
    username  text NOT NULL UNIQUE,
    password  text NOT NULL,
    user_role text NOT NULL CHECK (user_role IN ('admin','user')),
    is_active boolean NOT NULL DEFAULT true,
    mongo_id  text UNIQUE
);

-- Bảng lưu vector embedding (dùng pgvector)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE topic_embedding (
    topic_id   text PRIMARY KEY REFERENCES topic(topic_id) ON DELETE CASCADE,
    embedding  vector(768),
    model_name text NOT NULL,
    updated_at timestamptz DEFAULT now()
);