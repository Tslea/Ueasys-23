"""
Database session management.

This module provides database session and connection handling
using SQLAlchemy async support.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import get_settings
from src.config.logging_config import get_logger

logger = get_logger(__name__)

# Create async engine
_settings = get_settings()

# Build connection URL
DATABASE_URL = (
    f"postgresql+asyncpg://{_settings.postgres_user}:{_settings.postgres_password}"
    f"@{_settings.postgres_host}:{_settings.postgres_port}/{_settings.postgres_db}"
)

# Create engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=_settings.debug,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# Create session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session.
    
    Use as async context manager:
        async with get_session() as session:
            # Use session
            
    Yields:
        AsyncSession for database operations
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error("Database session error", error=str(e))
        raise
    finally:
        await session.close()


async def get_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Use in route handlers:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session_dependency)):
            # Use session
    """
    async with get_session() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    from src.db.models.base import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created")


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")
