"""
FastAPI Application - Main application setup and configuration.

This module creates and configures the FastAPI application.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config.settings import get_settings
from src.config.logging_config import get_logger
from src.db.session import init_db, close_db

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Ueasys API...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ueasys API...")
    await close_db()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Ueasys API",
        description="Living Character System - Interact with authentic characters",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(
            "Unhandled exception",
            error=str(exc),
            path=request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    
    # Include routers
    from src.api.routes import health, characters, conversations, chat, extraction
    
    app.include_router(health.router, tags=["Health"])
    app.include_router(characters.router, prefix="/api/v1/characters", tags=["Characters"])
    app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["Conversations"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
    app.include_router(extraction.router, prefix="/api", tags=["Extraction"])
    
    logger.info(
        "FastAPI application created",
        debug=settings.debug,
        routes=len(app.routes),
    )
    
    return app


# Create default app instance
app = create_app()
