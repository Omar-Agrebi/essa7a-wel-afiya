import asyncio
import time
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from database.session import AsyncSessionLocal

from agents.observatory_model import ObservatoryModel

from app.services.opportunity_service import OpportunityService
from app.repositories.opportunity_repository import OpportunityRepository

from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

from app.services.recommendation_service import RecommendationService
from app.repositories.recommendation_repository import RecommendationRepository

from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository

from app.core.config import settings
from app.core.logging import get_logger

def _build_services(session: AsyncSession) -> dict[str, Any]:
    """
    Construct all four services with the provided AsyncSession.
    Called inside async with AsyncSessionLocal() blocks.
    Returns dict keyed by service name string.
    """
    return {
        "opportunity": OpportunityService(
            OpportunityRepository(session)),
        "user": UserService(
            UserRepository(session)),
        "recommendation": RecommendationService(
            RecommendationRepository(session)),
        "notification": NotificationService(
            NotificationRepository(session)),
    }

async def run_full_pipeline() -> dict[str, Any]:
    """
    Runs the complete 7-stage Observatory pipeline.
    Stages: scrape → clean → classify → cluster →
            store → recommend → notify
    Creates its own DB session. Safe to call from
    scheduler or API router BackgroundTasks.
    Returns the full pipeline report dict.
    Never raises — returns error dict on failure.
    """
    logger = get_logger("pipeline.tasks.full")
    start = time.time()
    logger.info("Full pipeline task started")
    try:
        async with AsyncSessionLocal() as session:
            services = _build_services(session)
            model = ObservatoryModel(
                services=services,
                settings=settings
            )
            report = await model.run_pipeline()
        report["task"] = "full_pipeline"
        logger.info(
            f"Full pipeline complete — "
            f"duration={round(time.time()-start,2)}s "
            f"raw={report.get('raw_collected',0)} "
            f"stored={report.get('clustered',0)} "
            f"recommendations="
            f"{report.get('recommendations_generated',0)}"
        )
        return report
    except Exception as e:
        logger.error(
            f"Full pipeline task failed: {e}",
            exc_info=True
        )
        return {
            "task": "full_pipeline",
            "status": "error",
            "error": str(e),
            "duration_sec": round(time.time()-start, 2)
        }
