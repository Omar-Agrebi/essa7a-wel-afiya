import time
from typing import Any

from database.session import AsyncSessionLocal
from agents.observatory_model import ObservatoryModel
from app.core.config import settings
from app.core.logging import get_logger

from pipeline.tasks.full_pipeline_task import _build_services

async def run_scraping() -> dict[str, Any]:
    """
    Runs stages 1–5 only:
      scrape → clean → classify → cluster → store
    Does not run recommendations or notifications.
    Creates its own DB session.
    Returns partial pipeline report.
    Never raises.
    """
    logger = get_logger("pipeline.tasks.scrape")
    start = time.time()
    logger.info("Scraping task started")
    try:
        async with AsyncSessionLocal() as session:
            services = _build_services(session)
            model = ObservatoryModel(
                services=services,
                settings=settings
            )
            report = await model.run_scraping_only()
        report["task"] = "scraping"
        logger.info(
            f"Scraping task complete — "
            f"duration={round(time.time()-start,2)}s "
            f"raw={report.get('raw_collected',0)} "
            f"stored={report.get('clustered',0)}"
        )
        return report
    except Exception as e:
        logger.error(
            f"Scraping task failed: {e}",
            exc_info=True
        )
        return {
            "task": "scraping",
            "status": "error",
            "error": str(e),
            "duration_sec": round(time.time()-start, 2)
        }
