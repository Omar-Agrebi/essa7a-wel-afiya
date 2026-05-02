import asyncio
import signal
import time
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from pipeline.tasks import (
    run_full_pipeline,
    run_recommendations,
    run_notifications
)
from app.core.logging import get_logger

UTC = timezone.utc

class PipelineScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="UTC")
        self.logger = get_logger("pipeline.scheduler")
        self._running: bool = False
        self._job_history: list[dict] = []

    def _append_history(self, entry: dict) -> None:
        if len(self._job_history) >= 50:
            self._job_history.pop(0)
        self._job_history.append(entry)

    def _setup_jobs(self) -> None:
        """Register all three scheduled jobs."""
        
        # Job 1 — Full pipeline, every 24 hours
        self.scheduler.add_job(
            func=self._run_full_pipeline_job,
            trigger=IntervalTrigger(hours=24, timezone="UTC"),
            id="full_pipeline",
            name="Full Observatory Pipeline",
            replace_existing=True,
            next_run_time=datetime.now(UTC) + timedelta(seconds=90)
        )

        # Job 2 — Recommendations, every 12 hours
        self.scheduler.add_job(
            func=self._run_recommendations_job,
            trigger=IntervalTrigger(hours=12, timezone="UTC"),
            id="recommendations",
            name="Recommendation Refresh",
            replace_existing=True,
            next_run_time=datetime.now(UTC) + timedelta(seconds=60)
        )

        # Job 3 — Notifications, every 6 hours
        self.scheduler.add_job(
            func=self._run_notifications_job,
            trigger=IntervalTrigger(hours=6, timezone="UTC"),
            id="notifications",
            name="Deadline Notifications",
            replace_existing=True,
            next_run_time=datetime.now(UTC) + timedelta(seconds=30)
        )

        # Log registered jobs
        for job in self.scheduler.get_jobs():
            self.logger.info(
                f"Job registered: '{job.name}' — "
                f"first run: {job.next_run_time.isoformat() if job.next_run_time else 'None'}"
            )

    async def _run_full_pipeline_job(self) -> None:
        """APScheduler job: full pipeline."""
        entry = {
            "job_id": "full_pipeline",
            "started_at": datetime.now(UTC).isoformat(),
            "status": "running",
            "finished_at": None,
            "summary": None,
            "error": None
        }
        self._append_history(entry)
        self.logger.info("Scheduled full pipeline job starting")
        try:
            report = await run_full_pipeline()
            entry["status"] = report.get("status", "success")
            entry["finished_at"] = datetime.now(UTC).isoformat()
            entry["summary"] = {
                "raw_collected": report.get("raw_collected", 0),
                "stored": report.get("clustered", 0),
                "recommendations": report.get("recommendations_generated", 0),
                "pipeline_errors": len(report.get("pipeline_errors", []))
            }
            self.logger.info(
                f"Full pipeline job complete: {entry['summary']}"
            )
        except Exception as e:
            entry["status"] = "error"
            entry["error"] = str(e)
            entry["finished_at"] = datetime.now(UTC).isoformat()
            self.logger.error(
                f"Full pipeline job failed: {e}",
                exc_info=True
            )

    async def _run_recommendations_job(self) -> None:
        """APScheduler job: recommendations only."""
        entry = {
            "job_id": "recommendations",
            "started_at": datetime.now(UTC).isoformat(),
            "status": "running",
            "finished_at": None,
            "error": None
        }
        self._append_history(entry)
        self.logger.info("Scheduled recommendation job starting")
        try:
            report = await run_recommendations()
            entry["status"] = "success"
            entry["finished_at"] = datetime.now(UTC).isoformat()
            entry["generated"] = report.get("items_processed", 0)
            self.logger.info(
                f"Recommendation job complete — "
                f"generated={entry['generated']}"
            )
        except Exception as e:
            entry["status"] = "error"
            entry["error"] = str(e)
            entry["finished_at"] = datetime.now(UTC).isoformat()
            self.logger.error(
                f"Recommendation job failed: {e}",
                exc_info=True
            )

    async def _run_notifications_job(self) -> None:
        """APScheduler job: notifications only."""
        entry = {
            "job_id": "notifications",
            "started_at": datetime.now(UTC).isoformat(),
            "status": "running",
            "finished_at": None,
            "error": None
        }
        self._append_history(entry)
        self.logger.info("Scheduled notification job starting")
        try:
            report = await run_notifications()
            entry["status"] = "success"
            entry["finished_at"] = datetime.now(UTC).isoformat()
            entry["created"] = report.get("notifications_created", 0)
            self.logger.info(
                f"Notification job complete — "
                f"created={entry['created']}"
            )
        except Exception as e:
            entry["status"] = "error"
            entry["error"] = str(e)
            entry["finished_at"] = datetime.now(UTC).isoformat()
            self.logger.error(
                f"Notification job failed: {e}",
                exc_info=True
            )

    def start(self) -> None:
        """Start the scheduler. No-op if already running."""
        if self._running:
            self.logger.warning(
                "Scheduler already running — ignoring start()"
            )
            return
        self._setup_jobs()
        self.scheduler.start()
        self._running = True
        self.logger.info(
            f"PipelineScheduler started — "
            f"{len(self.scheduler.get_jobs())} jobs registered"
        )

    def stop(self) -> None:
        """Gracefully stop the scheduler."""
        if not self._running:
            return
        self.scheduler.shutdown(wait=False)
        self._running = False
        self.logger.info("PipelineScheduler stopped")

    def get_jobs_info(self) -> list[dict]:
        """Return current job metadata for API status endpoint."""
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": (
                    job.next_run_time.isoformat()
                    if job.next_run_time else None
                ),
                "trigger": str(job.trigger)
            }
            for job in self.scheduler.get_jobs()
        ]

    def get_job_history(self, limit: int = 20) -> list[dict]:
        """Return last N job execution records."""
        return self._job_history[-limit:]

    @property
    def is_running(self) -> bool:
        return self._running


pipeline_scheduler = PipelineScheduler()

def start_scheduler() -> None:
    """Called by FastAPI lifespan on startup."""
    pipeline_scheduler.start()

def stop_scheduler() -> None:
    """Called by FastAPI lifespan on shutdown."""
    pipeline_scheduler.stop()


if __name__ == "__main__":
    """
    Standalone worker mode.
    Run with: python -m pipeline.scheduler
    Starts the scheduler and keeps the process alive
    until SIGINT or SIGTERM is received.
    Handles both Docker container signals and
    keyboard interrupt gracefully.
    """

    async def _worker_main() -> None:
        logger = get_logger("pipeline.worker")
        logger.info(
            "Pipeline worker process starting in "
            "standalone mode"
        )

        pipeline_scheduler.start()

        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()

        def _handle_signal(sig_name: str) -> None:
            logger.info(
                f"Signal {sig_name} received — "
                f"initiating shutdown"
            )
            stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda s=sig: _handle_signal(s.name)
            )

        logger.info(
            "Worker running. "
            "Send SIGINT or SIGTERM to stop."
        )

        await stop_event.wait()

        pipeline_scheduler.stop()
        logger.info(
            "Pipeline worker stopped cleanly"
        )

    asyncio.run(_worker_main())
