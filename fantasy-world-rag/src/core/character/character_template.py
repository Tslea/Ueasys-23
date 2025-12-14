"""
Character Template - Data Classes for Character Definitions

This module defines the dataclasses used to represent character templates
loaded from YAML files.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class PersonalityTraits:
    """Big Five personality model traits."""
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5
    dominant_traits: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    fears: List[str] = field(default_factory=list)


@dataclass
class EmotionalProfile:
    """Character's emotional configuration."""
    default_mood: str = "neutral"
    mood_volatility: float = 0.3
    joy_triggers: List[str] = field(default_factory=list)
    anger_triggers: List[str] = field(default_factory=list)
    sadness_triggers: List[str] = field(default_factory=list)
    fear_triggers: List[str] = field(default_factory=list)


@dataclass
class SpeechPattern:
    """Character's speaking style and patterns."""
    formality: float = 0.5
    verbosity: float = 0.5
    complexity: float = 0.5
    warmth: float = 0.5
    catchphrases: List[str] = field(default_factory=list)
    vocabulary_preferences: List[str] = field(default_factory=list)
    avoided_words: List[str] = field(default_factory=list)
    style_notes: List[str] = field(default_factory=list)


@dataclass
class CharacterBackground:
    """Character's history and background."""
    origin: str = "Unknown"
    history: str = ""
    key_events: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    world_knowledge: List[str] = field(default_factory=list)


@dataclass
class CharacterGoal:
    """A goal or objective for the character."""
    description: str = ""
    priority: float = 0.5
    goal_type: str = "general"
    progress: float = 0.0


@dataclass
class CharacterRelationship:
    """Relationship with another character."""
    character_id: str = ""
    character_name: str = ""
    relationship_type: str = "neutral"
    strength: float = 0.0
    description: str = ""


@dataclass
class CharacterTemplate:
    """
    Complete character template loaded from YAML.
    
    This is the main data structure that holds all character information
    parsed from YAML files.
    """
    id: str
    name: str
    description: str
    archetype: str
    personality: PersonalityTraits
    emotional_profile: EmotionalProfile
    speech_pattern: SpeechPattern
    background: CharacterBackground
    goals: List[CharacterGoal] = field(default_factory=list)
    relationships: List[CharacterRelationship] = field(default_factory=list)
    
    # Optional fields
    full_name: Optional[str] = None
    world: str = "fantasy"
    role: str = "npc"
    other_names: List[str] = field(default_factory=list)
    knowledge_domains: Dict[str, Any] = field(default_factory=dict)
    response_config: Dict[str, Any] = field(default_factory=dict)
    interaction_patterns: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set full_name if not provided."""
        if self.full_name is None:
            self.full_name = self.name
