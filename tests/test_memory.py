"""
Tests for Memory Systems (Episodic and Semantic).
"""

import pytest
from datetime import datetime
from src.core.memory.episodic_memory import (
    EpisodicMemory,
    Episode,
    MemoryImportance
)
from src.core.memory.semantic_memory import (
    SemanticMemory,
    SemanticFact,
    FactCategory
)


class TestEpisode:
    """Tests for Episode dataclass."""
    
    def test_create_episode(self):
        """Test creating an episode."""
        episode = Episode(
            id="ep-001",
            character_id="test-char",
            content="A memorable conversation occurred.",
            context={"location": "tavern", "time": "evening"},
            emotional_valence=0.7,
            importance=MemoryImportance.SIGNIFICANT,
            participants=["user", "test-char"],
            timestamp=datetime.now()
        )
        
        assert episode.id == "ep-001"
        assert episode.emotional_valence == 0.7
        assert "user" in episode.participants
    
    def test_episode_to_dict(self):
        """Test converting episode to dictionary."""
        episode = Episode(
            id="ep-001",
            character_id="test-char",
            content="Test content",
            context={},
            emotional_valence=0.5,
            importance=MemoryImportance.MODERATE
        )
        
        data = episode.to_dict()
        
        assert data["id"] == "ep-001"
        assert "timestamp" in data


class TestEpisodicMemory:
    """Tests for EpisodicMemory class."""
    
    def test_create_episodic_memory(self):
        """Test creating episodic memory system."""
        memory = EpisodicMemory(
            character_id="test-char",
            max_episodes=100
        )
        
        assert memory.character_id == "test-char"
        assert memory.max_episodes == 100
    
    @pytest.mark.asyncio
    async def test_store_episode(self):
        """Test storing an episode."""
        memory = EpisodicMemory(character_id="test-char")
        
        episode_id = await memory.store(
            content="We discussed the weather.",
            context={"location": "garden"},
            emotional_valence=0.3,
            importance=MemoryImportance.TRIVIAL
        )
        
        assert episode_id is not None
        assert len(memory.episodes) == 1
    
    @pytest.mark.asyncio
    async def test_retrieve_recent(self):
        """Test retrieving recent episodes."""
        memory = EpisodicMemory(character_id="test-char")
        
        # Store several episodes
        for i in range(5):
            await memory.store(
                content=f"Episode {i}",
                context={},
                emotional_valence=0.5,
                importance=MemoryImportance.MODERATE
            )
        
        recent = await memory.retrieve_recent(3)
        
        assert len(recent) == 3
        # Most recent should be last stored
        assert "Episode 4" in recent[0].content
    
    @pytest.mark.asyncio
    async def test_retrieve_by_context(self):
        """Test retrieving episodes by context."""
        memory = EpisodicMemory(character_id="test-char")
        
        await memory.store(
            content="At the tavern",
            context={"location": "tavern"},
            emotional_valence=0.5,
            importance=MemoryImportance.MODERATE
        )
        
        await memory.store(
            content="At the castle",
            context={"location": "castle"},
            emotional_valence=0.5,
            importance=MemoryImportance.MODERATE
        )
        
        tavern_episodes = await memory.retrieve_by_context({"location": "tavern"})
        
        assert len(tavern_episodes) == 1
        assert "tavern" in tavern_episodes[0].content
    
    @pytest.mark.asyncio
    async def test_memory_consolidation(self):
        """Test that old memories are consolidated."""
        memory = EpisodicMemory(character_id="test-char", max_episodes=3)
        
        # Store more than max
        for i in range(5):
            await memory.store(
                content=f"Episode {i}",
                context={},
                emotional_valence=0.5,
                importance=MemoryImportance.TRIVIAL
            )
        
        # Should have consolidated to max
        assert len(memory.episodes) <= 3
    
    @pytest.mark.asyncio
    async def test_important_memories_retained(self):
        """Test that important memories are retained during consolidation."""
        memory = EpisodicMemory(character_id="test-char", max_episodes=3)
        
        # Store one critical memory
        await memory.store(
            content="Critical event",
            context={},
            emotional_valence=0.9,
            importance=MemoryImportance.CRITICAL
        )
        
        # Store several trivial memories
        for i in range(5):
            await memory.store(
                content=f"Trivial {i}",
                context={},
                emotional_valence=0.1,
                importance=MemoryImportance.TRIVIAL
            )
        
        # Critical memory should be retained
        all_content = [ep.content for ep in memory.episodes]
        assert "Critical event" in all_content


class TestSemanticFact:
    """Tests for SemanticFact dataclass."""
    
    def test_create_semantic_fact(self):
        """Test creating a semantic fact."""
        fact = SemanticFact(
            id="fact-001",
            character_id="test-char",
            subject="Dragons",
            predicate="breathe",
            object="fire",
            category=FactCategory.WORLD_KNOWLEDGE,
            confidence=0.95,
            source="learned from mentor"
        )
        
        assert fact.subject == "Dragons"
        assert fact.confidence == 0.95
    
    def test_fact_as_statement(self):
        """Test converting fact to natural statement."""
        fact = SemanticFact(
            id="fact-001",
            character_id="test-char",
            subject="The king",
            predicate="lives in",
            object="the castle",
            category=FactCategory.WORLD_KNOWLEDGE,
            confidence=1.0
        )
        
        statement = fact.as_statement()
        
        assert "king" in statement
        assert "castle" in statement


class TestSemanticMemory:
    """Tests for SemanticMemory class."""
    
    def test_create_semantic_memory(self):
        """Test creating semantic memory system."""
        memory = SemanticMemory(character_id="test-char")
        
        assert memory.character_id == "test-char"
    
    @pytest.mark.asyncio
    async def test_store_fact(self):
        """Test storing a fact."""
        memory = SemanticMemory(character_id="test-char")
        
        fact_id = await memory.store(
            subject="Elves",
            predicate="live in",
            object="forests",
            category=FactCategory.WORLD_KNOWLEDGE,
            confidence=0.9
        )
        
        assert fact_id is not None
        assert len(memory.facts) == 1
    
    @pytest.mark.asyncio
    async def test_query_facts(self):
        """Test querying facts."""
        memory = SemanticMemory(character_id="test-char")
        
        await memory.store(
            subject="Dwarves",
            predicate="mine",
            object="gold",
            category=FactCategory.WORLD_KNOWLEDGE,
            confidence=0.9
        )
        
        await memory.store(
            subject="Dwarves",
            predicate="craft",
            object="weapons",
            category=FactCategory.WORLD_KNOWLEDGE,
            confidence=0.85
        )
        
        dwarf_facts = await memory.query(subject="Dwarves")
        
        assert len(dwarf_facts) == 2
    
    @pytest.mark.asyncio
    async def test_search_facts(self):
        """Test searching facts by text."""
        memory = SemanticMemory(character_id="test-char")
        
        await memory.store(
            subject="The Dark Lord",
            predicate="seeks",
            object="the ring",
            category=FactCategory.CHARACTER_KNOWLEDGE,
            confidence=1.0
        )
        
        results = await memory.search("ring")
        
        assert len(results) > 0
        assert "ring" in results[0].object
    
    @pytest.mark.asyncio
    async def test_update_confidence(self):
        """Test updating fact confidence."""
        memory = SemanticMemory(character_id="test-char")
        
        fact_id = await memory.store(
            subject="The treasure",
            predicate="is hidden in",
            object="the mountain",
            category=FactCategory.WORLD_KNOWLEDGE,
            confidence=0.5
        )
        
        await memory.update_confidence(fact_id, 0.9)
        
        fact = memory.get_fact(fact_id)
        assert fact.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_get_facts_by_category(self):
        """Test getting facts by category."""
        memory = SemanticMemory(character_id="test-char")
        
        await memory.store(
            subject="User",
            predicate="prefers",
            object="formal speech",
            category=FactCategory.USER_PREFERENCES,
            confidence=0.8
        )
        
        await memory.store(
            subject="Magic",
            predicate="requires",
            object="focus",
            category=FactCategory.WORLD_KNOWLEDGE,
            confidence=0.9
        )
        
        prefs = await memory.get_by_category(FactCategory.USER_PREFERENCES)
        
        assert len(prefs) == 1
        assert prefs[0].subject == "User"
