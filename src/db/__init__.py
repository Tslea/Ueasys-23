"""
Database module for Fantasy World RAG.

This module provides database models and connection handling:
- SQLAlchemy models for characters, conversations, memories
- Database session management
- Migrations support with Alembic
"""

from src.db.models.base import Base, TimestampMixin
from src.db.models.character import Character, CharacterTrait, CharacterRelationship
from src.db.models.conversation import Conversation, Message
from src.db.models.memory import Memory, MemoryType
from src.db.session import get_session, async_session_factory

__all__ = [
    "Base",
    "TimestampMixin",
    "Character",
    "CharacterTrait",
    "CharacterRelationship",
    "Conversation",
    "Message",
    "Memory",
    "MemoryType",
    "get_session",
    "async_session_factory",
]
