from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import lifespan
from app.api.routes.classes import router as class_router 
from app.api.routes.subject import router as subject_router
from app.api.routes.topic import router as topic_router
from app.api.routes.lesson import router as lesson_router
from app.api.routes.chunk import router as chunk_router
from app.api.routes.keyword import router as keyword_router
from app.api.routes.chunk_keyword import router as chunk_keyword_router
from app.api.routes.upload import router as upload_router
from app.api.routes.sync import router as sync_router
from app.api.routes.query import router as query_router
from app.api.routes.search import router as search_router

app = FastAPI(title='Edu Platform API', version='1.0.0', lifespan=lifespan)

# FE Vite: có thể mở bằng localhost hoặc 127.0.0.1 — cả hai đều cần trong allow_origins
origins = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/health')
async def health():
    return {'status': 'ok'}

app.include_router(class_router, prefix='/api')
app.include_router(subject_router, prefix='/api')
app.include_router(topic_router, prefix='/api')
app.include_router(lesson_router, prefix='/api')
app.include_router(chunk_router, prefix='/api')
app.include_router(keyword_router, prefix='/api')
app.include_router(chunk_keyword_router, prefix='/api')
app.include_router(upload_router, prefix='/api')
app.include_router(sync_router, prefix='/api')
app.include_router(query_router, prefix='/api')
app.include_router(search_router, prefix='/api')