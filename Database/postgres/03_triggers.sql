-- =========================================================
-- Hàm slugify tiếng Việt (dùng chung)
-- =========================================================
CREATE OR REPLACE FUNCTION slugify_vi(input_text text)
RETURNS text
LANGUAGE plpgsql IMMUTABLE AS $$
BEGIN
    RETURN trim(both '-' from
        regexp_replace(
            regexp_replace(
                lower(
                    replace(replace(unaccent(coalesce(input_text,'')),'đ','d'),'Đ','d')
                ),
                '[^a-z0-9]+','-','g'
            ),
            '(^-+|-+$)', '', 'g'
        )
    );
END;
$$;

-- =========================================================
-- CLASS ID = slugify_vi(class_name)
-- =========================================================
CREATE OR REPLACE FUNCTION trg_class_set_id()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.class_id := COALESCE(
        NULLIF(btrim(NEW.class_id),''),
        slugify_vi(NEW.class_name)
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS class_set_id ON "class";
CREATE TRIGGER class_set_id
BEFORE INSERT ON "class"
FOR EACH ROW EXECUTE FUNCTION trg_class_set_id();

-- =========================================================
-- SUBJECT ID = class_id + '_' + slug(subject_name) + '-' + slug(subject_type)
-- =========================================================
CREATE OR REPLACE FUNCTION trg_subject_set_id()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.subject_id := COALESCE(
        NULLIF(btrim(NEW.subject_id),''),
        NEW.class_id || '_' || slugify_vi(NEW.subject_name) || '-' || slugify_vi(NEW.subject_type)
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS subject_set_id ON subject;
CREATE TRIGGER subject_set_id
BEFORE INSERT ON subject
FOR EACH ROW EXECUTE FUNCTION trg_subject_set_id();

-- =========================================================
-- TOPIC ID = subject_id + '_tp-' + topic_num (lpad 2 số)
-- =========================================================
CREATE OR REPLACE FUNCTION trg_topic_set_id()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.topic_id := COALESCE(
        NULLIF(btrim(NEW.topic_id),''),
        NEW.subject_id || '_tp-' || lpad(NEW.topic_num::text, 2, '0')
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS topic_set_id ON topic;
CREATE TRIGGER topic_set_id
BEFORE INSERT ON topic
FOR EACH ROW EXECUTE FUNCTION trg_topic_set_id();

-- =========================================================
-- LESSON ID = topic_id + '_les-' + lesson_num
-- =========================================================
CREATE OR REPLACE FUNCTION trg_lesson_set_id()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.lesson_id := COALESCE(
        NULLIF(btrim(NEW.lesson_id),''),
        NEW.topic_id || '_les-' || lpad(NEW.lesson_num::text, 2, '0')
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS lesson_set_id ON lesson;
CREATE TRIGGER lesson_set_id
BEFORE INSERT ON lesson
FOR EACH ROW EXECUTE FUNCTION trg_lesson_set_id();

-- =========================================================
-- CHUNK ID = lesson_id + '_chunk-' + chunk_num
-- =========================================================
CREATE OR REPLACE FUNCTION trg_chunk_set_id()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.chunk_id := COALESCE(
        NULLIF(btrim(NEW.chunk_id),''),
        NEW.lesson_id || '_chunk-' || lpad(NEW.chunk_num::text, 2, '0')
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS chunk_set_id ON chunk;
CREATE TRIGGER chunk_set_id
BEFORE INSERT ON chunk
FOR EACH ROW EXECUTE FUNCTION trg_chunk_set_id();

-- =========================================================
-- KEYWORD ID = 'kw_' + keyword_slug (tự sinh slug nếu thiếu)
-- =========================================================
CREATE OR REPLACE FUNCTION trg_keyword_set_id()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.keyword_slug IS NULL OR btrim(NEW.keyword_slug) = '' THEN
        NEW.keyword_slug := slugify_vi(NEW.keyword_name);
    END IF;

    NEW.keyword_id := COALESCE(
        NULLIF(btrim(NEW.keyword_id),''),
        'kw_' || NEW.keyword_slug
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS keyword_set_id ON keyword;
CREATE TRIGGER keyword_set_id
BEFORE INSERT ON keyword
FOR EACH ROW EXECUTE FUNCTION trg_keyword_set_id();