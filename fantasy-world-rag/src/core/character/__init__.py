"""
Character module initialization.

Contains all character-related components including personality,
emotional state, and the main character engine.
"""

from src.core.character.character_engine import CharacterEngine
from src.core.character.personality_core import PersonalityCore
from src.core.character.emotional_state import EmotionalState, Emotion
from src.core.character.consistency_checker import ConsistencyChecker

__all__ = [
    "CharacterEngine",
    "PersonalityCore",
    "EmotionalState",
    "Emotion",
    "ConsistencyChecker",
]
