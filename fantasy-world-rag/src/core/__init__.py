"""
Core module for Fantasy World RAG.

This module contains the fundamental building blocks of the character system:
- Character Engine: Orchestrates all character components
- Personality Core: Defines character identity and traits
- Emotional State: Manages dynamic emotional responses
- Consistency Checker: Validates character behavior against canon
"""

from src.core.character.character_engine import CharacterEngine
from src.core.character.personality_core import PersonalityCore
from src.core.character.emotional_state import EmotionalState
from src.core.character.consistency_checker import ConsistencyChecker

__all__ = [
    "CharacterEngine",
    "PersonalityCore",
    "EmotionalState",
    "ConsistencyChecker",
]
