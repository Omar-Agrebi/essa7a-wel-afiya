import time
from typing import Any

from database.session import AsyncSessionLocal
from agents.observatory_model import ObservatoryModel
from app.core.config import settings
from app.core.logging import get_logger

from pipeline.tasks.full_pipeline_task import _build_services

async def run_recommendations(
    user_id: str | None = None
) -> dict[str, Any]:
    """
    Runs stage 6 only: recommendation generation.
    Reads opportunities already stored in DB.
    Does not re-scrape or re-classify.

    Args:
      user_id: if provided, generates recommendations
               for that specific user only.
               if None, generates for all registered users.

    Returns recommendation report dict.
    Never raises.
    """
    logger = get_logger("pipeline.tasks.recommend")
    start = time.time()
    target = f"user {user_id}" if user_id else "all users"
    logger.info(f"Recommendation task started for {target}")
    try:
        async with AsyncSessionLocal() as session:
            services = _build_services(session)
            model = ObservatoryModel(
                services=services,
                settings=settings
            )
            report = await model.run_recommendations_only(
                user_id=user_id
            )
        report["task"] = "recommendations"
        report["target"] = target
        logger.info(
            f"Recommendation task complete — "
            f"duration={round(time.time()-start,2)}s "
            f"generated={report.get('items_processed',0)}"
        )
        return report
    except Exception as e:
        logger.error(
            f"Recommendation task failed: {e}",
            exc_info=True
        )
        return {
            "task": "recommendations",
            "status": "error",
            "target": target,
            "error": str(e),
            "duration_sec": round(time.time()-start, 2)
        }
