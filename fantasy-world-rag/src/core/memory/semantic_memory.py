"""
Semantic Memory - General knowledge and facts.

This module manages semantic memories, which are general facts,
knowledge, and information that don't have specific temporal context.
These memories represent what the character knows about the world.

Example:
    >>> from src.core.memory import SemanticMemory
    >>> memory = SemanticMemory(character_id="gandalf")
    >>> await memory.store("The One Ring was forged by Sauron", category="lore")
    >>> facts = await memory.retrieve("ring", category="lore")
"""

from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.config.settings import get_settings

logger = get_logger(__name__)


class SemanticMemoryItem(BaseModel):
    """
    A single semantic memory (fact or knowledge).
    
    Attributes:
        memory_id: Unique identifier
        character_id: Character this knowledge belongs to
        content: The knowledge content
        category: Category of knowledge (lore, skill, relationship, etc.)
        confidence: Confidence in this knowledge (0.0 to 1.0)
        source: Where this knowledge came from
        related_concepts: Related knowledge items
        access_count: How often accessed
        tags: Searchable tags
    """
    memory_id: str = Field(default_factory=lambda: str(uuid4()))
    character_id: str
    content: str
    category: str = "general"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Optional[str] = None
    related_concepts: list[str] = Field(default_factory=list)
    access_count: int = Field(default=0)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    def mark_accessed(self) -> None:
        """Mark this knowledge as accessed."""
        self.access_count += 1


class SemanticMemory(LoggerMixin):
    """
    Semantic memory system for character knowledge.
    
    Manages factual knowledge and general information that the
    character knows, organized by categories.
    
    Attributes:
        character_id: Character this memory belongs to
        memories: Dictionary of all semantic memories
        max_memories: Maximum memories to keep
        
    Example:
        >>> memory = SemanticMemory(character_id="gandalf")
        >>> await memory.store("Mithrandir is another name for Gandalf", category="names")
        >>> results = await memory.retrieve("Mithrandir")
    """
    
    def __init__(
        self,
        character_id: str,
        max_memories: Optional[int] = None,
    ):
        """
        Initialize semantic memory system.
        
        Args:
            character_id: Character this memory belongs to
            max_memories: Maximum memories to keep
        """
        self.character_id = character_id
        self._settings = get_settings()
        self.max_memories = max_memories or self._settings.memory_max_semantic_items
        
        # In-memory storage (Phase 2 will use vector DB)
        self._memories: dict[str, SemanticMemoryItem] = {}
        
        # Category index for faster retrieval
        self._category_index: dict[str, set[str]] = {}
        
        self.logger.info(
            "Initialized SemanticMemory",
            character_id=character_id,
            max_memories=self.max_memories,
        )
    
    async def store(
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
        Store a new semantic memory (fact/knowledge).
        
        Args:
            content: Knowledge content
            category: Category (lore, skill, relationship, etc.)
            confidence: Confidence level (0.0 to 1.0)
            source: Source of knowledge
            related_concepts: Related knowledge items
            tags: Searchable tags
            **metadata: Additional metadata
            
        Returns:
            memory_id: ID of stored memory
        """
        memory = SemanticMemoryItem(
            character_id=self.character_id,
            content=content,
            category=category,
            confidence=confidence,
            source=source,
            related_concepts=related_concepts or [],
            tags=tags or [],
            metadata=metadata,
        )
        
        self._memories[memory.memory_id] = memory
        
        # Update category index
        if category not in self._category_index:
            self._category_index[category] = set()
        self._category_index[category].add(memory.memory_id)
        
        # Prune if necessary
        if len(self._memories) > self.max_memories:
            await self._prune_memories()
        
        self.logger.debug(
            "Stored semantic memory",
            character_id=self.character_id,
            memory_id=memory.memory_id,
            category=category,
        )
        
        return memory.memory_id
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        min_confidence: float = 0.0,
    ) -> list[SemanticMemoryItem]:
        """
        Retrieve relevant semantic memories.
        
        Args:
            query: Search query
            top_k: Number of results
            category: Filter by category
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of relevant knowledge items
        """
        query_lower = query.lower()
        
        # Determine which memories to search
        if category:
            memory_ids = self._category_index.get(category, set())
            candidates = [
                self._memories[mid] for mid in memory_ids
                if mid in self._memories
            ]
        else:
            candidates = list(self._memories.values())
        
        # Filter and score
        results = []
        for memory in candidates:
            if memory.confidence < min_confidence:
                continue
            
            if self._matches_query(memory, query_lower):
                # Simple scoring for MVP (Phase 2 will use embeddings)
                score = self._calculate_score(memory, query_lower)
                results.append((score, memory))
        
        # Sort and return top_k
        results.sort(key=lambda x: x[0], reverse=True)
        retrieved = [mem for _, mem in results[:top_k]]
        
        # Mark as accessed
        for memory in retrieved:
            memory.mark_accessed()
        
        self.logger.debug(
            "Retrieved semantic memories",
            character_id=self.character_id,
            query_length=len(query),
            results=len(retrieved),
        )
        
        return retrieved
    
    def _matches_query(self, memory: SemanticMemoryItem, query_lower: str) -> bool:
        """Check if memory matches query."""
        # Check content
        if query_lower in memory.content.lower():
            return True
        
        # Check tags
        for tag in memory.tags:
            if query_lower in tag.lower():
                return True
        
        # Check related concepts
        for concept in memory.related_concepts:
            if query_lower in concept.lower():
                return True
        
        return False
    
    def _calculate_score(self, memory: SemanticMemoryItem, query_lower: str) -> float:
        """Calculate relevance score for memory."""
        score = 0.0
        
        # Content match
        content_lower = memory.content.lower()
        if query_lower in content_lower:
            # Exact substring match
            score += 1.0
            # Bonus for early occurrence
            position = content_lower.find(query_lower)
            position_score = 1.0 - (position / len(content_lower))
            score += position_score * 0.5
        
        # Confidence boost
        score *= memory.confidence
        
        # Access frequency boost (popular knowledge)
        import math
        access_boost = math.log(memory.access_count + 1) / math.log(100)
        score += access_boost * 0.3
        
        return score
    
    async def _prune_memories(self) -> None:
        """Prune least relevant memories."""
        if len(self._memories) <= self.max_memories:
            return
        
        # Score all memories by access count and confidence
        scored = [
            (mem.access_count * mem.confidence, mem_id, mem)
            for mem_id, mem in self._memories.items()
        ]
        
        # Sort by score (lowest first)
        scored.sort(key=lambda x: x[0])
        
        # Remove lowest scoring
        to_remove = len(self._memories) - self.max_memories
        for i in range(to_remove):
            _, mem_id, mem = scored[i]
            del self._memories[mem_id]
            
            # Update category index
            if mem.category in self._category_index:
                self._category_index[mem.category].discard(mem_id)
        
        self.logger.info(
            "Pruned semantic memories",
            character_id=self.character_id,
            removed=to_remove,
            remaining=len(self._memories),
        )
    
    def get_by_category(self, category: str) -> list[SemanticMemoryItem]:
        """Get all memories in a category."""
        memory_ids = self._category_index.get(category, set())
        return [
            self._memories[mid] for mid in memory_ids
            if mid in self._memories
        ]
    
    def get_categories(self) -> list[str]:
        """Get all categories."""
        return list(self._category_index.keys())
    
    def get_by_id(self, memory_id: str) -> Optional[SemanticMemoryItem]:
        """Get a specific memory by ID."""
        return self._memories.get(memory_id)
    
    def get_all(self) -> list[SemanticMemoryItem]:
        """Get all memories."""
        return list(self._memories.values())
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary statistics."""
        if not self._memories:
            return {
                "total": 0,
                "character_id": self.character_id,
                "categories": 0,
            }
        
        memories = list(self._memories.values())
        return {
            "total": len(memories),
            "character_id": self.character_id,
            "categories": len(self._category_index),
            "avg_confidence": sum(m.confidence for m in memories) / len(memories),
            "most_accessed": max(m.access_count for m in memories) if memories else 0,
        }
    
    async def clear(self) -> None:
        """Clear all memories."""
        self._memories.clear()
        self._category_index.clear()
        self.logger.info("Cleared all semantic memories", character_id=self.character_id)
    
    def __len__(self) -> int:
        """Number of memories."""
        return len(self._memories)
