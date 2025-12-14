"""
Health check routes.

Provides endpoints for health checks and system status.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter

from src.config.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.
    
    Returns basic health status of the API.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


@router.get("/health/detailed")
async def detailed_health_check() -> dict[str, Any]:
    """
    Detailed health check endpoint.
    
    Returns detailed status including database and service health.
    """
    checks: dict[str, dict[str, Any]] = {}
    
    # Check database
    try:
        from src.db.session import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = {"status": "healthy"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
    
    # Check Redis
    try:
        import redis.asyncio as redis
        client = redis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}"
        )
        await client.ping()
        await client.close()
        checks["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
    
    # Check Qdrant
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        client.get_collections()
        checks["qdrant"] = {"status": "healthy"}
    except Exception as e:
        checks["qdrant"] = {"status": "unhealthy", "error": str(e)}
    
    # Overall status
    all_healthy = all(
        c.get("status") == "healthy" for c in checks.values()
    )
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "checks": checks,
    }


@router.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Fantasy World RAG API",
        "docs": "/docs",
        "health": "/health",
    }
