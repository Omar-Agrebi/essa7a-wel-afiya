"""
Pipeline task exports.
Import task functions from here for clean imports
in scheduler.py and API routers.
"""

from pipeline.tasks.full_pipeline_task import (
    run_full_pipeline,
    _build_services,
    get_last_pipeline_report,
)
from pipeline.tasks.scrape_task import run_scraping
from pipeline.tasks.recommend_task import run_recommendations
from pipeline.tasks.notify_task import run_notifications

__all__ = [
    "run_full_pipeline",
    "run_scraping",
    "run_recommendations",
    "run_notifications",
    "_build_services",
]
