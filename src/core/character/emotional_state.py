"""
Emotional State - Dynamic emotional system for characters.

This module manages the emotional state of characters, including:
- Current emotional state
- Emotional transitions and triggers
- Emotional memory and patterns
- Emotion influence on responses

The emotional system is dynamic and changes based on interactions,
while still being anchored to the character's personality core.

Example:
    >>> from src.core.character import EmotionalState, Emotion
    >>> state = EmotionalState(character_id="gandalf")
    >>> state.apply_emotion(Emotion.JOY, intensity=0.7, trigger="seeing old friend")
    >>> print(state.dominant_emotion)
    Emotion.JOY
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from src.config.logging_config import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


class Emotion(str, Enum):
    """
    Primary emotions based on Plutchik's wheel of emotions.
    
    These are the core emotions that characters can experience.
    Complex emotions are combinations of these primaries.
    """
    # Primary emotions
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    
    # Secondary/Complex emotions
    LOVE = "love"  # joy + trust
    SUBMISSION = "submission"  # trust + fear
    AWE = "awe"  # fear + surprise
    DISAPPROVAL = "disapproval"  # surprise + sadness
    REMORSE = "remorse"  # sadness + disgust
    CONTEMPT = "contempt"  # disgust + anger
    AGGRESSIVENESS = "aggressiveness"  # anger + anticipation
    OPTIMISM = "optimism"  # anticipation + joy
    
    # Neutral state
    NEUTRAL = "neutral"
    
    # Fantasy-specific
    CURIOSITY = "curiosity"
    DETERMINATION = "determination"
    WEARINESS = "weariness"
    HOPE = "hope"
    DESPAIR = "despair"
    SERENITY = "serenity"


class EmotionInstance(BaseModel):
    """
    A specific emotional instance with context.
    
    Attributes:
        emotion: The emotion type
        intensity: How strongly the emotion is felt (0.0 to 1.0)
        trigger: What caused this emotion
        timestamp: When this emotion was triggered
        decay_rate: How quickly this emotion fades
        source: Source of the trigger (user, world, memory, etc.)
    """
    emotion: Emotion = Field(...)
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    trigger: str = Field(default="")
    timestamp: datetime = Field(default_factory=datetime.now)
    decay_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    source: str = Field(default="interaction")
    
    @field_validator("intensity")
    @classmethod
    def clamp_intensity(cls, v: float) -> float:
        """Ensure intensity stays within bounds."""
        return max(0.0, min(1.0, v))
    
    def decay(self, elapsed_seconds: float) -> "EmotionInstance":
        """
        Apply time-based decay to emotion intensity.
        
        Args:
            elapsed_seconds: Time elapsed since last update
            
        Returns:
            New EmotionInstance with decayed intensity
        """
        decay_factor = self.decay_rate * (elapsed_seconds / 60.0)  # Decay per minute
        new_intensity = max(0.0, self.intensity - decay_factor)
        
        return EmotionInstance(
            emotion=self.emotion,
            intensity=new_intensity,
            trigger=self.trigger,
            timestamp=self.timestamp,
            decay_rate=self.decay_rate,
            source=self.source,
        )
    
    @property
    def is_active(self) -> bool:
        """Check if emotion is still significantly active."""
        return self.intensity > 0.1


class EmotionalMemory(BaseModel):
    """
    Record of emotional experiences for pattern recognition.
    
    Tracks emotional history to detect patterns and inform
    future emotional responses.
    """
    trigger_patterns: dict[str, list[Emotion]] = Field(default_factory=dict)
    emotion_frequency: dict[str, int] = Field(default_factory=dict)
    recent_emotions: list[EmotionInstance] = Field(default_factory=list)
    max_recent: int = Field(default=100)
    
    def record(self, instance: EmotionInstance) -> None:
        """Record an emotional experience."""
        # Track trigger patterns
        if instance.trigger:
            trigger_key = instance.trigger.lower()[:50]
            if trigger_key not in self.trigger_patterns:
                self.trigger_patterns[trigger_key] = []
            self.trigger_patterns[trigger_key].append(instance.emotion)
        
        # Track frequency
        emotion_key = instance.emotion.value
        self.emotion_frequency[emotion_key] = self.emotion_frequency.get(emotion_key, 0) + 1
        
        # Add to recent
        self.recent_emotions.append(instance)
        if len(self.recent_emotions) > self.max_recent:
            self.recent_emotions = self.recent_emotions[-self.max_recent:]
    
    def get_common_response(self, trigger: str) -> Optional[Emotion]:
        """Get the most common emotional response to a trigger."""
        trigger_key = trigger.lower()[:50]
        if trigger_key in self.trigger_patterns:
            emotions = self.trigger_patterns[trigger_key]
            if emotions:
                # Return most common emotion for this trigger
                emotion_counts: dict[Emotion, int] = {}
                for e in emotions:
                    emotion_counts[e] = emotion_counts.get(e, 0) + 1
                return max(emotion_counts, key=emotion_counts.get)
        return None


class EmotionalState(BaseModel):
    """
    The dynamic emotional state of a character.
    
    Manages current emotions, emotional transitions, and provides
    emotional context for character responses.
    
    Attributes:
        character_id: ID of the character this state belongs to
        active_emotions: Currently active emotions
        baseline_mood: Default mood when no emotions are active
        emotional_stability: How quickly emotions change (0=volatile, 1=stable)
        emotional_memory: History of emotional experiences
        last_update: When the state was last updated
        
    Example:
        >>> state = EmotionalState(character_id="gandalf")
        >>> state.apply_emotion(Emotion.ANGER, intensity=0.8, trigger="Balrog appears")
        >>> response_modifier = state.get_response_modifier()
    """
    
    character_id: str = Field(...)
    active_emotions: dict[Emotion, EmotionInstance] = Field(default_factory=dict)
    baseline_mood: Emotion = Field(default=Emotion.NEUTRAL)
    baseline_intensity: float = Field(default=0.3, ge=0.0, le=1.0)
    emotional_stability: float = Field(default=0.5, ge=0.0, le=1.0)
    emotional_memory: EmotionalMemory = Field(default_factory=EmotionalMemory)
    last_update: datetime = Field(default_factory=datetime.now)
    
    def apply_emotion(
        self,
        emotion: Emotion,
        intensity: float = 0.5,
        trigger: str = "",
        source: str = "interaction",
    ) -> None:
        """
        Apply an emotion to the character's state.
        
        The emotion is added to active emotions, potentially
        modifying existing emotions of the same type.
        
        Args:
            emotion: The emotion to apply
            intensity: How strongly to apply it (0.0 to 1.0)
            trigger: What caused this emotion
            source: Source of the trigger
        """
        settings = get_settings()
        
        # Adjust intensity based on emotional stability
        adjusted_intensity = intensity * (1.0 - self.emotional_stability * 0.5)
        adjusted_intensity = max(0.0, min(1.0, adjusted_intensity))
        
        # If emotion already exists, blend intensities
        if emotion in self.active_emotions:
            existing = self.active_emotions[emotion]
            blended_intensity = (existing.intensity + adjusted_intensity) / 2
            adjusted_intensity = max(existing.intensity, blended_intensity)
        
        # Create emotion instance
        instance = EmotionInstance(
            emotion=emotion,
            intensity=adjusted_intensity,
            trigger=trigger,
            timestamp=datetime.now(),
            decay_rate=settings.emotion_decay_rate,
            source=source,
        )
        
        # Store and record
        self.active_emotions[emotion] = instance
        self.emotional_memory.record(instance)
        
        logger.debug(
            "Applied emotion",
            character_id=self.character_id,
            emotion=emotion.value,
            intensity=adjusted_intensity,
            trigger=trigger,
        )
    
    def update(self) -> None:
        """
        Update emotional state with time-based decay.
        
        Should be called periodically to allow emotions to
        naturally decay over time.
        """
        now = datetime.now()
        elapsed = (now - self.last_update).total_seconds()
        
        # Decay all active emotions
        updated_emotions: dict[Emotion, EmotionInstance] = {}
        for emotion, instance in self.active_emotions.items():
            decayed = instance.decay(elapsed)
            if decayed.is_active:
                updated_emotions[emotion] = decayed
        
        self.active_emotions = updated_emotions
        self.last_update = now
    
    @property
    def dominant_emotion(self) -> Emotion:
        """
        Get the currently dominant emotion.
        
        Returns:
            The emotion with the highest intensity, or baseline mood
        """
        self.update()
        
        if not self.active_emotions:
            return self.baseline_mood
        
        return max(
            self.active_emotions.keys(),
            key=lambda e: self.active_emotions[e].intensity
        )
    
    @property
    def dominant_intensity(self) -> float:
        """Get the intensity of the dominant emotion."""
        self.update()
        
        if not self.active_emotions:
            return self.baseline_intensity
        
        dominant = self.dominant_emotion
        return self.active_emotions[dominant].intensity
    
    def get_emotional_summary(self) -> dict[str, Any]:
        """
        Get a summary of the current emotional state.
        
        Returns:
            Dictionary with emotional state information
        """
        self.update()
        
        return {
            "dominant_emotion": self.dominant_emotion.value,
            "dominant_intensity": self.dominant_intensity,
            "active_emotions": {
                e.value: inst.intensity
                for e, inst in self.active_emotions.items()
            },
            "baseline_mood": self.baseline_mood.value,
            "stability": self.emotional_stability,
        }
    
    def get_response_modifier(self) -> dict[str, Any]:
        """
        Get modifiers for response generation based on emotional state.
        
        Returns:
            Dictionary of modifiers to apply to LLM generation
        """
        self.update()
        settings = get_settings()
        
        dominant = self.dominant_emotion
        intensity = self.dominant_intensity
        influence = settings.emotion_influence_factor
        
        # Map emotions to response characteristics
        emotion_effects: dict[Emotion, dict[str, Any]] = {
            Emotion.JOY: {"tone": "warm", "energy": "high", "openness": "high"},
            Emotion.SADNESS: {"tone": "melancholic", "energy": "low", "openness": "medium"},
            Emotion.ANGER: {"tone": "sharp", "energy": "high", "openness": "low"},
            Emotion.FEAR: {"tone": "cautious", "energy": "medium", "openness": "low"},
            Emotion.SURPRISE: {"tone": "curious", "energy": "high", "openness": "high"},
            Emotion.DISGUST: {"tone": "dismissive", "energy": "medium", "openness": "low"},
            Emotion.TRUST: {"tone": "open", "energy": "medium", "openness": "high"},
            Emotion.ANTICIPATION: {"tone": "eager", "energy": "high", "openness": "medium"},
            Emotion.NEUTRAL: {"tone": "neutral", "energy": "medium", "openness": "medium"},
            Emotion.DETERMINATION: {"tone": "resolute", "energy": "high", "openness": "medium"},
            Emotion.WEARINESS: {"tone": "tired", "energy": "low", "openness": "low"},
            Emotion.HOPE: {"tone": "optimistic", "energy": "medium", "openness": "high"},
            Emotion.DESPAIR: {"tone": "hopeless", "energy": "low", "openness": "low"},
        }
        
        effects = emotion_effects.get(
            dominant,
            {"tone": "neutral", "energy": "medium", "openness": "medium"}
        )
        
        return {
            "dominant_emotion": dominant.value,
            "intensity": intensity,
            "influence_factor": influence,
            "effects": effects,
            "should_acknowledge": intensity > 0.6,  # High emotion should be acknowledged
        }
    
    def generate_emotion_prompt_section(self) -> str:
        """
        Generate a prompt section describing current emotional state.
        
        Returns:
            Formatted string for LLM prompt
        """
        summary = self.get_emotional_summary()
        
        lines = [
            "\n## Current Emotional State",
            f"- **Primary Emotion**: {summary['dominant_emotion'].replace('_', ' ').title()}",
            f"- **Intensity**: {summary['dominant_intensity']:.1%}",
        ]
        
        if len(summary["active_emotions"]) > 1:
            other_emotions = [
                f"{e.replace('_', ' ').title()} ({i:.0%})"
                for e, i in summary["active_emotions"].items()
                if e != summary["dominant_emotion"] and i > 0.2
            ]
            if other_emotions:
                lines.append(f"- **Also feeling**: {', '.join(other_emotions)}")
        
        return "\n".join(lines)
    
    def reset(self) -> None:
        """Reset emotional state to baseline."""
        self.active_emotions = {}
        self.last_update = datetime.now()
        logger.info("Reset emotional state", character_id=self.character_id)
    
    def __str__(self) -> str:
        """String representation."""
        return f"EmotionalState({self.character_id}: {self.dominant_emotion.value} @ {self.dominant_intensity:.0%})"
