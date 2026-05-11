import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from app.services.minio_upload_sync import upload_and_sync_lesson

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/lesson")
async def upload_lesson(
    file: UploadFile = File(...),
    topic_id: str = Form(...),
    lesson_num: int = Form(...),
    lesson_name: str = Form(...),
    lesson_type: str = Form("ly thuyet"),
    lesson_des: str = Form(""),
    background_tasks: BackgroundTasks = None
):
    # Lưu file tạm an toàn
    temp_dir = "/tmp/edu_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Ghi file bất đồng bộ
        async with aiofiles.open(temp_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Gọi service (có thể chạy nền nếu cần)
        result = upload_and_sync_lesson(
            file_path=temp_path,
            topic_id=topic_id,
            lesson_num=lesson_num,
            lesson_name=lesson_name,
            lesson_type=lesson_type,
            lesson_des=lesson_des
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Dọn dẹp file tạm trong background
        if background_tasks:
            background_tasks.add_task(os.unlink, temp_path)
        else:
            try:
                os.remove(temp_path)
            except OSError:
                pass