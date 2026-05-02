import time
from typing import Any

from database.session import AsyncSessionLocal
from agents.observatory_model import ObservatoryModel
from app.core.config import settings
from app.core.logging import get_logger

from pipeline.tasks.full_pipeline_task import _build_services

async def run_notifications() -> dict[str, Any]:
    """
    Runs stage 7 only: notification dispatch.

    What this does:
      Scans opportunities expiring within 7 days.
      Matches them to users whose interests overlap
      with the opportunity's category.
      CREATES new dashboard notifications in the DB
      for each match found.
      Does NOT read or return existing notifications —
      that is the API's responsibility.

    Creates its own DB session.
    Calls model.notifier.run_safe() directly,
    bypassing the full pipeline scheduler.
    Returns notification agent report dict.
    Never raises.
    """
    logger = get_logger("pipeline.tasks.notify")
    start = time.time()
    logger.info("Notification task started")
    try:
        async with AsyncSessionLocal() as session:
            services = _build_services(session)
            model = ObservatoryModel(
                services=services,
                settings=settings
            )
            # Call the notification agent directly:
            report = await model.notifier.run_safe()
        report["task"] = "notifications"
        logger.info(
            f"Notification task complete — "
            f"duration={round(time.time()-start,2)}s "
            f"created={report.get('notifications_created',0)}"
        )
        return report
    except Exception as e:
        logger.error(
            f"Notification task failed: {e}",
            exc_info=True
        )
        return {
            "task": "notifications",
            "status": "error",
            "error": str(e),
            "duration_sec": round(time.time()-start, 2)
        }
