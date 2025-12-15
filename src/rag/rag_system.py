"""
RAG System - Unified RAG system for character interactions.

This module provides a high-level interface for the RAG system,
combining indexing and retrieval with LLM integration.

Example:
    >>> from src.rag import RAGSystem
    >>> rag = RAGSystem()
    >>> response = await rag.generate_response(
    ...     character_id="gandalf",
    ...     query="Tell me about the Ring"
    ... )
"""

from datetime import datetime
from typing import Any, Optional, Protocol

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.config.settings import get_settings
from src.rag.knowledge_indexer import KnowledgeIndexer, KnowledgeTier
from src.rag.rag_retriever import RAGRetriever, RetrievalContext, RetrievalMode

logger = get_logger(__name__)


class LLMProvider(Protocol):
    """Protocol for LLM providers."""
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a response from the LLM."""
        ...


class RAGResponse(BaseModel):
    """
    Response from the RAG system.
    
    Attributes:
        response: The generated response
        character_id: Character that generated the response
        retrieval_context: Context used for generation
        generation_time_ms: Time taken to generate
        metadata: Additional metadata
    """
    response: str
    character_id: str
    retrieval_context: Optional[RetrievalContext] = None
    generation_time_ms: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGSystem(LoggerMixin):
    """
    Unified RAG system for character interactions.
    
    Combines retrieval and generation for coherent character
    responses augmented with relevant knowledge.
    
    Attributes:
        indexer: Knowledge indexer
        retriever: RAG retriever
        
    Example:
        >>> rag = RAGSystem()
        >>> 
        >>> # Index character knowledge
        >>> await rag.index_character(gandalf_data)
        >>> 
        >>> # Generate response
        >>> response = await rag.generate_response(
        ...     character_id="gandalf",
        ...     query="What is your opinion on the Ring?"
        ... )
    """
    
    def __init__(
        self,
        collection_name: str = "fantasy_characters",
        llm_provider: Optional[LLMProvider] = None,
    ):
        """
        Initialize the RAG system.
        
        Args:
            collection_name: Name of the vector store collection
            llm_provider: Optional LLM provider for generation
        """
        self._settings = get_settings()
        self._collection_name = collection_name
        
        # Initialize components
        self._indexer = KnowledgeIndexer(collection_name=collection_name)
        self._retriever = RAGRetriever(collection_name=collection_name)
        self._llm = llm_provider
        
        # Cache for character system prompts
        self._system_prompt_cache: dict[str, str] = {}
        
        self.logger.info(
            "Initialized RAGSystem",
            collection=collection_name,
        )
    
    def set_llm_provider(self, provider: LLMProvider) -> None:
        """Set the LLM provider for generation."""
        self._llm = provider
    
    async def index_character(
        self,
        character_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Index character knowledge.
        
        Args:
            character_data: Character data to index
            
        Returns:
            Indexing statistics
        """
        stats = await self._indexer.index_character(character_data)
        
        # Cache system prompt if personality data provided
        if "id" in character_data and "essence" in character_data:
            self._build_system_prompt_cache(
                character_data["id"],
                character_data
            )
        
        return stats.model_dump()
    
    def _build_system_prompt_cache(
        self,
        character_id: str,
        character_data: dict[str, Any],
    ) -> None:
        """Build and cache system prompt for a character."""
        name = character_data.get("name", "Unknown")
        essence = character_data.get("essence", {})
        style = character_data.get("style", {})
        
        prompt_parts = [
            f"You are {name}, a character in a fantasy world.",
            "",
            "## Core Identity",
        ]
        
        if "personality" in essence:
            prompt_parts.append(f"Personality: {essence['personality']}")
        
        if "values" in essence:
            values = essence["values"]
            if isinstance(values, list):
                values = ", ".join(values)
            prompt_parts.append(f"Values: {values}")
        
        if "background" in essence:
            prompt_parts.append(f"Background: {essence['background']}")
        
        if style:
            prompt_parts.extend([
                "",
                "## Communication Style",
            ])
            if "speech_patterns" in style:
                prompt_parts.append(f"Speech patterns: {style['speech_patterns']}")
            if "tone" in style:
                prompt_parts.append(f"Tone: {style['tone']}")
        
        prompt_parts.extend([
            "",
            "## Guidelines",
            "- Stay in character at all times",
            "- Respond authentically based on your personality and knowledge",
            "- Use your characteristic speech patterns",
            "- Draw on relevant memories and knowledge when responding",
        ])
        
        self._system_prompt_cache[character_id] = "\n".join(prompt_parts)
    
    async def retrieve_context(
        self,
        character_id: str,
        query: str,
        mode: RetrievalMode = RetrievalMode.BALANCED,
        top_k: int = 10,
    ) -> RetrievalContext:
        """
        Retrieve relevant context for a query.
        
        Args:
            character_id: Character to retrieve for
            query: The query text
            mode: Retrieval mode
            top_k: Maximum results
            
        Returns:
            RetrievalContext with relevant knowledge
        """
        return await self._retriever.retrieve_context(
            character_id=character_id,
            query=query,
            mode=mode,
            top_k=top_k,
        )
    
    async def retrieve(
        self,
        query: str,
        character_id: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant knowledge for a query.
        
        Simple interface for retrieving knowledge chunks
        that's compatible with CharacterEngine expectations.
        
        Args:
            query: The query text
            character_id: Character to retrieve for
            top_k: Maximum results
            
        Returns:
            List of relevant knowledge chunks as dicts
        """
        try:
            context = await self.retrieve_context(
                character_id=character_id,
                query=query,
                top_k=top_k,
            )
            # Convert RetrievalContext results to simple dict format
            results = []
            for chunk in context.chunks:
                results.append({
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                    "score": chunk.score,
                    "tier": chunk.tier.value if hasattr(chunk, 'tier') else "unknown",
                })
            return results
        except Exception as e:
            self.logger.error("Retrieve failed", error=str(e))
            return []
    
    async def generate_response(
        self,
        character_id: str,
        query: str,
        conversation_history: Optional[list[dict[str, str]]] = None,
        mode: RetrievalMode = RetrievalMode.BALANCED,
        include_context: bool = True,
    ) -> RAGResponse:
        """
        Generate a character response using RAG.
        
        Args:
            character_id: Character to respond as
            query: User's query/message
            conversation_history: Previous conversation messages
            mode: Retrieval mode for context
            include_context: Whether to include RAG context
            
        Returns:
            RAGResponse with generated response and metadata
        """
        start_time = datetime.now()
        
        self.logger.info(
            "Generating RAG response",
            character_id=character_id,
            query_length=len(query),
        )
        
        # Retrieve context
        context = None
        if include_context:
            if conversation_history:
                context = await self._retriever.retrieve_for_conversation(
                    character_id=character_id,
                    conversation_history=conversation_history,
                    current_message=query,
                )
            else:
                context = await self._retriever.retrieve_context(
                    character_id=character_id,
                    query=query,
                    mode=mode,
                )
        
        # Build prompt
        system_prompt = self._system_prompt_cache.get(character_id)
        if not system_prompt:
            system_prompt = f"You are a fantasy character with ID {character_id}. Respond in character."
        
        # Add retrieved context to prompt
        prompt = self._build_generation_prompt(
            query=query,
            context=context,
            conversation_history=conversation_history,
        )
        
        # Generate response
        if self._llm:
            response_text = await self._llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
            )
        else:
            # Fallback for development without LLM
            response_text = self._generate_fallback_response(
                character_id, query, context
            )
        
        generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return RAGResponse(
            response=response_text,
            character_id=character_id,
            retrieval_context=context,
            generation_time_ms=generation_time,
            metadata={
                "mode": mode.value if include_context else "no_retrieval",
                "context_items": len(context.results) if context else 0,
            },
        )
    
    def _build_generation_prompt(
        self,
        query: str,
        context: Optional[RetrievalContext],
        conversation_history: Optional[list[dict[str, str]]],
    ) -> str:
        """Build the generation prompt."""
        parts = []
        
        # Add conversation history
        if conversation_history:
            parts.append("## Previous Conversation")
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                parts.append(f"{role.title()}: {content}")
            parts.append("")
        
        # Add retrieved context
        if context and context.results:
            parts.append("## Relevant Knowledge")
            parts.append(context.get_formatted_context())
            parts.append("")
        
        # Add current query
        parts.append("## Current Message")
        parts.append(f"User: {query}")
        parts.append("")
        parts.append("Respond in character:")
        
        return "\n".join(parts)
    
    def _generate_fallback_response(
        self,
        character_id: str,
        query: str,
        context: Optional[RetrievalContext],
    ) -> str:
        """Generate a fallback response when LLM is not available."""
        response_parts = [
            f"[Development Mode - No LLM Configured]",
            f"",
            f"Character: {character_id}",
            f"Query: {query[:100]}...",
        ]
        
        if context and context.results:
            response_parts.extend([
                f"",
                f"Retrieved {len(context.results)} context items:",
            ])
            for result in context.results[:3]:
                response_parts.append(f"- [{result.tier.value}] {result.content[:50]}...")
        
        return "\n".join(response_parts)
    
    async def delete_character(self, character_id: str) -> bool:
        """
        Delete all indexed knowledge for a character.
        
        Args:
            character_id: Character to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            await self._indexer.delete_character(character_id)
            
            # Clear cache
            if character_id in self._system_prompt_cache:
                del self._system_prompt_cache[character_id]
            
            return True
        except Exception as e:
            self.logger.error(
                "Failed to delete character",
                character_id=character_id,
                error=str(e),
            )
            return False
    
    async def get_character_knowledge_summary(
        self,
        character_id: str,
    ) -> dict[str, Any]:
        """
        Get a summary of indexed knowledge for a character.
        
        Args:
            character_id: Character to summarize
            
        Returns:
            Summary dictionary with counts and sample content by tier
        """
        summary = await self._retriever.get_character_summary(character_id)
        
        return {
            "character_id": character_id,
            "by_tier": {
                tier: {
                    "count": len(items),
                    "samples": items[:3],
                }
                for tier, items in summary.items()
            },
            "total_chunks": sum(len(items) for items in summary.values()),
        }
