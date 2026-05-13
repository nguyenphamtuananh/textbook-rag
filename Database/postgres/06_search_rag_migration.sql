-- Migration bổ sung cho Pha 2: search/filter theo ngày + update timestamp.

ALTER TABLE "class" ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE "class" ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

ALTER TABLE subject ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE subject ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

ALTER TABLE topic ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE topic ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

ALTER TABLE lesson ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE lesson ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

ALTER TABLE chunk ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE chunk ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

ALTER TABLE keyword ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE keyword ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

ALTER TABLE chunk_keyword ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE chunk_keyword ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

DO $$
DECLARE
    t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['class','subject','topic','lesson','chunk','keyword','chunk_keyword'] LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS %I_set_updated_at ON %I', t, t);
        IF t = 'class' THEN
            EXECUTE 'CREATE TRIGGER class_set_updated_at BEFORE UPDATE ON "class" FOR EACH ROW EXECUTE FUNCTION set_updated_at()';
        ELSE
            EXECUTE format('CREATE TRIGGER %I_set_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION set_updated_at()', t, t);
        END IF;
    END LOOP;
END $$;

CREATE INDEX IF NOT EXISTS idx_class_created_at ON "class"(created_at);
CREATE INDEX IF NOT EXISTS idx_subject_created_at ON subject(created_at);
CREATE INDEX IF NOT EXISTS idx_topic_created_at ON topic(created_at);
CREATE INDEX IF NOT EXISTS idx_lesson_created_at ON lesson(created_at);
CREATE INDEX IF NOT EXISTS idx_chunk_created_at ON chunk(created_at);
CREATE INDEX IF NOT EXISTS idx_keyword_created_at ON keyword(created_at);
