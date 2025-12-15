"""
Memory Manager - Unified memory orchestration.

This module provides a unified interface for managing both episodic
and semantic memory systems, handling storage, retrieval, and
consolidation of character memories.

Example:
    >>> from src.core.memory import MemoryManager
    >>> manager = MemoryManager(character_id="gandalf")
    >>> await manager.store_interaction("Met Frodo", importance=0.9)
    >>> memories = await manager.retrieve_relevant("Frodo")
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Union

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.config.settings import get_settings
from src.core.memory.episodic_memory import EpisodicMemory, EpisodeMemoryItem
from src.core.memory.semantic_memory import SemanticMemory, SemanticMemoryItem
from src.core.memory.memory_retrieval import MemoryRetriever, RetrievalStrategy

logger = get_logger(__name__)


class MemorySearchResult(BaseModel):
    """
    Combined result from memory search.
    
    Attributes:
        episodic: List of episodic memories found
        semantic: List of semantic memories found
        combined_score: Overall relevance score
        metadata: Additional search metadata
    """
    episodic: list[EpisodeMemoryItem] = Field(default_factory=list)
    semantic: list[SemanticMemoryItem] = Field(default_factory=list)
    combined_score: float = 0.0
    query: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    @property
    def total_count(self) -> int:
        """Total memories found."""
        return len(self.episodic) + len(self.semantic)
    
    @property
    def has_results(self) -> bool:
        """Check if any results found."""
        return self.total_count > 0
    
    def to_context_string(self, max_items: int = 5) -> str:
        """
        Convert memories to a context string for LLM.
        
        Args:
            max_items: Maximum items per memory type
            
        Returns:
            Formatted string for prompt inclusion
        """
        parts = []
        
        if self.episodic:
            parts.append("### Recent Experiences:")
            for mem in self.episodic[:max_items]:
                emotion_tag = f" [{mem.emotion}]" if mem.emotion else ""
                parts.append(f"- {mem.content}{emotion_tag}")
        
        if self.semantic:
            parts.append("\n### Relevant Knowledge:")
            for mem in self.semantic[:max_items]:
                parts.append(f"- {mem.content}")
        
        return "\n".join(parts) if parts else "No relevant memories found."


class MemoryManager(LoggerMixin):
    """
    Unified memory manager for character memory systems.
    
    Orchestrates episodic and semantic memory, providing a single
    interface for all memory operations including storage, retrieval,
    and consolidation.
    
    Attributes:
        character_id: Character this memory belongs to
        episodic: Episodic memory system
        semantic: Semantic memory system
        retriever: Advanced retrieval system
        
    Example:
        >>> manager = MemoryManager(character_id="gandalf")
        >>> await manager.store_interaction(
        ...     "Discussed the ring's danger with Frodo",
        ...     importance=0.9,
        ...     participants=["Frodo"]
        ... )
        >>> result = await manager.retrieve_relevant("ring danger")
    """
    
    def __init__(
        self,
        character_id: str,
        episodic: Optional[EpisodicMemory] = None,
        semantic: Optional[SemanticMemory] = None,
        retriever: Optional[MemoryRetriever] = None,
    ):
        """
        Initialize the memory manager.
        
        Args:
            character_id: Character this memory belongs to
            episodic: Episodic memory system (created if None)
            semantic: Semantic memory system (created if None)
            retriever: Memory retriever (created if None)
        """
        self.character_id = character_id
        self._settings = get_settings()
        
        # Initialize memory systems
        self.episodic = episodic or EpisodicMemory(character_id)
        self.semantic = semantic or SemanticMemory(character_id)
        self.retriever = retriever or MemoryRetriever(
            episodic=self.episodic,
            semantic=self.semantic,
        )
        
        # Consolidation tracking
        self._consolidation_threshold = self._settings.memory_consolidation_threshold
        self._interactions_since_consolidation = 0
        
        self.logger.info(
            "Initialized MemoryManager",
            character_id=character_id,
        )
    
    async def store(
        self,
        content: str,
        metadata: dict[str, Any],
    ) -> str:
        """
        Store a memory (protocol method for CharacterEngine).
        
        Args:
            content: Memory content
            metadata: Memory metadata
            
        Returns:
            memory_id: ID of stored memory
        """
        memory_type = metadata.get("type", "interaction")
        
        if memory_type == "knowledge":
            return await self.store_knowledge(
                content=content,
                category=metadata.get("category", "general"),
                confidence=metadata.get("confidence", 1.0),
                source=metadata.get("source"),
            )
        else:
            return await self.store_interaction(
                content=content,
                importance=metadata.get("importance", 0.5),
                emotion=metadata.get("emotion"),
                participants=metadata.get("participants", []),
                location=metadata.get("location"),
            )
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant memories (protocol method for CharacterEngine).
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of memory dictionaries
        """
        result = await self.retrieve_relevant(query, top_k=top_k)
        
        # Convert to dictionary format
        memories = []
        for mem in result.episodic:
            memories.append({
                "type": "episodic",
                "content": mem.content,
                "importance": mem.importance,
                "emotion": mem.emotion,
                "timestamp": mem.timestamp.isoformat(),
            })
        for mem in result.semantic:
            memories.append({
                "type": "semantic",
                "content": mem.content,
                "category": mem.category,
                "confidence": mem.confidence,
            })
        
        return memories
    
    async def store_interaction(
        self,
        content: str,
        importance: float = 0.5,
        emotion: Optional[str] = None,
        participants: Optional[list[str]] = None,
        location: Optional[str] = None,
        tags: Optional[list[str]] = None,
        **metadata: Any,
    ) -> str:
        """
        Store an interaction memory (episodic).
        
        Args:
            content: What happened
            importance: How important (0.0 to 1.0)
            emotion: Associated emotion
            participants: Who was involved
            location: Where it happened
            tags: Searchable tags
            **metadata: Additional data
            
        Returns:
            memory_id: ID of stored memory
        """
        memory_id = await self.episodic.store(
            content=content,
            importance=importance,
            emotion=emotion,
            participants=participants,
            location=location,
            tags=tags,
            **metadata,
        )
        
        # Check for consolidation
        self._interactions_since_consolidation += 1
        if self._interactions_since_consolidation >= self._consolidation_threshold:
            await self._run_consolidation()
        
        return memory_id
    
    async def store_knowledge(
        self,
        content: str,
        category: str = "general",
        confidence: float = 1.0,
        source: Optional[str] = None,
        related_concepts: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        **metadata: Any,
    ) -> str:
        """
        Store a knowledge fact (semantic).
        
        Args:
            content: The knowledge/fact
            category: Category of knowledge
            confidence: Confidence level
            source: Knowledge source
            related_concepts: Related concepts
            tags: Searchable tags
            **metadata: Additional data
            
        Returns:
            memory_id: ID of stored memory
        """
        return await self.semantic.store(
            content=content,
            category=category,
            confidence=confidence,
            source=source,
            related_concepts=related_concepts,
            tags=tags,
            **metadata,
        )
    
    async def retrieve_relevant(
        self,
        query: str,
        top_k: int = 5,
        strategy: RetrievalStrategy = RetrievalStrategy.BALANCED,
        include_episodic: bool = True,
        include_semantic: bool = True,
        time_window: Optional[timedelta] = None,
        category_filter: Optional[str] = None,
    ) -> MemorySearchResult:
        """
        Retrieve relevant memories using specified strategy.
        
        Args:
            query: Search query
            top_k: Number of results per type
            strategy: Retrieval strategy to use
            include_episodic: Include episodic memories
            include_semantic: Include semantic memories
            time_window: Time window for episodic memories
            category_filter: Category filter for semantic memories
            
        Returns:
            MemorySearchResult with all found memories
        """
        return await self.retriever.retrieve(
            query=query,
            top_k=top_k,
            strategy=strategy,
            include_episodic=include_episodic,
            include_semantic=include_semantic,
            time_window=time_window,
            category_filter=category_filter,
        )
    
    async def retrieve_by_emotion(
        self,
        emotion: str,
        top_k: int = 5,
    ) -> list[EpisodeMemoryItem]:
        """
        Retrieve memories associated with a specific emotion.
        
        Args:
            emotion: Emotion to filter by
            top_k: Number of results
            
        Returns:
            List of episodic memories with that emotion
        """
        return await self.episodic.retrieve(
            query="",
            top_k=top_k,
            emotion_filter=emotion,
        )
    
    async def retrieve_recent(
        self,
        hours: int = 24,
        top_k: int = 10,
    ) -> list[EpisodeMemoryItem]:
        """
        Retrieve recent memories.
        
        Args:
            hours: How many hours back to look
            top_k: Number of results
            
        Returns:
            List of recent episodic memories
        """
        return await self.episodic.retrieve(
            query="",
            top_k=top_k,
            time_window=timedelta(hours=hours),
        )
    
    async def retrieve_about_participant(
        self,
        participant: str,
        top_k: int = 5,
    ) -> MemorySearchResult:
        """
        Retrieve memories involving a specific participant.
        
        Args:
            participant: Name of participant
            top_k: Number of results
            
        Returns:
            MemorySearchResult with memories about participant
        """
        return await self.retrieve_relevant(
            query=participant,
            top_k=top_k,
            strategy=RetrievalStrategy.RELATIONSHIP_FOCUSED,
        )
    
    async def _run_consolidation(self) -> None:
        """
        Run memory consolidation process.
        
        Consolidates frequently accessed memories and extracts
        semantic knowledge from episodic memories.
        """
        self.logger.info(
            "Running memory consolidation",
            character_id=self.character_id,
        )
        
        # Get frequently accessed episodic memories
        all_episodic = self.episodic.get_all()
        
        for memory in all_episodic:
            if memory.should_consolidate():
                # Consolidate the memory
                await self.episodic.consolidate(memory.memory_id)
                
                # Extract knowledge if high importance
                if memory.importance > 0.7:
                    # Create semantic memory from episodic
                    await self.semantic.store(
                        content=f"Experience: {memory.content}",
                        category="experience_derived",
                        confidence=memory.importance,
                        source=f"episodic:{memory.memory_id}",
                        tags=memory.tags,
                    )
        
        self._interactions_since_consolidation = 0
        
        self.logger.info(
            "Memory consolidation complete",
            character_id=self.character_id,
        )
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of all memory systems."""
        return {
            "character_id": self.character_id,
            "episodic": self.episodic.get_summary(),
            "semantic": self.semantic.get_summary(),
            "interactions_since_consolidation": self._interactions_since_consolidation,
        }
    
    async def clear_all(self) -> None:
        """Clear all memories."""
        await self.episodic.clear()
        await self.semantic.clear()
        self._interactions_since_consolidation = 0
        self.logger.info("Cleared all memories", character_id=self.character_id)
    
    def __len__(self) -> int:
        """Total number of memories."""
        return len(self.episodic) + len(self.semantic)
