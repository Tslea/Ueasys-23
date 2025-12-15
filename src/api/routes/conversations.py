"""
Conversation routes - CRUD operations for conversations.

This module provides REST API endpoints for conversation management.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config.logging_config import get_logger
from src.db.session import get_session_dependency
from src.db.models.conversation import Conversation, Message, ConversationStatus, MessageRole

logger = get_logger(__name__)
router = APIRouter()


# Request/Response models
class ConversationCreate(BaseModel):
    """Request model for creating a conversation."""
    character_id: str
    user_id: str
    title: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)
    settings: dict[str, Any] = Field(default_factory=dict)


class MessageCreate(BaseModel):
    """Request model for adding a message."""
    role: MessageRole
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    """Response model for a message."""
    id: str
    role: str
    content: str
    tokens: int
    created_at: str
    metadata: dict[str, Any]

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response model for a conversation."""
    id: str
    character_id: str
    user_id: str
    title: Optional[str]
    status: str
    message_count: int
    context: dict[str, Any]
    settings: dict[str, Any]
    started_at: str
    ended_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    """Response model for conversation with messages."""
    messages: list[MessageResponse]


class ConversationListResponse(BaseModel):
    """Response model for conversation list."""
    items: list[ConversationResponse]
    total: int
    page: int
    page_size: int


# Routes
@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    character_id: Optional[str] = None,
    user_id: Optional[str] = None,
    status: Optional[ConversationStatus] = None,
    session: AsyncSession = Depends(get_session_dependency),
) -> ConversationListResponse:
    """
    List conversations with pagination.
    
    Args:
        page: Page number
        page_size: Items per page
        character_id: Filter by character
        user_id: Filter by user
        status: Filter by status
        
    Returns:
        Paginated list of conversations
    """
    query = select(Conversation)
    
    if character_id:
        query = query.where(Conversation.character_id == character_id)
    if user_id:
        query = query.where(Conversation.user_id == user_id)
    if status:
        query = query.where(Conversation.status == status)
    
    # Get total count
    count_query = select(Conversation.id)
    if character_id:
        count_query = count_query.where(Conversation.character_id == character_id)
    if user_id:
        count_query = count_query.where(Conversation.user_id == user_id)
    if status:
        count_query = count_query.where(Conversation.status == status)
    
    result = await session.execute(count_query)
    total = len(result.scalars().all())
    
    # Get page
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Conversation.created_at.desc())
    
    result = await session.execute(query)
    conversations = result.scalars().all()
    
    return ConversationListResponse(
        items=[
            ConversationResponse(
                id=c.id,
                character_id=c.character_id,
                user_id=c.user_id,
                title=c.title,
                status=c.status.value,
                message_count=c.message_count,
                context=c.context_json,
                settings=c.settings_json,
                started_at=c.started_at.isoformat(),
                ended_at=c.ended_at.isoformat() if c.ended_at else None,
                created_at=c.created_at.isoformat(),
            )
            for c in conversations
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    include_messages: bool = Query(True),
    session: AsyncSession = Depends(get_session_dependency),
) -> ConversationDetailResponse:
    """
    Get a specific conversation.
    
    Args:
        conversation_id: Conversation UUID
        include_messages: Whether to include messages
        
    Returns:
        Conversation details with optional messages
        
    Raises:
        HTTPException: If conversation not found
    """
    query = select(Conversation).where(Conversation.id == conversation_id)
    
    if include_messages:
        query = query.options(selectinload(Conversation.messages))
    
    result = await session.execute(query)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = []
    if include_messages:
        messages = [
            MessageResponse(
                id=m.id,
                role=m.role.value,
                content=m.content,
                tokens=m.tokens,
                created_at=m.created_at.isoformat(),
                metadata=m.metadata_json,
            )
            for m in conversation.messages
        ]
    
    return ConversationDetailResponse(
        id=conversation.id,
        character_id=conversation.character_id,
        user_id=conversation.user_id,
        title=conversation.title,
        status=conversation.status.value,
        message_count=conversation.message_count,
        context=conversation.context_json,
        settings=conversation.settings_json,
        started_at=conversation.started_at.isoformat(),
        ended_at=conversation.ended_at.isoformat() if conversation.ended_at else None,
        created_at=conversation.created_at.isoformat(),
        messages=messages,
    )


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    session: AsyncSession = Depends(get_session_dependency),
) -> ConversationResponse:
    """
    Create a new conversation.
    
    Args:
        data: Conversation creation data
        
    Returns:
        Created conversation
    """
    conversation = Conversation(
        id=str(uuid4()),
        character_id=data.character_id,
        user_id=data.user_id,
        title=data.title,
        context_json=data.context,
        settings_json=data.settings,
        started_at=datetime.now(),
    )
    
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    
    logger.info(
        "Created conversation",
        conversation_id=conversation.id,
        character_id=conversation.character_id,
    )
    
    return ConversationResponse(
        id=conversation.id,
        character_id=conversation.character_id,
        user_id=conversation.user_id,
        title=conversation.title,
        status=conversation.status.value,
        message_count=conversation.message_count,
        context=conversation.context_json,
        settings=conversation.settings_json,
        started_at=conversation.started_at.isoformat(),
        ended_at=None,
        created_at=conversation.created_at.isoformat(),
    )


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=201)
async def add_message(
    conversation_id: str,
    data: MessageCreate,
    session: AsyncSession = Depends(get_session_dependency),
) -> MessageResponse:
    """
    Add a message to a conversation.
    
    Args:
        conversation_id: Conversation UUID
        data: Message data
        
    Returns:
        Created message
        
    Raises:
        HTTPException: If conversation not found
    """
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    message = Message(
        id=str(uuid4()),
        conversation_id=conversation_id,
        role=data.role,
        content=data.content,
        tokens=len(data.content) // 4,  # Rough estimate
        metadata_json=data.metadata,
    )
    
    session.add(message)
    conversation.message_count += 1
    
    await session.commit()
    await session.refresh(message)
    
    return MessageResponse(
        id=message.id,
        role=message.role.value,
        content=message.content,
        tokens=message.tokens,
        created_at=message.created_at.isoformat(),
        metadata=message.metadata_json,
    )


@router.post("/{conversation_id}/end", response_model=ConversationResponse)
async def end_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_session_dependency),
) -> ConversationResponse:
    """
    End a conversation.
    
    Args:
        conversation_id: Conversation UUID
        
    Returns:
        Updated conversation
        
    Raises:
        HTTPException: If conversation not found
    """
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.status = ConversationStatus.ENDED
    conversation.ended_at = datetime.now()
    
    await session.commit()
    await session.refresh(conversation)
    
    logger.info("Ended conversation", conversation_id=conversation_id)
    
    return ConversationResponse(
        id=conversation.id,
        character_id=conversation.character_id,
        user_id=conversation.user_id,
        title=conversation.title,
        status=conversation.status.value,
        message_count=conversation.message_count,
        context=conversation.context_json,
        settings=conversation.settings_json,
        started_at=conversation.started_at.isoformat(),
        ended_at=conversation.ended_at.isoformat() if conversation.ended_at else None,
        created_at=conversation.created_at.isoformat(),
    )


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_session_dependency),
) -> None:
    """
    Delete a conversation.
    
    Args:
        conversation_id: Conversation UUID
        
    Raises:
        HTTPException: If conversation not found
    """
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await session.delete(conversation)
    await session.commit()
    
    logger.info("Deleted conversation", conversation_id=conversation_id)
