import os
from minio import Minio
from minio.error import S3Error
from pymongo import MongoClient
from app.core.config import settings
from datetime import datetime

def upload_and_sync_lesson(file_path: str, topic_id: str, lesson_num: int,
                           lesson_name: str, lesson_type: str, lesson_des: str):
    """
    Upload file PDF lên MinIO và đồng bộ metadata vào MongoDB.
    Trả về dict: {lesson_id, mongo_id, minio_url}
    """
    # MinIO client
    minio_client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=False
    )
    bucket = settings.MINIO_BUCKET

    # Đảm bảo bucket tồn tại
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)

    # Tạo lesson_id và object_key
    lesson_id = f"{topic_id}_les-{lesson_num:02d}"
    object_key = f"documents/lop-10/tin-hoc/lesson/{topic_id}-lesson_{lesson_num:02d}.pdf"

    try:
        # Upload file
        minio_client.fput_object(bucket, object_key, file_path)
        minio_url = f"http://{settings.MINIO_ENDPOINT}/{bucket}/{object_key}"
    except S3Error as e:
        raise Exception(f"MinIO upload failed: {e}")

    # Kết nối MongoDB và insert document
    try:
        mongo_client = MongoClient(settings.MONGO_URI)
        db = mongo_client[settings.MONGO_DB]
        collection = db["lesson"]
        doc = {
            "lesson_id": lesson_id,
            "lesson_num": lesson_num,
            "lesson_name": lesson_name,
            "lesson_type": lesson_type,
            "lesson_des": lesson_des,
            "topic_id": topic_id,
            "minio_url": minio_url,
            "asset_prefixes": {"documents": [minio_url], "images": [], "videos": []},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_deleted": False
        }
        result = collection.insert_one(doc)
        mongo_id = str(result.inserted_id)
    except Exception as e:
        # Có thể rollback MinIO? Tạm thời báo lỗi
        raise Exception(f"MongoDB insert failed: {e}")
    finally:
        mongo_client.close()

    return {
        "lesson_id": lesson_id,
        "mongo_id": mongo_id,
        "minio_url": minio_url
    }