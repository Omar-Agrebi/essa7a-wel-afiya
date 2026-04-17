"""Initializes the database schema using SQLAlchemy's create_all."""
import asyncio
from typing import Any
from app.core.logging import get_logger
from database.session import engine
from database.base import Base

from app.models.opportunity import Opportunity
from app.models.user import User
from app.models.recommendation import Recommendation
from app.models.notification import Notification

logger = get_logger(__name__)

async def init_db() -> None:
    """Creates all database tables based on defined models."""
    logger.info("Initializing database...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def main() -> None:
    """Entry point for manual script execution."""
    await init_db()

if __name__ == "__main__":
    asyncio.run(main())
