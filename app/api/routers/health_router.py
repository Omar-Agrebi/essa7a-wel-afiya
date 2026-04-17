from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def check_health():
    """Health check for system status and environment mapping."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "scraper_mode": settings.SCRAPER_MODE
    }

@router.get("/db")
async def check_database(db: AsyncSession = Depends(get_db)):
    """Health check for database connectivity by testing a simple SELECT 1."""
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "unreachable"
        }
