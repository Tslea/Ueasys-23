"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock, AsyncMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider."""
    from src.llm.base_provider import LLMResponse
    
    provider = MagicMock()
    provider.generate = AsyncMock(return_value=LLMResponse(
        content="This is a mock response from the LLM.",
        model="mock-model",
        finish_reason="stop",
        usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        metadata={}
    ))
    provider.generate_stream = AsyncMock()
    return provider


@pytest.fixture
def sample_character_template():
    """Create a sample character template for testing."""
    from src.core.character.character_template import (
        CharacterTemplate,
        PersonalityTraits,
        EmotionalProfile,
        SpeechPattern,
        CharacterBackground,
        CharacterGoal,
        CharacterRelationship
    )
    
    return CharacterTemplate(
        id="test-character",
        name="Test Character",
        full_name="Test Character the Brave",
        description="A test character for unit testing purposes.",
        archetype="hero",
        personality=PersonalityTraits(
            openness=0.7,
            conscientiousness=0.8,
            extraversion=0.6,
            agreeableness=0.75,
            neuroticism=0.3,
            dominant_traits=["brave", "honest", "loyal"],
            values=["justice", "honor"],
            fears=["failure", "betrayal"]
        ),
        emotional_profile=EmotionalProfile(
            default_mood="determined",
            mood_volatility=0.3,
            joy_triggers=["victory", "friendship"],
            anger_triggers=["injustice", "betrayal"],
            sadness_triggers=["loss", "failure"],
            fear_triggers=["darkness", "isolation"]
        ),
        speech_pattern=SpeechPattern(
            formality=0.6,
            verbosity=0.5,
            complexity=0.5,
            warmth=0.7,
            catchphrases=["For honor!", "Stand with me!"],
            vocabulary_preferences=["brave", "honor", "truth"],
            avoided_words=["coward", "retreat"],
            style_notes=["speaks directly", "uses metaphors"]
        ),
        background=CharacterBackground(
            origin="The Northern Kingdoms",
            history="Born a simple farmer, rose to become a hero.",
            key_events=["The great battle", "Meeting the mentor"],
            secrets=["Has a hidden past"],
            world_knowledge=["Northern customs", "Battle tactics"]
        ),
        goals=[
            CharacterGoal(
                description="Protect the innocent",
                priority=1.0,
                goal_type="duty",
                progress=0.0
            )
        ],
        relationships=[
            CharacterRelationship(
                character_id="mentor",
                character_name="The Mentor",
                relationship_type="teacher",
                strength=0.9,
                description="Wise teacher and guide"
            )
        ]
    )


@pytest.fixture
def sample_character_state():
    """Create a sample character state for testing."""
    from src.core.character.character_state import CharacterState
    
    return CharacterState(
        character_id="test-character",
        current_mood="determined",
        mood_intensity=0.6,
        energy_level=0.8,
        social_disposition=0.7,
        active_goals=["protect_the_innocent"],
        recent_emotions=["determination", "hope"],
        context_awareness={"location": "castle", "time": "morning"},
        conversation_history=[]
    )


@pytest.fixture
def sample_conversation_context():
    """Create a sample conversation context."""
    return {
        "session_id": "test-session-123",
        "user_id": "test-user",
        "character_id": "test-character",
        "messages": [],
        "metadata": {}
    }


@pytest.fixture
def mock_rag_system():
    """Create a mock RAG system."""
    rag = MagicMock()
    rag.search = AsyncMock(return_value=[
        {
            "content": "Relevant knowledge chunk 1",
            "score": 0.9,
            "metadata": {"type": "character_knowledge"}
        },
        {
            "content": "Relevant knowledge chunk 2",
            "score": 0.8,
            "metadata": {"type": "world_lore"}
        }
    ])
    return rag


@pytest.fixture
def mock_memory_system():
    """Create a mock memory system."""
    from src.core.memory.episodic_memory import EpisodicMemory
    from src.core.memory.semantic_memory import SemanticMemory
    
    episodic = MagicMock(spec=EpisodicMemory)
    episodic.retrieve_recent = AsyncMock(return_value=[])
    episodic.store = AsyncMock()
    
    semantic = MagicMock(spec=SemanticMemory)
    semantic.search = AsyncMock(return_value=[])
    semantic.store = AsyncMock()
    
    return {"episodic": episodic, "semantic": semantic}
