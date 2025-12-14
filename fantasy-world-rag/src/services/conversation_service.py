"""
Conversation Service - Business logic for conversation management.

This module provides the service layer for conversation operations.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config.logging_config import get_logger, LoggerMixin
from src.db.models.conversation import Conversation, Message, ConversationStatus, MessageRole

logger = get_logger(__name__)


class ConversationService(LoggerMixin):
    """
    Service for conversation management.
    
    Handles conversation lifecycle, message storage, and retrieval.
    
    Example:
        >>> service = ConversationService(session)
        >>> conv = await service.create_conversation("gandalf", "user123")
        >>> await service.add_message(conv.id, "user", "Hello!")
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the conversation service.
        
        Args:
            session: Database session
        """
        self._session = session
        self.logger.info("Initialized ConversationService")
    
    async def create_conversation(
        self,
        character_id: str,
        user_id: str,
        title: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        settings: Optional[dict[str, Any]] = None,
    ) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            character_id: Character UUID
            user_id: User identifier
            title: Optional conversation title
            context: Initial context
            settings: Conversation settings
            
        Returns:
            Created Conversation model
        """
        conversation = Conversation(
            id=str(uuid4()),
            character_id=character_id,
            user_id=user_id,
            title=title,
            context_json=context or {},
            settings_json=settings or {},
            started_at=datetime.now(),
        )
        
        self._session.add(conversation)
        await self._session.commit()
        await self._session.refresh(conversation)
        
        self.logger.info(
            "Created conversation",
            conversation_id=conversation.id,
            character_id=character_id,
        )
        
        return conversation
    
    async def get_conversation(
        self,
        conversation_id: str,
        include_messages: bool = False,
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: Conversation UUID
            include_messages: Whether to load messages
            
        Returns:
            Conversation model or None
        """
        query = select(Conversation).where(Conversation.id == conversation_id)
        
        if include_messages:
            query = query.options(selectinload(Conversation.messages))
        
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_or_create_conversation(
        self,
        character_id: str,
        user_id: str,
    ) -> Conversation:
        """
        Get active conversation or create new one.
        
        Args:
            character_id: Character UUID
            user_id: User identifier
            
        Returns:
            Conversation model
        """
        # Look for active conversation
        result = await self._session.execute(
            select(Conversation).where(
                Conversation.character_id == character_id,
                Conversation.user_id == user_id,
                Conversation.status == ConversationStatus.ACTIVE,
            ).order_by(Conversation.created_at.desc())
        )
        conversation = result.scalar_one_or_none()
        
        if conversation:
            return conversation
        
        return await self.create_conversation(character_id, user_id)
    
    async def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        tokens: int = 0,
        generation_time_ms: Optional[int] = None,
        emotional_context: Optional[dict[str, Any]] = None,
        rag_context: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Message:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation UUID
            role: Message role
            content: Message content
            tokens: Token count
            generation_time_ms: Generation time for character messages
            emotional_context: Emotional state during message
            rag_context: RAG context used
            metadata: Additional metadata
            
        Returns:
            Created Message model
        """
        message = Message(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens=tokens or len(content) // 4,
            generation_time_ms=generation_time_ms,
            emotional_context_json=emotional_context or {},
            rag_context_json=rag_context or {},
            metadata_json=metadata or {},
        )
        
        self._session.add(message)
        
        # Update conversation message count
        result = await self._session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.message_count += 1
            conversation.total_tokens += message.tokens
        
        await self._session.commit()
        await self._session.refresh(message)
        
        return message
    
    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        before_id: Optional[str] = None,
    ) -> list[Message]:
        """
        Get messages from a conversation.
        
        Args:
            conversation_id: Conversation UUID
            limit: Maximum messages to return
            before_id: Get messages before this ID
            
        Returns:
            List of Message models
        """
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        
        if before_id:
            result = await self._session.execute(
                select(Message.created_at).where(Message.id == before_id)
            )
            before_time = result.scalar_one_or_none()
            if before_time:
                query = query.where(Message.created_at < before_time)
        
        result = await self._session.execute(query)
        messages = list(result.scalars().all())
        
        # Return in chronological order
        return list(reversed(messages))
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """
        Get conversation history in simple format for LLM.
        
        Args:
            conversation_id: Conversation UUID
            limit: Maximum messages
            
        Returns:
            List of {"role": ..., "content": ...} dicts
        """
        messages = await self.get_messages(conversation_id, limit=limit)
        
        return [
            {
                "role": "user" if m.role == MessageRole.USER else "assistant",
                "content": m.content,
            }
            for m in messages
        ]
    
    async def end_conversation(
        self,
        conversation_id: str,
    ) -> Optional[Conversation]:
        """
        End a conversation.
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            Updated Conversation model or None
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        conversation.status = ConversationStatus.ENDED
        conversation.ended_at = datetime.now()
        
        await self._session.commit()
        await self._session.refresh(conversation)
        
        self.logger.info("Ended conversation", conversation_id=conversation_id)
        
        return conversation
    
    async def archive_conversation(
        self,
        conversation_id: str,
    ) -> Optional[Conversation]:
        """
        Archive a conversation.
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            Updated Conversation model or None
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        conversation.status = ConversationStatus.ARCHIVED
        
        await self._session.commit()
        await self._session.refresh(conversation)
        
        return conversation
    
    async def delete_conversation(
        self,
        conversation_id: str,
    ) -> bool:
        """
        Delete a conversation and all messages.
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            True if deleted
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        await self._session.delete(conversation)
        await self._session.commit()
        
        self.logger.info("Deleted conversation", conversation_id=conversation_id)
        
        return True
