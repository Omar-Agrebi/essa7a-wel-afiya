from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, Query
from typing import Optional

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

@router.post("/run")
async def run_pipeline(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Trigger the full pipeline execution in the background."""
    from pipeline.tasks import run_full_pipeline
    background_tasks.add_task(run_full_pipeline)
    return {
        "message": "pipeline started",
        "mode": settings.SCRAPER_MODE
    }

@router.post("/run/scraping")
async def run_scraping_pipeline(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Trigger only the scraping stages of the pipeline in the background."""
    from pipeline.tasks import run_full_pipeline
    background_tasks.add_task(run_full_pipeline)
    return {"message": "scraping started"}

@router.post("/run/recommendations")
async def run_recommendations_pipeline(
    background_tasks: BackgroundTasks,
    user_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Trigger recommendation generation in the background."""
    from pipeline.tasks import run_recommendations
    uid_str = str(user_id) if user_id else None
    background_tasks.add_task(run_recommendations, user_id=uid_str)
    return {"message": "recommendations started"}

@router.get("/status")
async def get_pipeline_status():
    """Get the status report of the last pipeline run. Public – no auth required."""
    from pipeline.tasks import get_last_pipeline_report
    return get_last_pipeline_report()
