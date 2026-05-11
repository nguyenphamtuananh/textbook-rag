from fastapi import APIRouter, BackgroundTasks
from app.services.pg_to_neo_sync import sync_all

router = APIRouter(prefix="/sync", tags=["Sync"])

@router.post("/neo4j")
async def sync_neo4j(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_all)
    return {"message": "Sync started in background"}