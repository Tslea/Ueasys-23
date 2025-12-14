"""
Character Service - Business logic for character management.

This module provides the service layer for character operations,
coordinating between the database, RAG system, and character engine.
"""

from typing import Any, Optional
from uuid import uuid4

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging_config import get_logger, LoggerMixin
from src.db.models.character import Character, CharacterTrait, AlignmentType, ArchetypeType
from src.core.character.personality_core import PersonalityCore, Alignment, Archetype
from src.core.character.character_engine import CharacterEngine
from src.rag.rag_system import RAGSystem

logger = get_logger(__name__)


class CharacterService(LoggerMixin):
    """
    Service for character management.
    
    Handles creation, loading, and management of characters,
    coordinating between database storage and runtime engines.
    
    Example:
        >>> service = CharacterService(session, rag_system)
        >>> character = await service.load_character("gandalf")
        >>> engine = await service.get_character_engine("gandalf")
    """
    
    def __init__(
        self,
        session: AsyncSession,
        rag_system: Optional[RAGSystem] = None,
    ):
        """
        Initialize the character service.
        
        Args:
            session: Database session
            rag_system: Optional RAG system for knowledge indexing
        """
        self._session = session
        self._rag = rag_system or RAGSystem()
        
        # Cache for character engines
        self._engine_cache: dict[str, CharacterEngine] = {}
        
        self.logger.info("Initialized CharacterService")
    
    async def create_character(
        self,
        name: str,
        archetype: ArchetypeType,
        alignment: AlignmentType,
        personality: dict[str, Any],
        speaking_style: dict[str, Any],
        background: dict[str, Any],
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Character:
        """
        Create a new character.
        
        Args:
            name: Character name
            archetype: Character archetype
            alignment: Moral alignment
            personality: Personality configuration
            speaking_style: Speaking style configuration
            background: Background information
            title: Optional title
            description: Optional description
            
        Returns:
            Created Character model
        """
        character = Character(
            id=str(uuid4()),
            name=name,
            title=title,
            description=description,
            archetype=archetype,
            alignment=alignment,
            personality_json=personality,
            speaking_style_json=speaking_style,
            background_json=background,
        )
        
        self._session.add(character)
        await self._session.commit()
        await self._session.refresh(character)
        
        # Index in RAG system
        await self._index_character(character)
        
        self.logger.info(
            "Created character",
            character_id=character.id,
            name=name,
        )
        
        return character
    
    async def load_from_yaml(self, yaml_path: str) -> Character:
        """
        Load a character from a YAML file.
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            Created Character model
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # Map archetype string to enum
        archetype_str = data.get("archetype", "hero").upper()
        archetype = ArchetypeType[archetype_str]
        
        # Map alignment string to enum
        alignment_str = data.get("alignment", "true_neutral").upper()
        alignment = AlignmentType[alignment_str]
        
        return await self.create_character(
            name=data["name"],
            archetype=archetype,
            alignment=alignment,
            personality=data.get("personality", {}),
            speaking_style=data.get("speaking_style", {}),
            background=data.get("background", {}),
            title=data.get("title"),
            description=data.get("description"),
        )
    
    async def get_character(self, character_id: str) -> Optional[Character]:
        """
        Get a character by ID.
        
        Args:
            character_id: Character UUID
            
        Returns:
            Character model or None
        """
        result = await self._session.execute(
            select(Character).where(Character.id == character_id)
        )
        return result.scalar_one_or_none()
    
    async def get_character_by_name(self, name: str) -> Optional[Character]:
        """
        Get a character by name.
        
        Args:
            name: Character name
            
        Returns:
            Character model or None
        """
        result = await self._session.execute(
            select(Character).where(Character.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_character_engine(
        self,
        character_id: str,
        use_cache: bool = True,
    ) -> Optional[CharacterEngine]:
        """
        Get a CharacterEngine for a character.
        
        Args:
            character_id: Character UUID
            use_cache: Whether to use cached engines
            
        Returns:
            CharacterEngine instance or None
        """
        # Check cache
        if use_cache and character_id in self._engine_cache:
            return self._engine_cache[character_id]
        
        # Load character
        character = await self.get_character(character_id)
        if not character:
            return None
        
        # Create personality core
        personality = self._build_personality_core(character)
        
        # Create engine
        engine = CharacterEngine(personality=personality)
        
        # Cache
        if use_cache:
            self._engine_cache[character_id] = engine
        
        return engine
    
    def _build_personality_core(self, character: Character) -> PersonalityCore:
        """Build PersonalityCore from Character model."""
        # Map DB enum to core enum
        archetype = Archetype[character.archetype.name]
        alignment = Alignment[character.alignment.name]
        
        personality_data = character.personality_json
        
        return PersonalityCore(
            character_id=character.id,
            name=character.name,
            archetype=archetype,
            alignment=alignment,
            traits=[],  # Will be populated from personality_data
            values=[],
            motivations=personality_data.get("motivations", []),
            fears=personality_data.get("fears", []),
        )
    
    async def _index_character(self, character: Character) -> None:
        """Index character in RAG system."""
        # Build character data for indexing
        character_data = {
            "id": character.id,
            "name": character.name,
            "essence": {
                "personality": character.personality_json.get("description", ""),
                "values": character.personality_json.get("values", []),
                "motivations": character.personality_json.get("motivations", []),
                "background": character.background_json.get("summary", ""),
            },
            "knowledge": {
                "abilities": character.background_json.get("abilities", []),
                "history": character.background_json.get("history", []),
                "lore": character.background_json.get("lore", []),
            },
            "relationships": character.personality_json.get("relationships", []),
            "style": character.speaking_style_json,
        }
        
        await self._rag.index_character(character_data)
    
    async def update_character(
        self,
        character_id: str,
        **updates: Any,
    ) -> Optional[Character]:
        """
        Update a character.
        
        Args:
            character_id: Character UUID
            **updates: Fields to update
            
        Returns:
            Updated Character model or None
        """
        character = await self.get_character(character_id)
        if not character:
            return None
        
        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)
        
        await self._session.commit()
        await self._session.refresh(character)
        
        # Clear cache and re-index
        if character_id in self._engine_cache:
            del self._engine_cache[character_id]
        await self._index_character(character)
        
        return character
    
    async def delete_character(self, character_id: str) -> bool:
        """
        Delete a character.
        
        Args:
            character_id: Character UUID
            
        Returns:
            True if deleted
        """
        character = await self.get_character(character_id)
        if not character:
            return False
        
        await self._session.delete(character)
        await self._session.commit()
        
        # Clear cache and RAG
        if character_id in self._engine_cache:
            del self._engine_cache[character_id]
        await self._rag.delete_character(character_id)
        
        self.logger.info("Deleted character", character_id=character_id)
        
        return True
