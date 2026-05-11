from fastapi import FastAPI
from app.core.database import init_pg, close_pg
from app.api.routes.my_class import router as class_router
from app.api.routes.subject import router as subject_router
from app.api.routes.topic import router as topic_router
from app.api.routes.lesson import router as lesson_router
from app.api.routes.chunk import router as chunk_router
from app.api.routes.keyword import router as keyword_router
from app.api.routes.chunk_keyword import router as chunk_keyword_router
from app.api.routes.upload import router as upload_router
from app.api.routes.sync import router as sync_router

app = FastAPI(title="Edu Platform API", version="1.0.0")

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# Đăng ký routers
app.include_router(class_router, prefix="/api")
app.include_router(subject_router, prefix="/api")
app.include_router(topic_router, prefix="/api")
app.include_router(lesson_router, prefix="/api")
app.include_router(chunk_router, prefix="/api")
app.include_router(keyword_router, prefix="/api")
app.include_router(chunk_keyword_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(sync_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    await init_pg()

@app.on_event("shutdown")
async def shutdown_event():
    await close_pg()