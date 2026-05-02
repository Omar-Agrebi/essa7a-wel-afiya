"""Database connection and session factory."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

echo_sql = settings.ENVIRONMENT.lower() == "development"

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=echo_sql,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session and ensures it is closed.
    
    Yields:
        AsyncSession: The database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
