import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from database.init_db import init_db
from app.api.middleware.cors_middleware import setup_cors_middleware
from app.api.middleware.logging_middleware import LoggingMiddleware

from app.api.routers import opportunity_router
from app.api.routers import user_router
from app.api.routers import recommendation_router
from app.api.routers import notification_router
from app.api.routers import pipeline_router
from app.api.routers import health_router
from app.api.routers import insights_router

logger = get_logger("api.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events mapping to startup and shutdown logic."""
    await init_db()
    logger.info("Application started")
    yield
    logger.info("Application shutting down")

app = FastAPI(
    title="Intelligent University Observatory",
    description="MAS for academic opportunity discovery",
    version="1.0.0",
    lifespan=lifespan
)

# Register Middleware (Order matters)
setup_cors_middleware(app)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(opportunity_router.router)
app.include_router(user_router.router)
app.include_router(recommendation_router.router)
app.include_router(notification_router.router)
app.include_router(pipeline_router.router)
app.include_router(health_router.router)
app.include_router(insights_router.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global handler for unhandled exceptions to prevent server crash leaks."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
