-- Seed tối thiểu cho dev / FE test (class → subject → topic → lesson)
-- Chạy: docker exec -i edu_postgres psql -U edu_user -d edu_db < Database/postgres/05_dev_seed.sql
-- Hoặc từ máy host (PowerShell tại D:\textbook):
--   Get-Content Database\postgres\05_dev_seed.sql | docker exec -i edu_postgres psql -U edu_user -d edu_db

BEGIN;

INSERT INTO "class" (class_id, class_name, minio_url, mongo_id)
VALUES (
    'demo-class-12',
    'Lớp 12',
    NULL,
    NULL
)
ON CONFLICT (class_id) DO NOTHING;

INSERT INTO subject (subject_id, class_id, subject_name, subject_type, minio_url, mongo_id)
VALUES (
    'demo-class-12_toan-hoc-ket-noi-tri-thuc',
    'demo-class-12',
    'Toán học',
    'Kết nối tri thức',
    NULL,
    NULL
)
ON CONFLICT (subject_id) DO NOTHING;

INSERT INTO topic (topic_id, subject_id, topic_num, topic_name, minio_url, mongo_id)
VALUES (
    'demo-class-12_toan-hoc-ket-noi-tri-thuc_tp-01',
    'demo-class-12_toan-hoc-ket-noi-tri-thuc',
    1,
    'Ứng dụng đạo hàm để khảo sát và vẽ đồ thị hàm số',
    NULL,
    NULL
)
ON CONFLICT (topic_id) DO NOTHING;

INSERT INTO lesson (lesson_id, topic_id, lesson_num, lesson_name, lesson_des, lesson_type, minio_url, mongo_id)
VALUES (
    'demo-class-12_toan-hoc-ket-noi-tri-thuc_tp-01_les-01',
    'demo-class-12_toan-hoc-ket-noi-tri-thuc_tp-01',
    1,
    'Khảo sát hàm số và vẽ đồ thị',
    'Ôn tập đạo hàm, bảng biến thiên và tiệm cận.',
    'ly thuyet',
    NULL,
    NULL
)
ON CONFLICT (lesson_id) DO NOTHING;

INSERT INTO lesson (lesson_id, topic_id, lesson_num, lesson_name, lesson_des, lesson_type, minio_url, mongo_id)
VALUES (
    'demo-class-12_toan-hoc-ket-noi-tri-thuc_tp-01_les-02',
    'demo-class-12_toan-hoc-ket-noi-tri-thuc_tp-01',
    2,
    'Bài tập cực trị thực tế',
    'Bài tập ứng dụng tìm max/min.',
    'bai tap',
    NULL,
    NULL
)
ON CONFLICT (lesson_id) DO NOTHING;

COMMIT;
