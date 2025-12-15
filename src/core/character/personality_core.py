"""
Personality Core - Immutable character identity and traits.

This module defines the foundational personality of a character,
including their archetypes, values, core traits, and fundamental
identity that should remain consistent across all interactions.

The PersonalityCore is the "soul" of the character - it never changes
and serves as the anchor for all character behavior.

Example:
    >>> from src.core.character import PersonalityCore
    >>> gandalf = PersonalityCore.from_yaml("data/characters/gandalf/personality.yaml")
    >>> print(gandalf.primary_archetype)
    'The Wise Mentor'
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Self

import yaml
from pydantic import BaseModel, Field, field_validator

from src.config.logging_config import get_logger

logger = get_logger(__name__)


class Archetype(str, Enum):
    """
    Character archetypes based on Jungian psychology and fantasy tropes.
    
    These archetypes help define the fundamental nature of a character
    and guide their typical behaviors and responses.
    """
    HERO = "hero"
    MENTOR = "mentor"
    TRICKSTER = "trickster"
    SHADOW = "shadow"
    GUARDIAN = "guardian"
    HERALD = "herald"
    SHAPESHIFTER = "shapeshifter"
    THRESHOLD_GUARDIAN = "threshold_guardian"
    RULER = "ruler"
    SAGE = "sage"
    INNOCENT = "innocent"
    EXPLORER = "explorer"
    REBEL = "rebel"
    LOVER = "lover"
    CREATOR = "creator"
    CAREGIVER = "caregiver"
    MAGICIAN = "magician"
    JESTER = "jester"
    EVERYMAN = "everyman"
    DRAGON = "dragon"  # Classic fantasy antagonist


class Alignment(str, Enum):
    """
    D&D-style alignment system for character moral compass.
    
    Helps determine how a character approaches moral dilemmas
    and interacts with rules and authority.
    """
    LAWFUL_GOOD = "lawful_good"
    NEUTRAL_GOOD = "neutral_good"
    CHAOTIC_GOOD = "chaotic_good"
    LAWFUL_NEUTRAL = "lawful_neutral"
    TRUE_NEUTRAL = "true_neutral"
    CHAOTIC_NEUTRAL = "chaotic_neutral"
    LAWFUL_EVIL = "lawful_evil"
    NEUTRAL_EVIL = "neutral_evil"
    CHAOTIC_EVIL = "chaotic_evil"


class PersonalityTrait(BaseModel):
    """
    A single personality trait with intensity.
    
    Attributes:
        name: Name of the trait (e.g., "wise", "courageous")
        intensity: How strongly this trait manifests (0.0 to 1.0)
        description: Brief description of how this trait manifests
        triggers: Situations that activate this trait
    """
    name: str = Field(..., min_length=1, max_length=50)
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    description: str = Field(default="")
    triggers: list[str] = Field(default_factory=list)
    
    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, v: float) -> float:
        """Ensure intensity is within valid range."""
        return max(0.0, min(1.0, v))


class CoreValue(BaseModel):
    """
    A fundamental value that guides character decisions.
    
    Attributes:
        name: Name of the value (e.g., "honor", "freedom")
        priority: How important this value is (1 = highest)
        description: What this value means to the character
        conflicts_with: Values that may conflict with this one
    """
    name: str = Field(..., min_length=1, max_length=50)
    priority: int = Field(default=1, ge=1, le=10)
    description: str = Field(default="")
    conflicts_with: list[str] = Field(default_factory=list)


class SpeakingStyle(BaseModel):
    """
    Defines how the character speaks.
    
    Attributes:
        formality: Level of formal speech (0 = very casual, 1 = very formal)
        verbosity: How much the character talks (0 = terse, 1 = verbose)
        vocabulary_level: Complexity of vocabulary (0 = simple, 1 = complex)
        common_phrases: Phrases the character often uses
        speech_patterns: Unique speech patterns or quirks
        languages: Languages the character speaks
        accent_notes: Notes about accent or dialect
    """
    formality: float = Field(default=0.5, ge=0.0, le=1.0)
    verbosity: float = Field(default=0.5, ge=0.0, le=1.0)
    vocabulary_level: float = Field(default=0.5, ge=0.0, le=1.0)
    common_phrases: list[str] = Field(default_factory=list)
    speech_patterns: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=lambda: ["Common"])
    accent_notes: str = Field(default="")


class BackgroundInfo(BaseModel):
    """
    Character background and history.
    
    Attributes:
        origin: Place of origin
        race: Character's race/species
        age: Character's age (can be descriptive)
        occupation: Current or primary occupation
        brief_history: Short history summary
        significant_events: Key events in character's life
        secrets: Hidden information about the character
    """
    origin: str = Field(default="Unknown")
    race: str = Field(default="Human")
    age: str = Field(default="Unknown")
    occupation: str = Field(default="Adventurer")
    brief_history: str = Field(default="")
    significant_events: list[str] = Field(default_factory=list)
    secrets: list[str] = Field(default_factory=list)


class PersonalityCore(BaseModel):
    """
    The immutable core of a character's personality.
    
    This class defines everything that makes a character who they are
    at their most fundamental level. These attributes should not change
    during interactions - they are the character's "soul".
    
    Attributes:
        character_id: Unique identifier for the character
        name: Character's full name
        display_name: Name to show in UI
        primary_archetype: Main character archetype
        secondary_archetypes: Additional archetypal influences
        alignment: Moral alignment
        traits: List of personality traits
        values: Core values that guide decisions
        speaking_style: How the character communicates
        background: Character history and background
        motivations: What drives the character
        fears: What the character fears
        strengths: Character's strengths
        weaknesses: Character's weaknesses
        quirks: Unique behavioral quirks
        canonical_source: Original source material
        
    Example:
        >>> gandalf = PersonalityCore(
        ...     character_id="gandalf_grey",
        ...     name="Gandalf the Grey",
        ...     primary_archetype=Archetype.MENTOR,
        ...     alignment=Alignment.NEUTRAL_GOOD,
        ... )
    """
    
    character_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    display_name: str = Field(default="")
    
    # Archetypes
    primary_archetype: Archetype = Field(default=Archetype.HERO)
    secondary_archetypes: list[Archetype] = Field(default_factory=list)
    
    # Moral framework
    alignment: Alignment = Field(default=Alignment.TRUE_NEUTRAL)
    
    # Personality composition
    traits: list[PersonalityTrait] = Field(default_factory=list)
    values: list[CoreValue] = Field(default_factory=list)
    
    # Communication
    speaking_style: SpeakingStyle = Field(default_factory=SpeakingStyle)
    
    # Background
    background: BackgroundInfo = Field(default_factory=BackgroundInfo)
    
    # Motivations and conflicts
    motivations: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    quirks: list[str] = Field(default_factory=list)
    
    # Source tracking
    canonical_source: str = Field(default="Original")
    source_materials: list[str] = Field(default_factory=list)
    
    def model_post_init(self, __context: Any) -> None:
        """Set display name if not provided."""
        if not self.display_name:
            self.display_name = self.name.split()[0] if self.name else self.character_id
    
    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        """
        Load personality from a YAML file.
        
        Args:
            path: Path to the YAML file
            
        Returns:
            PersonalityCore instance
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValidationError: If the YAML content is invalid
            
        Example:
            >>> gandalf = PersonalityCore.from_yaml("data/characters/gandalf/personality.yaml")
        """
        path = Path(path)
        logger.info("Loading personality from YAML", path=str(path))
        
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    def to_yaml(self, path: str | Path) -> None:
        """
        Save personality to a YAML file.
        
        Args:
            path: Path to save the YAML file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, allow_unicode=True)
        
        logger.info("Saved personality to YAML", path=str(path))
    
    def get_dominant_traits(self, top_n: int = 3) -> list[PersonalityTrait]:
        """
        Get the most dominant personality traits.
        
        Args:
            top_n: Number of traits to return
            
        Returns:
            List of traits sorted by intensity
        """
        return sorted(self.traits, key=lambda t: t.intensity, reverse=True)[:top_n]
    
    def get_primary_values(self, top_n: int = 3) -> list[CoreValue]:
        """
        Get the most important values.
        
        Args:
            top_n: Number of values to return
            
        Returns:
            List of values sorted by priority
        """
        return sorted(self.values, key=lambda v: v.priority)[:top_n]
    
    def generate_personality_prompt(self) -> str:
        """
        Generate a prompt section describing this personality.
        
        Returns:
            A formatted string describing the character's personality
            for use in LLM prompts.
        """
        dominant_traits = self.get_dominant_traits()
        primary_values = self.get_primary_values()
        
        prompt_parts = [
            f"# Character: {self.name}",
            f"\n## Core Identity",
            f"- **Archetype**: {self.primary_archetype.value.replace('_', ' ').title()}",
            f"- **Alignment**: {self.alignment.value.replace('_', ' ').title()}",
            f"- **Origin**: {self.background.origin}",
            f"- **Race**: {self.background.race}",
        ]
        
        if dominant_traits:
            prompt_parts.append("\n## Dominant Traits")
            for trait in dominant_traits:
                prompt_parts.append(f"- **{trait.name.title()}** (intensity: {trait.intensity:.1f}): {trait.description}")
        
        if primary_values:
            prompt_parts.append("\n## Core Values")
            for value in primary_values:
                prompt_parts.append(f"- **{value.name.title()}**: {value.description}")
        
        if self.motivations:
            prompt_parts.append("\n## Motivations")
            for motivation in self.motivations:
                prompt_parts.append(f"- {motivation}")
        
        if self.speaking_style.common_phrases:
            prompt_parts.append("\n## Speech Patterns")
            prompt_parts.append(f"- Formality: {'Formal' if self.speaking_style.formality > 0.5 else 'Casual'}")
            prompt_parts.append(f"- Common phrases: {', '.join(self.speaking_style.common_phrases[:5])}")
        
        return "\n".join(prompt_parts)
    
    def is_compatible_with(self, action: str, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Check if an action is compatible with this personality.
        
        Args:
            action: The action to evaluate
            context: Additional context for evaluation
            
        Returns:
            Tuple of (is_compatible, reason)
            
        Note:
            This is a basic check. Use ConsistencyChecker for
            more thorough validation.
        """
        # TODO: Implement more sophisticated compatibility checking
        # For now, return True with a placeholder message
        return True, "Action is potentially compatible with character personality"
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.name} ({self.primary_archetype.value})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"PersonalityCore(id={self.character_id!r}, "
            f"name={self.name!r}, "
            f"archetype={self.primary_archetype.value})"
        )
