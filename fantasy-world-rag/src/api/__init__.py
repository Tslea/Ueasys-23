"""
API module for Fantasy World RAG.

This module provides the FastAPI application and routes:
- REST API endpoints for characters, conversations, etc.
- WebSocket support for real-time chat
- Authentication and middleware
"""

from src.api.app import create_app, app
from src.api.routes import characters, conversations, chat, health

__all__ = [
    "create_app",
    "app",
    "characters",
    "conversations",
    "chat",
    "health",
]
