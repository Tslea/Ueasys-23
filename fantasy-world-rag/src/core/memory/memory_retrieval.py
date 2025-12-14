"""
Memory Retrieval - Advanced retrieval strategies for memories.

This module provides sophisticated retrieval strategies for combining
episodic and semantic memories effectively based on different contexts.

Example:
    >>> from src.core.memory import MemoryRetriever, RetrievalStrategy
    >>> retriever = MemoryRetriever(episodic=ep_mem, semantic=sem_mem)
    >>> result = await retriever.retrieve("ring", strategy=RetrievalStrategy.TEMPORAL)
"""

from datetime import timedelta
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.core.memory.episodic_memory import EpisodicMemory, EpisodeMemoryItem
from src.core.memory.semantic_memory import SemanticMemory, SemanticMemoryItem

logger = get_logger(__name__)


class RetrievalStrategy(str, Enum):
    """
    Strategies for memory retrieval.
    
    Different strategies prioritize different aspects of memory
    based on the context of the query.
    """
    BALANCED = "balanced"  # Equal weight to both types
    EPISODIC_HEAVY = "episodic_heavy"  # Prioritize experiences
    SEMANTIC_HEAVY = "semantic_heavy"  # Prioritize knowledge
    TEMPORAL = "temporal"  # Recent memories first
    EMOTIONAL = "emotional"  # Emotionally charged memories
    RELATIONSHIP_FOCUSED = "relationship_focused"  # Focus on people
    CONTEXTUAL = "contextual"  # Adapt based on query


class RetrievalConfig(BaseModel):
    """
    Configuration for a retrieval operation.
    
    Attributes:
        strategy: Retrieval strategy to use
        top_k: Number of results per memory type
        episodic_weight: Weight for episodic memories
        semantic_weight: Weight for semantic memories
        recency_boost: Boost for recent memories
        importance_threshold: Minimum importance
        confidence_threshold: Minimum confidence
    """
    strategy: RetrievalStrategy = RetrievalStrategy.BALANCED
    top_k: int = 5
    episodic_weight: float = 0.5
    semantic_weight: float = 0.5
    recency_boost: float = 0.2
    importance_threshold: float = 0.0
    confidence_threshold: float = 0.0


class MemoryRetriever(LoggerMixin):
    """
    Advanced memory retrieval system.
    
    Provides sophisticated retrieval strategies that combine
    episodic and semantic memories effectively.
    
    Attributes:
        episodic: Episodic memory system
        semantic: Semantic memory system
        
    Example:
        >>> retriever = MemoryRetriever(episodic=ep, semantic=sem)
        >>> result = await retriever.retrieve(
        ...     "Frodo's journey",
        ...     strategy=RetrievalStrategy.TEMPORAL
        ... )
    """
    
    def __init__(
        self,
        episodic: EpisodicMemory,
        semantic: SemanticMemory,
    ):
        """
        Initialize the retriever.
        
        Args:
            episodic: Episodic memory system
            semantic: Semantic memory system
        """
        self.episodic = episodic
        self.semantic = semantic
        
        # Strategy configurations
        self._strategy_configs = self._build_strategy_configs()
        
        self.logger.info("Initialized MemoryRetriever")
    
    def _build_strategy_configs(self) -> dict[RetrievalStrategy, RetrievalConfig]:
        """Build configuration for each strategy."""
        return {
            RetrievalStrategy.BALANCED: RetrievalConfig(
                strategy=RetrievalStrategy.BALANCED,
                episodic_weight=0.5,
                semantic_weight=0.5,
            ),
            RetrievalStrategy.EPISODIC_HEAVY: RetrievalConfig(
                strategy=RetrievalStrategy.EPISODIC_HEAVY,
                episodic_weight=0.8,
                semantic_weight=0.2,
            ),
            RetrievalStrategy.SEMANTIC_HEAVY: RetrievalConfig(
                strategy=RetrievalStrategy.SEMANTIC_HEAVY,
                episodic_weight=0.2,
                semantic_weight=0.8,
            ),
            RetrievalStrategy.TEMPORAL: RetrievalConfig(
                strategy=RetrievalStrategy.TEMPORAL,
                episodic_weight=0.7,
                semantic_weight=0.3,
                recency_boost=0.5,
            ),
            RetrievalStrategy.EMOTIONAL: RetrievalConfig(
                strategy=RetrievalStrategy.EMOTIONAL,
                episodic_weight=0.8,
                semantic_weight=0.2,
                importance_threshold=0.3,
            ),
            RetrievalStrategy.RELATIONSHIP_FOCUSED: RetrievalConfig(
                strategy=RetrievalStrategy.RELATIONSHIP_FOCUSED,
                episodic_weight=0.6,
                semantic_weight=0.4,
            ),
            RetrievalStrategy.CONTEXTUAL: RetrievalConfig(
                strategy=RetrievalStrategy.CONTEXTUAL,
                episodic_weight=0.5,
                semantic_weight=0.5,
            ),
        }
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        strategy: RetrievalStrategy = RetrievalStrategy.BALANCED,
        include_episodic: bool = True,
        include_semantic: bool = True,
        time_window: Optional[timedelta] = None,
        category_filter: Optional[str] = None,
        emotion_filter: Optional[str] = None,
    ) -> "MemorySearchResult":
        """
        Retrieve memories using specified strategy.
        
        Args:
            query: Search query
            top_k: Number of results per type
            strategy: Retrieval strategy
            include_episodic: Include episodic memories
            include_semantic: Include semantic memories
            time_window: Time window for episodic
            category_filter: Category filter for semantic
            emotion_filter: Emotion filter for episodic
            
        Returns:
            MemorySearchResult with combined results
        """
        # Import here to avoid circular dependency
        from src.core.memory.memory_manager import MemorySearchResult
        
        config = self._strategy_configs.get(
            strategy,
            self._strategy_configs[RetrievalStrategy.BALANCED]
        )
        
        # Detect contextual strategy
        if strategy == RetrievalStrategy.CONTEXTUAL:
            config = self._determine_contextual_config(query)
        
        episodic_results: list[EpisodeMemoryItem] = []
        semantic_results: list[SemanticMemoryItem] = []
        
        # Retrieve episodic memories
        if include_episodic:
            ep_top_k = int(top_k * config.episodic_weight * 2)
            episodic_results = await self.episodic.retrieve(
                query=query,
                top_k=ep_top_k,
                min_importance=config.importance_threshold,
                time_window=time_window,
                emotion_filter=emotion_filter,
            )
        
        # Retrieve semantic memories
        if include_semantic:
            sem_top_k = int(top_k * config.semantic_weight * 2)
            semantic_results = await self.semantic.retrieve(
                query=query,
                top_k=sem_top_k,
                category=category_filter,
                min_confidence=config.confidence_threshold,
            )
        
        # Apply strategy-specific reranking
        episodic_results = self._rerank_episodic(
            episodic_results, config, top_k
        )
        semantic_results = self._rerank_semantic(
            semantic_results, config, top_k
        )
        
        # Calculate combined score
        combined_score = self._calculate_combined_score(
            episodic_results, semantic_results, config
        )
        
        self.logger.debug(
            "Retrieved memories",
            query_length=len(query),
            strategy=strategy.value,
            episodic_count=len(episodic_results),
            semantic_count=len(semantic_results),
        )
        
        return MemorySearchResult(
            episodic=episodic_results,
            semantic=semantic_results,
            combined_score=combined_score,
            query=query,
            metadata={
                "strategy": strategy.value,
                "config": config.model_dump(),
            },
        )
    
    def _determine_contextual_config(self, query: str) -> RetrievalConfig:
        """
        Determine best config based on query content.
        
        Analyzes the query to select the most appropriate
        retrieval strategy automatically.
        """
        query_lower = query.lower()
        
        # Check for temporal indicators
        temporal_words = ["recent", "yesterday", "today", "last", "when", "time"]
        if any(word in query_lower for word in temporal_words):
            return self._strategy_configs[RetrievalStrategy.TEMPORAL]
        
        # Check for emotional indicators
        emotion_words = ["feel", "felt", "emotion", "happy", "sad", "angry", "afraid"]
        if any(word in query_lower for word in emotion_words):
            return self._strategy_configs[RetrievalStrategy.EMOTIONAL]
        
        # Check for relationship indicators
        relationship_words = ["who", "person", "friend", "enemy", "met", "know"]
        if any(word in query_lower for word in relationship_words):
            return self._strategy_configs[RetrievalStrategy.RELATIONSHIP_FOCUSED]
        
        # Check for knowledge indicators
        knowledge_words = ["what", "how", "why", "explain", "tell", "know about"]
        if any(word in query_lower for word in knowledge_words):
            return self._strategy_configs[RetrievalStrategy.SEMANTIC_HEAVY]
        
        # Default to balanced
        return self._strategy_configs[RetrievalStrategy.BALANCED]
    
    def _rerank_episodic(
        self,
        memories: list[EpisodeMemoryItem],
        config: RetrievalConfig,
        top_k: int,
    ) -> list[EpisodeMemoryItem]:
        """Rerank episodic memories based on strategy config."""
        if not memories:
            return []
        
        from datetime import datetime
        current_time = datetime.now()
        
        # Score and sort
        scored = []
        for mem in memories:
            score = mem.calculate_relevance_score(current_time)
            
            # Apply recency boost
            days_old = (current_time - mem.timestamp).days
            if days_old < 7:
                score *= (1 + config.recency_boost)
            
            scored.append((score, mem))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scored[:top_k]]
    
    def _rerank_semantic(
        self,
        memories: list[SemanticMemoryItem],
        config: RetrievalConfig,
        top_k: int,
    ) -> list[SemanticMemoryItem]:
        """Rerank semantic memories based on strategy config."""
        if not memories:
            return []
        
        # Score and sort by confidence and access
        scored = []
        for mem in memories:
            score = mem.confidence
            
            # Boost by access frequency
            import math
            access_boost = math.log(mem.access_count + 1) / 10
            score += access_boost
            
            scored.append((score, mem))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scored[:top_k]]
    
    def _calculate_combined_score(
        self,
        episodic: list[EpisodeMemoryItem],
        semantic: list[SemanticMemoryItem],
        config: RetrievalConfig,
    ) -> float:
        """Calculate overall retrieval score."""
        if not episodic and not semantic:
            return 0.0
        
        ep_score = 0.0
        if episodic:
            ep_score = sum(m.importance for m in episodic) / len(episodic)
        
        sem_score = 0.0
        if semantic:
            sem_score = sum(m.confidence for m in semantic) / len(semantic)
        
        return (
            config.episodic_weight * ep_score +
            config.semantic_weight * sem_score
        )
    
    async def retrieve_similar(
        self,
        memory_id: str,
        memory_type: str = "episodic",
        top_k: int = 5,
    ) -> list[Any]:
        """
        Retrieve memories similar to a given memory.
        
        Args:
            memory_id: ID of the reference memory
            memory_type: Type of memory ("episodic" or "semantic")
            top_k: Number of similar memories to return
            
        Returns:
            List of similar memories
        """
        if memory_type == "episodic":
            reference = self.episodic.get_by_id(memory_id)
            if not reference:
                return []
            return await self.episodic.retrieve(
                query=reference.content,
                top_k=top_k + 1,  # +1 to exclude self
            )
        else:
            reference = self.semantic.get_by_id(memory_id)
            if not reference:
                return []
            return await self.semantic.retrieve(
                query=reference.content,
                top_k=top_k + 1,
            )
    
    async def retrieve_chain(
        self,
        start_query: str,
        depth: int = 3,
        branch_factor: int = 2,
    ) -> list[Any]:
        """
        Retrieve a chain of related memories.
        
        Starts with a query and follows related concepts
        to build a chain of connected memories.
        
        Args:
            start_query: Initial query
            depth: How many levels deep to go
            branch_factor: How many branches per level
            
        Returns:
            List of chained memories
        """
        from src.core.memory.memory_manager import MemorySearchResult
        
        all_memories: list[Any] = []
        queries = [start_query]
        seen_ids: set[str] = set()
        
        for level in range(depth):
            next_queries = []
            
            for query in queries[:branch_factor]:
                result = await self.retrieve(
                    query=query,
                    top_k=branch_factor,
                    strategy=RetrievalStrategy.BALANCED,
                )
                
                for mem in result.episodic:
                    if mem.memory_id not in seen_ids:
                        seen_ids.add(mem.memory_id)
                        all_memories.append(mem)
                        # Add tags as next queries
                        next_queries.extend(mem.tags[:2])
                
                for mem in result.semantic:
                    if mem.memory_id not in seen_ids:
                        seen_ids.add(mem.memory_id)
                        all_memories.append(mem)
                        # Add related concepts as next queries
                        next_queries.extend(mem.related_concepts[:2])
            
            queries = next_queries
        
        return all_memories
