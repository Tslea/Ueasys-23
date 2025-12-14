"""
Character routes - CRUD operations for characters.

This module provides REST API endpoints for character management.
"""

from typing import Any, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging_config import get_logger
from src.db.session import get_session_dependency
from src.db.models.character import Character, CharacterStatus, AlignmentType, ArchetypeType
from src.services.document_indexer import DocumentIndexer

logger = get_logger(__name__)
router = APIRouter()

# Global document indexer
_document_indexer: Optional[DocumentIndexer] = None


def get_document_indexer() -> DocumentIndexer:
    """Get or create document indexer singleton."""
    global _document_indexer
    if _document_indexer is None:
        _document_indexer = DocumentIndexer()
    return _document_indexer


# Request/Response models
class CharacterCreate(BaseModel):
    """Request model for creating a character."""
    name: str = Field(..., min_length=1, max_length=255)
    title: Optional[str] = None
    description: Optional[str] = None
    archetype: ArchetypeType = ArchetypeType.HERO
    alignment: AlignmentType = AlignmentType.TRUE_NEUTRAL
    personality: dict[str, Any] = Field(default_factory=dict)
    speaking_style: dict[str, Any] = Field(default_factory=dict)
    background: dict[str, Any] = Field(default_factory=dict)


class CharacterUpdate(BaseModel):
    """Request model for updating a character."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    title: Optional[str] = None
    description: Optional[str] = None
    archetype: Optional[ArchetypeType] = None
    alignment: Optional[AlignmentType] = None
    status: Optional[CharacterStatus] = None
    personality: Optional[dict[str, Any]] = None
    speaking_style: Optional[dict[str, Any]] = None
    background: Optional[dict[str, Any]] = None


class CharacterResponse(BaseModel):
    """Response model for a character."""
    id: str
    name: str
    title: Optional[str]
    description: Optional[str]
    archetype: str
    alignment: str
    status: str
    personality: dict[str, Any]
    speaking_style: dict[str, Any]
    background: dict[str, Any]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CharacterListResponse(BaseModel):
    """Response model for character list."""
    items: list[CharacterResponse]
    total: int
    page: int
    page_size: int


# Routes
@router.get("", response_model=CharacterListResponse)
async def list_characters(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[CharacterStatus] = None,
    archetype: Optional[ArchetypeType] = None,
    session: AsyncSession = Depends(get_session_dependency),
) -> CharacterListResponse:
    """
    List all characters with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        status: Filter by status
        archetype: Filter by archetype
        
    Returns:
        Paginated list of characters
    """
    query = select(Character)
    
    if status:
        query = query.where(Character.status == status)
    if archetype:
        query = query.where(Character.archetype == archetype)
    
    # Get total count
    count_query = select(Character.id)
    if status:
        count_query = count_query.where(Character.status == status)
    if archetype:
        count_query = count_query.where(Character.archetype == archetype)
    
    result = await session.execute(count_query)
    total = len(result.scalars().all())
    
    # Get page
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await session.execute(query)
    characters = result.scalars().all()
    
    return CharacterListResponse(
        items=[
            CharacterResponse(
                id=c.id,
                name=c.name,
                title=c.title,
                description=c.description,
                archetype=c.archetype.value,
                alignment=c.alignment.value,
                status=c.status.value,
                personality=c.personality_json,
                speaking_style=c.speaking_style_json,
                background=c.background_json,
                created_at=c.created_at.isoformat(),
                updated_at=c.updated_at.isoformat(),
            )
            for c in characters
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: str,
    session: AsyncSession = Depends(get_session_dependency),
) -> CharacterResponse:
    """
    Get a specific character by ID.
    
    Args:
        character_id: Character UUID
        
    Returns:
        Character details
        
    Raises:
        HTTPException: If character not found
    """
    result = await session.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return CharacterResponse(
        id=character.id,
        name=character.name,
        title=character.title,
        description=character.description,
        archetype=character.archetype.value,
        alignment=character.alignment.value,
        status=character.status.value,
        personality=character.personality_json,
        speaking_style=character.speaking_style_json,
        background=character.background_json,
        created_at=character.created_at.isoformat(),
        updated_at=character.updated_at.isoformat(),
    )


@router.post("", response_model=CharacterResponse, status_code=201)
async def create_character(
    data: CharacterCreate,
    session: AsyncSession = Depends(get_session_dependency),
) -> CharacterResponse:
    """
    Create a new character.
    
    Args:
        data: Character creation data
        
    Returns:
        Created character
    """
    character = Character(
        id=str(uuid4()),
        name=data.name,
        title=data.title,
        description=data.description,
        archetype=data.archetype,
        alignment=data.alignment,
        personality_json=data.personality,
        speaking_style_json=data.speaking_style,
        background_json=data.background,
    )
    
    session.add(character)
    await session.commit()
    await session.refresh(character)
    
    logger.info("Created character", character_id=character.id, name=character.name)
    
    return CharacterResponse(
        id=character.id,
        name=character.name,
        title=character.title,
        description=character.description,
        archetype=character.archetype.value,
        alignment=character.alignment.value,
        status=character.status.value,
        personality=character.personality_json,
        speaking_style=character.speaking_style_json,
        background=character.background_json,
        created_at=character.created_at.isoformat(),
        updated_at=character.updated_at.isoformat(),
    )


@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str,
    data: CharacterUpdate,
    session: AsyncSession = Depends(get_session_dependency),
) -> CharacterResponse:
    """
    Update a character.
    
    Args:
        character_id: Character UUID
        data: Update data
        
    Returns:
        Updated character
        
    Raises:
        HTTPException: If character not found
    """
    result = await session.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Update fields
    if data.name is not None:
        character.name = data.name
    if data.title is not None:
        character.title = data.title
    if data.description is not None:
        character.description = data.description
    if data.archetype is not None:
        character.archetype = data.archetype
    if data.alignment is not None:
        character.alignment = data.alignment
    if data.status is not None:
        character.status = data.status
    if data.personality is not None:
        character.personality_json = data.personality
    if data.speaking_style is not None:
        character.speaking_style_json = data.speaking_style
    if data.background is not None:
        character.background_json = data.background
    
    await session.commit()
    await session.refresh(character)
    
    logger.info("Updated character", character_id=character.id)
    
    return CharacterResponse(
        id=character.id,
        name=character.name,
        title=character.title,
        description=character.description,
        archetype=character.archetype.value,
        alignment=character.alignment.value,
        status=character.status.value,
        personality=character.personality_json,
        speaking_style=character.speaking_style_json,
        background=character.background_json,
        created_at=character.created_at.isoformat(),
        updated_at=character.updated_at.isoformat(),
    )


@router.delete("/{character_id}", status_code=204)
async def delete_character(
    character_id: str,
    session: AsyncSession = Depends(get_session_dependency),
) -> None:
    """
    Delete a character.
    
    Args:
        character_id: Character UUID
        
    Raises:
        HTTPException: If character not found
    """
    result = await session.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    await session.delete(character)
    await session.commit()
    
    logger.info("Deleted character", character_id=character_id)


# === Document/Knowledge Management ===

class DocumentUpload(BaseModel):
    """A document to upload for a character."""
    name: str
    content: str


class DocumentUploadRequest(BaseModel):
    """Request to upload documents for a character."""
    documents: List[DocumentUpload]


class DocumentUploadResponse(BaseModel):
    """Response from document upload."""
    character_id: str
    documents_indexed: int
    total_chunks: int
    details: List[dict[str, Any]]


class KnowledgeStats(BaseModel):
    """Statistics about a character's knowledge base."""
    character_id: str
    total_chunks: int
    documents: List[str] = []


@router.post("/{character_id}/knowledge", response_model=DocumentUploadResponse)
async def upload_character_knowledge(
    character_id: str,
    request: DocumentUploadRequest,
    session: AsyncSession = Depends(get_session_dependency),
) -> DocumentUploadResponse:
    """
    Upload documents/books for a character's knowledge base.
    
    This indexes the documents into Qdrant, allowing the character
    to "remember" and reference the content during conversations.
    
    Use this to:
    - Upload books, stories, lore documents
    - Add background information
    - Expand character knowledge
    
    Args:
        character_id: Character UUID
        request: Documents to upload
        
    Returns:
        Statistics about indexed documents
    """
    # Verify character exists
    result = await session.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Index documents
    indexer = get_document_indexer()
    
    documents = [
        {"name": doc.name, "content": doc.content}
        for doc in request.documents
    ]
    
    results = await indexer.index_multiple_documents(
        character_id=character_id,
        documents=documents,
    )
    
    total_chunks = sum(r.indexed_chunks for r in results)
    
    logger.info(
        "Uploaded knowledge for character",
        character_id=character_id,
        character_name=character.name,
        documents=len(results),
        chunks=total_chunks,
    )
    
    return DocumentUploadResponse(
        character_id=character_id,
        documents_indexed=len(results),
        total_chunks=total_chunks,
        details=[
            {
                "document": r.document_name,
                "chunks": r.indexed_chunks,
                "failed": r.failed_chunks,
            }
            for r in results
        ],
    )


@router.get("/{character_id}/knowledge", response_model=KnowledgeStats)
async def get_character_knowledge_stats(
    character_id: str,
    session: AsyncSession = Depends(get_session_dependency),
) -> KnowledgeStats:
    """
    Get statistics about a character's knowledge base.
    
    Returns the number of indexed chunks and document names.
    """
    # Verify character exists
    result = await session.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    indexer = get_document_indexer()
    count = await indexer.get_character_document_count(character_id)
    
    return KnowledgeStats(
        character_id=character_id,
        total_chunks=count,
    )


@router.delete("/{character_id}/knowledge", status_code=204)
async def delete_character_knowledge(
    character_id: str,
    session: AsyncSession = Depends(get_session_dependency),
) -> None:
    """
    Delete all indexed knowledge for a character.
    
    This removes all documents from the RAG system but
    does not delete the character itself.
    """
    # Verify character exists
    result = await session.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    indexer = get_document_indexer()
    await indexer.delete_character_documents(character_id)
    
    logger.info(
        "Deleted knowledge for character",
        character_id=character_id,
        character_name=character.name,
    )
