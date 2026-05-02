from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
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
    try:
        from agents.system.coordinator_agent import AgentCoordinator
        coordinator = AgentCoordinator()
        background_tasks.add_task(coordinator.run_full_pipeline)
    except ImportError:
        pass
    
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
    try:
        from agents.system.coordinator_agent import AgentCoordinator
        coordinator = AgentCoordinator()
        background_tasks.add_task(coordinator.run_scraping)
    except ImportError:
        pass
        
    return {"message": "scraping started"}

@router.post("/run/recommendations")
async def run_recommendations_pipeline(
    background_tasks: BackgroundTasks,
    user_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Trigger recommendation generation in the background."""
    try:
        from agents.system.coordinator_agent import AgentCoordinator
        coordinator = AgentCoordinator()
        background_tasks.add_task(coordinator.run_recommendations, user_id=user_id)
    except ImportError:
        pass
        
    return {"message": "recommendations started"}

@router.get("/status")
async def get_pipeline_status(
    current_user: User = Depends(get_current_user)
):
    """Get the status report of the last run from AgentCoordinator."""
    try:
        from agents.system.coordinator_agent import AgentCoordinator
        # Assuming coordinator stores a class-level variable report, or has a static way to retrieve it
        if hasattr(AgentCoordinator, "last_report") and AgentCoordinator.last_report:
            return AgentCoordinator.last_report
    except ImportError:
        pass
        
    return {"status": "never_run"}
