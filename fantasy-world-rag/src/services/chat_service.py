"""
Chat Service - Unified chat processing with RAG.

This module provides the main chat service that coordinates
character engine, RAG, memory, and LLM for generating responses.
Uses Grok for fast, cost-effective character responses.
"""

from datetime import datetime
from typing import Any, Optional, AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging_config import get_logger, LoggerMixin
from src.config.settings import get_settings
from src.db.models.conversation import MessageRole
from src.services.character_service import CharacterService
from src.services.conversation_service import ConversationService
from src.rag.rag_system import RAGSystem
from src.rag.rag_retriever import RetrievalMode
from src.llm.base_provider import BaseLLMProvider
from src.llm import get_chat_llm
from src.llm.prompt_templates import CharacterPromptBuilder
from src.core.character.character_engine import CharacterEngine

logger = get_logger(__name__)


class ChatResponse:
    """Response from chat service."""
    
    def __init__(
        self,
        response: str,
        character_id: str,
        character_name: str,
        conversation_id: str,
        message_id: str,
        emotional_state: Optional[str] = None,
        generation_time_ms: int = 0,
        tokens_used: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ):
        self.response = response
        self.character_id = character_id
        self.character_name = character_name
        self.conversation_id = conversation_id
        self.message_id = message_id
        self.emotional_state = emotional_state
        self.generation_time_ms = generation_time_ms
        self.tokens_used = tokens_used
        self.metadata = metadata or {}


class ChatService(LoggerMixin):
    """
    Unified chat service.
    
    Coordinates all components for generating character responses:
    - Character Engine for personality and state
    - RAG System for knowledge retrieval
    - LLM for generation
    - Memory for persistence
    
    Example:
        >>> service = ChatService(session)
        >>> response = await service.chat(
        ...     character_id="gandalf",
        ...     user_id="user123",
        ...     message="What do you know about the Ring?"
        ... )
    """
    
    def __init__(
        self,
        session: AsyncSession,
        llm_provider: Optional[BaseLLMProvider] = None,
        rag_system: Optional[RAGSystem] = None,
    ):
        """
        Initialize the chat service.
        
        Args:
            session: Database session
            llm_provider: Optional LLM provider
            rag_system: Optional RAG system
        """
        self._session = session
        self._settings = get_settings()
        
        # Initialize services
        self._rag = rag_system or RAGSystem()
        self._character_service = CharacterService(session, self._rag)
        self._conversation_service = ConversationService(session)
        self._prompt_builder = CharacterPromptBuilder()
        
        # Initialize LLM provider - use chat provider (Grok by default)
        if llm_provider:
            self._llm = llm_provider
        else:
            self._llm = get_chat_llm()
        
        self.logger.info(
            "Initialized ChatService",
            llm_provider=type(self._llm).__name__ if self._llm else "None"
        )
    
    async def chat(
        self,
        character_id: str,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Process a chat message and generate a response.
        
        Args:
            character_id: Character UUID
            user_id: User identifier
            message: User's message
            conversation_id: Optional existing conversation
            context: Additional context
            
        Returns:
            ChatResponse with generated response
        """
        start_time = datetime.now()
        
        self.logger.info(
            "Processing chat message",
            character_id=character_id,
            user_id=user_id,
            message_length=len(message),
        )
        
        # Get character engine
        engine = await self._character_service.get_character_engine(character_id)
        if not engine:
            raise ValueError(f"Character not found: {character_id}")
        
        character = await self._character_service.get_character(character_id)
        
        # Get or create conversation
        if conversation_id:
            conversation = await self._conversation_service.get_conversation(
                conversation_id
            )
            if not conversation:
                raise ValueError(f"Conversation not found: {conversation_id}")
        else:
            conversation = await self._conversation_service.get_or_create_conversation(
                character_id, user_id
            )
        
        # Add user message
        user_msg = await self._conversation_service.add_message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=message,
        )
        
        # Get conversation history
        history = await self._conversation_service.get_conversation_history(
            conversation.id,
            limit=10,
        )
        
        # Process through character engine
        engine_response = await engine.process_message(
            message=message,
            context=context or {},
        )
        
        # Retrieve RAG context
        retrieval_context = await self._rag.retrieve_context(
            character_id=character_id,
            query=message,
            mode=RetrievalMode.BALANCED,
        )
        
        # Build prompt
        system_prompt = self._prompt_builder.build_system_prompt(
            character_data={
                "name": character.name,
                "essence": character.personality_json,
                "style": character.speaking_style_json,
            },
            personality=engine.personality,
        )
        
        user_prompt = self._prompt_builder.build_conversation_prompt(
            character_name=character.name,
            message=message,
            context=retrieval_context,
            history=history,
            emotional_state=engine_response.get("emotional_state"),
            goals=engine_response.get("active_goals"),
            memories=engine_response.get("relevant_memories"),
        )
        
        # Generate response
        if self._llm:
            llm_response = await self._llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
            )
            response_text = llm_response.content
            tokens_used = llm_response.usage.total_tokens
        else:
            # Fallback without LLM
            response_text = self._generate_fallback_response(
                engine, engine_response, message
            )
            tokens_used = len(response_text) // 4
        
        generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Add character response
        char_msg = await self._conversation_service.add_message(
            conversation_id=conversation.id,
            role=MessageRole.CHARACTER,
            content=response_text,
            tokens=tokens_used,
            generation_time_ms=generation_time,
            emotional_context={"state": engine_response.get("emotional_state")},
            rag_context={"items": len(retrieval_context.results) if retrieval_context else 0},
        )
        
        # Update character memory
        await engine.record_interaction(
            user_message=message,
            character_response=response_text,
            context=context or {},
        )
        
        self.logger.info(
            "Chat response generated",
            character_id=character_id,
            conversation_id=conversation.id,
            generation_time_ms=generation_time,
        )
        
        return ChatResponse(
            response=response_text,
            character_id=character_id,
            character_name=character.name,
            conversation_id=conversation.id,
            message_id=char_msg.id,
            emotional_state=engine_response.get("emotional_state"),
            generation_time_ms=generation_time,
            tokens_used=tokens_used,
            metadata={
                "rag_items": len(retrieval_context.results) if retrieval_context else 0,
            },
        )
    
    async def stream_chat(
        self,
        character_id: str,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """
        Stream a chat response.
        
        Args:
            character_id: Character UUID
            user_id: User identifier
            message: User's message
            conversation_id: Optional existing conversation
            context: Additional context
            
        Yields:
            Response tokens as they are generated
        """
        # Get character and conversation
        engine = await self._character_service.get_character_engine(character_id)
        if not engine:
            raise ValueError(f"Character not found: {character_id}")
        
        character = await self._character_service.get_character(character_id)
        
        # Get or create conversation
        if conversation_id:
            conversation = await self._conversation_service.get_conversation(
                conversation_id
            )
            if not conversation:
                raise ValueError(f"Conversation not found: {conversation_id}")
        else:
            conversation = await self._conversation_service.get_or_create_conversation(
                character_id, user_id
            )
        
        # Add user message
        await self._conversation_service.add_message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=message,
        )
        
        # Get history
        history = await self._conversation_service.get_conversation_history(
            conversation.id, limit=10
        )
        
        # Process through engine
        engine_response = await engine.process_message(message, context or {})
        
        # Get RAG context
        retrieval_context = await self._rag.retrieve_context(
            character_id=character_id,
            query=message,
        )
        
        # Build prompts
        system_prompt = self._prompt_builder.build_system_prompt(
            character_data={
                "name": character.name,
                "essence": character.personality_json,
                "style": character.speaking_style_json,
            },
            personality=engine.personality,
        )
        
        user_prompt = self._prompt_builder.build_conversation_prompt(
            character_name=character.name,
            message=message,
            context=retrieval_context,
            history=history,
        )
        
        # Stream response
        full_response = ""
        
        if self._llm:
            async for token in self._llm.stream_generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
            ):
                full_response += token
                yield token
        else:
            # Fallback streaming
            response = self._generate_fallback_response(engine, engine_response, message)
            for word in response.split():
                full_response += word + " "
                yield word + " "
        
        # Save complete response
        await self._conversation_service.add_message(
            conversation_id=conversation.id,
            role=MessageRole.CHARACTER,
            content=full_response.strip(),
        )
    
    def _generate_fallback_response(
        self,
        engine: CharacterEngine,
        engine_response: dict[str, Any],
        message: str,
    ) -> str:
        """Generate fallback response without LLM."""
        name = engine.personality.name
        archetype = engine.personality.archetype.value
        
        # Simple template-based response
        if "?" in message:
            return f"*{name} ponders your question thoughtfully* That is indeed a matter worth considering. As a {archetype}, I have seen many things in my years..."
        else:
            return f"*{name} nods in acknowledgment* Your words carry weight. I shall remember what you have shared."
    
    async def get_character_status(
        self,
        character_id: str,
    ) -> dict[str, Any]:
        """
        Get current status of a character.
        
        Args:
            character_id: Character UUID
            
        Returns:
            Status dictionary with emotional state, goals, etc.
        """
        engine = await self._character_service.get_character_engine(character_id)
        if not engine:
            return {"error": "Character not found"}
        
        return {
            "character_id": character_id,
            "name": engine.personality.name,
            "emotional_state": "neutral",  # From emotional state manager
            "active_goals": [],  # From goal system
            "recent_memories": [],  # From memory system
        }
