"""
Tests for Character Template and State.
"""

import pytest
from src.core.character.character_template import (
    CharacterTemplate,
    PersonalityTraits,
    EmotionalProfile,
    SpeechPattern,
    CharacterBackground,
    CharacterGoal,
    CharacterRelationship
)
from src.core.character.character_state import CharacterState


class TestPersonalityTraits:
    """Tests for PersonalityTraits dataclass."""
    
    def test_create_personality_traits(self):
        """Test creating personality traits."""
        traits = PersonalityTraits(
            openness=0.7,
            conscientiousness=0.8,
            extraversion=0.5,
            agreeableness=0.6,
            neuroticism=0.3,
            dominant_traits=["brave", "wise"],
            values=["honor", "truth"],
            fears=["failure"]
        )
        
        assert traits.openness == 0.7
        assert traits.conscientiousness == 0.8
        assert "brave" in traits.dominant_traits
        assert "honor" in traits.values
    
    def test_traits_validation(self):
        """Test that traits accept valid values."""
        # Valid values
        traits = PersonalityTraits(
            openness=0.0,
            conscientiousness=1.0,
            extraversion=0.5,
            agreeableness=0.5,
            neuroticism=0.5
        )
        
        assert 0.0 <= traits.openness <= 1.0
        assert 0.0 <= traits.conscientiousness <= 1.0


class TestEmotionalProfile:
    """Tests for EmotionalProfile dataclass."""
    
    def test_create_emotional_profile(self):
        """Test creating an emotional profile."""
        profile = EmotionalProfile(
            default_mood="calm",
            mood_volatility=0.3,
            joy_triggers=["success", "friendship"],
            anger_triggers=["injustice"],
            sadness_triggers=["loss"],
            fear_triggers=["darkness"]
        )
        
        assert profile.default_mood == "calm"
        assert profile.mood_volatility == 0.3
        assert "success" in profile.joy_triggers
    
    def test_default_values(self):
        """Test default values for emotional profile."""
        profile = EmotionalProfile()
        
        assert profile.default_mood == "neutral"
        assert profile.mood_volatility == 0.5
        assert profile.joy_triggers == []


class TestSpeechPattern:
    """Tests for SpeechPattern dataclass."""
    
    def test_create_speech_pattern(self):
        """Test creating a speech pattern."""
        pattern = SpeechPattern(
            formality=0.8,
            verbosity=0.6,
            complexity=0.7,
            warmth=0.5,
            catchphrases=["Indeed!", "Most certainly."],
            vocabulary_preferences=["precisely", "therefore"],
            avoided_words=["like", "um"],
            style_notes=["Uses formal address"]
        )
        
        assert pattern.formality == 0.8
        assert "Indeed!" in pattern.catchphrases


class TestCharacterBackground:
    """Tests for CharacterBackground dataclass."""
    
    def test_create_background(self):
        """Test creating character background."""
        background = CharacterBackground(
            origin="The Northern Lands",
            history="A long and storied history...",
            key_events=["The Great War", "Finding the Artifact"],
            secrets=["Hidden lineage"],
            world_knowledge=["History", "Magic"]
        )
        
        assert background.origin == "The Northern Lands"
        assert len(background.key_events) == 2


class TestCharacterTemplate:
    """Tests for CharacterTemplate class."""
    
    def test_create_character_template(self, sample_character_template):
        """Test creating a character template."""
        template = sample_character_template
        
        assert template.id == "test-character"
        assert template.name == "Test Character"
        assert template.archetype == "hero"
        assert template.personality.openness == 0.7
    
    def test_template_to_dict(self, sample_character_template):
        """Test converting template to dictionary."""
        template = sample_character_template
        data = template.to_dict()
        
        assert data["id"] == "test-character"
        assert "personality" in data
        assert "speech_pattern" in data
    
    def test_template_from_dict(self, sample_character_template):
        """Test creating template from dictionary."""
        original = sample_character_template
        data = original.to_dict()
        
        # Verify dict has expected structure
        assert "id" in data
        assert "name" in data


class TestCharacterState:
    """Tests for CharacterState class."""
    
    def test_create_character_state(self, sample_character_state):
        """Test creating character state."""
        state = sample_character_state
        
        assert state.character_id == "test-character"
        assert state.current_mood == "determined"
        assert state.energy_level == 0.8
    
    def test_update_mood(self, sample_character_state):
        """Test updating character mood."""
        state = sample_character_state
        
        state.update_mood("happy", intensity=0.8)
        
        assert state.current_mood == "happy"
        assert state.mood_intensity == 0.8
        assert "happy" in state.recent_emotions
    
    def test_mood_decay(self, sample_character_state):
        """Test mood decay over time."""
        state = sample_character_state
        initial_intensity = state.mood_intensity
        
        state.decay_mood(0.1)
        
        assert state.mood_intensity < initial_intensity
    
    def test_energy_management(self, sample_character_state):
        """Test energy level management."""
        state = sample_character_state
        
        state.consume_energy(0.2)
        assert state.energy_level == 0.6
        
        state.restore_energy(0.1)
        assert state.energy_level == 0.7
    
    def test_energy_bounds(self, sample_character_state):
        """Test that energy stays within bounds."""
        state = sample_character_state
        
        state.restore_energy(10.0)  # Try to exceed max
        assert state.energy_level <= 1.0
        
        state.consume_energy(10.0)  # Try to go negative
        assert state.energy_level >= 0.0
    
    def test_add_recent_emotion(self, sample_character_state):
        """Test adding recent emotions."""
        state = sample_character_state
        
        state.add_recent_emotion("joy")
        state.add_recent_emotion("excitement")
        
        assert "joy" in state.recent_emotions
        assert "excitement" in state.recent_emotions
    
    def test_recent_emotions_limit(self, sample_character_state):
        """Test that recent emotions are limited."""
        state = sample_character_state
        state.recent_emotions = []
        
        # Add many emotions
        for i in range(20):
            state.add_recent_emotion(f"emotion_{i}")
        
        # Should be limited (typically to 10)
        assert len(state.recent_emotions) <= 10
    
    def test_context_awareness(self, sample_character_state):
        """Test context awareness updates."""
        state = sample_character_state
        
        state.update_context("weather", "stormy")
        
        assert state.context_awareness.get("weather") == "stormy"
    
    def test_get_state_summary(self, sample_character_state):
        """Test getting state summary."""
        state = sample_character_state
        
        summary = state.get_summary()
        
        assert "mood" in summary
        assert "energy" in summary
        assert summary["character_id"] == "test-character"
