"""
Knowledge Indexer - Indexes character knowledge into vector store.

This module handles the indexing of character knowledge into
a multi-tier vector store system using Qdrant.

Example:
    >>> from src.rag import KnowledgeIndexer
    >>> indexer = KnowledgeIndexer()
    >>> await indexer.index_character(character_data)
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.config.settings import get_settings

logger = get_logger(__name__)


class KnowledgeTier(str, Enum):
    """
    Multi-tier knowledge organization.
    
    Following the RAG system specification:
    - ESSENCE: Core identity, personality, values
    - KNOWLEDGE: Lore, history, abilities
    - RELATIONSHIPS: Character relationships
    - STYLE: Communication patterns, speech
    - CONTEXT: Current world state
    """
    ESSENCE = "essence"  # Tier 1: Core identity
    KNOWLEDGE = "knowledge"  # Tier 2: Lore & abilities
    RELATIONSHIPS = "relationships"  # Tier 3: Relationships
    STYLE = "style"  # Tier 4: Communication patterns
    CONTEXT = "context"  # Tier 5: Current state


class KnowledgeChunk(BaseModel):
    """
    A chunk of knowledge to be indexed.
    
    Attributes:
        chunk_id: Unique identifier
        character_id: Character this belongs to
        tier: Knowledge tier
        content: The actual content
        metadata: Additional metadata
        embedding: Vector embedding (set during indexing)
    """
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    character_id: str
    tier: KnowledgeTier
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[list[float]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class IndexingStats(BaseModel):
    """Statistics from an indexing operation."""
    total_chunks: int = 0
    indexed_chunks: int = 0
    failed_chunks: int = 0
    by_tier: dict[str, int] = Field(default_factory=dict)
    duration_ms: int = 0


class KnowledgeIndexer(LoggerMixin):
    """
    Indexes character knowledge into vector store.
    
    Handles the extraction, chunking, and indexing of character
    knowledge into a multi-tier vector store system.
    
    Attributes:
        collection_name: Qdrant collection name
        
    Example:
        >>> indexer = KnowledgeIndexer()
        >>> stats = await indexer.index_character({
        ...     "id": "gandalf",
        ...     "name": "Gandalf",
        ...     "essence": {...},
        ...     "knowledge": {...}
        ... })
    """
    
    def __init__(
        self,
        collection_name: str = "fantasy_characters",
        embedding_model: Optional[str] = None,
    ):
        """
        Initialize the knowledge indexer.
        
        Args:
            collection_name: Name of the Qdrant collection
            embedding_model: Name of the embedding model to use
        """
        self._settings = get_settings()
        self._collection_name = collection_name
        self._embedding_model = embedding_model or self._settings.embedding_model
        
        # Vector store client (initialized lazily)
        self._qdrant_client = None
        
        # Embedding function (initialized lazily)
        self._embed_function = None
        
        self.logger.info(
            "Initialized KnowledgeIndexer",
            collection=collection_name,
            embedding_model=self._embedding_model,
        )
    
    async def _ensure_client(self) -> None:
        """Ensure Qdrant client is initialized."""
        if self._qdrant_client is None:
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.models import Distance, VectorParams
                
                self._qdrant_client = QdrantClient(
                    host=self._settings.qdrant_host,
                    port=self._settings.qdrant_port,
                )
                
                # Create collection if not exists
                collections = self._qdrant_client.get_collections()
                if self._collection_name not in [c.name for c in collections.collections]:
                    self._qdrant_client.create_collection(
                        collection_name=self._collection_name,
                        vectors_config=VectorParams(
                            size=self._settings.embedding_dimension,
                            distance=Distance.COSINE,
                        ),
                    )
                    self.logger.info(
                        "Created Qdrant collection",
                        collection=self._collection_name,
                    )
            except Exception as e:
                self.logger.error(
                    "Failed to initialize Qdrant client",
                    error=str(e),
                )
                raise
    
    async def _ensure_embedder(self) -> None:
        """Ensure embedding function is initialized."""
        if self._embed_function is None:
            try:
                # Try to use OpenAI embeddings
                if self._settings.openai_api_key:
                    from openai import AsyncOpenAI
                    
                    client = AsyncOpenAI(api_key=self._settings.openai_api_key)
                    
                    async def embed(texts: list[str]) -> list[list[float]]:
                        response = await client.embeddings.create(
                            model=self._embedding_model,
                            input=texts,
                        )
                        return [item.embedding for item in response.data]
                    
                    self._embed_function = embed
                else:
                    # Fallback to a simple mock embedder for development
                    import hashlib
                    
                    def mock_embed(texts: list[str]) -> list[list[float]]:
                        embeddings = []
                        for text in texts:
                            # Create deterministic pseudo-embedding from text hash
                            hash_bytes = hashlib.sha256(text.encode()).digest()
                            embedding = [
                                (b - 128) / 128.0
                                for b in hash_bytes[:self._settings.embedding_dimension // 8]
                            ] * 8
                            # Pad/truncate to exact dimension
                            embedding = embedding[:self._settings.embedding_dimension]
                            while len(embedding) < self._settings.embedding_dimension:
                                embedding.append(0.0)
                            embeddings.append(embedding)
                        return embeddings
                    
                    async def async_mock_embed(texts: list[str]) -> list[list[float]]:
                        return mock_embed(texts)
                    
                    self._embed_function = async_mock_embed
                    self.logger.warning("Using mock embedder - set OPENAI_API_KEY for real embeddings")
            except Exception as e:
                self.logger.error("Failed to initialize embedder", error=str(e))
                raise
    
    async def index_character(
        self,
        character_data: dict[str, Any],
    ) -> IndexingStats:
        """
        Index all knowledge for a character.
        
        Args:
            character_data: Dictionary containing character data
                Expected keys: id, name, essence, knowledge, relationships, style
                
        Returns:
            IndexingStats with operation results
        """
        await self._ensure_client()
        await self._ensure_embedder()
        
        start_time = datetime.now()
        stats = IndexingStats()
        
        character_id = character_data.get("id", str(uuid4()))
        
        self.logger.info(
            "Starting character indexing",
            character_id=character_id,
            character_name=character_data.get("name", "Unknown"),
        )
        
        # Extract and chunk knowledge by tier
        chunks = []
        
        # Tier 1: Essence
        if "essence" in character_data:
            essence_chunks = self._extract_essence_chunks(
                character_id, character_data["essence"]
            )
            chunks.extend(essence_chunks)
            stats.by_tier["essence"] = len(essence_chunks)
        
        # Tier 2: Knowledge
        if "knowledge" in character_data:
            knowledge_chunks = self._extract_knowledge_chunks(
                character_id, character_data["knowledge"]
            )
            chunks.extend(knowledge_chunks)
            stats.by_tier["knowledge"] = len(knowledge_chunks)
        
        # Tier 3: Relationships
        if "relationships" in character_data:
            rel_chunks = self._extract_relationship_chunks(
                character_id, character_data["relationships"]
            )
            chunks.extend(rel_chunks)
            stats.by_tier["relationships"] = len(rel_chunks)
        
        # Tier 4: Style
        if "style" in character_data:
            style_chunks = self._extract_style_chunks(
                character_id, character_data["style"]
            )
            chunks.extend(style_chunks)
            stats.by_tier["style"] = len(style_chunks)
        
        stats.total_chunks = len(chunks)
        
        # Generate embeddings in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            try:
                texts = [c.content for c in batch]
                embeddings = await self._embed_function(texts)
                
                for chunk, embedding in zip(batch, embeddings):
                    chunk.embedding = embedding
                
                # Index batch in Qdrant
                await self._index_batch(batch)
                stats.indexed_chunks += len(batch)
                
            except Exception as e:
                self.logger.error(
                    "Failed to index batch",
                    batch_start=i,
                    error=str(e),
                )
                stats.failed_chunks += len(batch)
        
        stats.duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        self.logger.info(
            "Completed character indexing",
            character_id=character_id,
            stats=stats.model_dump(),
        )
        
        return stats
    
    def _extract_essence_chunks(
        self,
        character_id: str,
        essence: dict[str, Any],
    ) -> list[KnowledgeChunk]:
        """Extract essence tier chunks."""
        chunks = []
        
        # Personality description
        if "personality" in essence:
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.ESSENCE,
                content=f"Personality: {essence['personality']}",
                metadata={"aspect": "personality"},
            ))
        
        # Values
        if "values" in essence:
            values_text = ", ".join(essence["values"]) if isinstance(essence["values"], list) else essence["values"]
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.ESSENCE,
                content=f"Core values: {values_text}",
                metadata={"aspect": "values"},
            ))
        
        # Motivations
        if "motivations" in essence:
            for i, motivation in enumerate(essence.get("motivations", [])):
                chunks.append(KnowledgeChunk(
                    character_id=character_id,
                    tier=KnowledgeTier.ESSENCE,
                    content=f"Motivation: {motivation}",
                    metadata={"aspect": "motivation", "priority": i + 1},
                ))
        
        # Background
        if "background" in essence:
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.ESSENCE,
                content=f"Background: {essence['background']}",
                metadata={"aspect": "background"},
            ))
        
        return chunks
    
    def _extract_knowledge_chunks(
        self,
        character_id: str,
        knowledge: dict[str, Any],
    ) -> list[KnowledgeChunk]:
        """Extract knowledge tier chunks."""
        chunks = []
        
        # Abilities
        for ability in knowledge.get("abilities", []):
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.KNOWLEDGE,
                content=f"Ability: {ability}",
                metadata={"aspect": "ability"},
            ))
        
        # History
        for event in knowledge.get("history", []):
            if isinstance(event, dict):
                event_text = f"{event.get('period', 'Unknown period')}: {event.get('description', event)}"
            else:
                event_text = str(event)
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.KNOWLEDGE,
                content=f"History: {event_text}",
                metadata={"aspect": "history"},
            ))
        
        # Lore
        for lore in knowledge.get("lore", []):
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.KNOWLEDGE,
                content=f"Lore: {lore}",
                metadata={"aspect": "lore"},
            ))
        
        return chunks
    
    def _extract_relationship_chunks(
        self,
        character_id: str,
        relationships: dict[str, Any] | list[dict[str, Any]],
    ) -> list[KnowledgeChunk]:
        """Extract relationship tier chunks."""
        chunks = []
        
        rel_list = relationships if isinstance(relationships, list) else relationships.get("characters", [])
        
        for rel in rel_list:
            if isinstance(rel, dict):
                rel_text = f"Relationship with {rel.get('name', 'Unknown')}: {rel.get('description', '')} (Type: {rel.get('type', 'unknown')})"
            else:
                rel_text = str(rel)
            
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.RELATIONSHIPS,
                content=rel_text,
                metadata={"aspect": "relationship"},
            ))
        
        return chunks
    
    def _extract_style_chunks(
        self,
        character_id: str,
        style: dict[str, Any],
    ) -> list[KnowledgeChunk]:
        """Extract style tier chunks."""
        chunks = []
        
        # Speech patterns
        if "speech_patterns" in style:
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.STYLE,
                content=f"Speech patterns: {style['speech_patterns']}",
                metadata={"aspect": "speech"},
            ))
        
        # Common phrases
        for phrase in style.get("common_phrases", []):
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.STYLE,
                content=f"Common phrase: '{phrase}'",
                metadata={"aspect": "phrase"},
            ))
        
        # Vocabulary
        if "vocabulary" in style:
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.STYLE,
                content=f"Vocabulary style: {style['vocabulary']}",
                metadata={"aspect": "vocabulary"},
            ))
        
        # Tone
        if "tone" in style:
            chunks.append(KnowledgeChunk(
                character_id=character_id,
                tier=KnowledgeTier.STYLE,
                content=f"Communication tone: {style['tone']}",
                metadata={"aspect": "tone"},
            ))
        
        return chunks
    
    async def _index_batch(self, chunks: list[KnowledgeChunk]) -> None:
        """Index a batch of chunks into Qdrant."""
        if not self._qdrant_client:
            return
        
        from qdrant_client.models import PointStruct
        
        points = [
            PointStruct(
                id=chunk.chunk_id,
                vector=chunk.embedding,
                payload={
                    "character_id": chunk.character_id,
                    "tier": chunk.tier.value,
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                    "created_at": chunk.created_at.isoformat(),
                },
            )
            for chunk in chunks
            if chunk.embedding is not None
        ]
        
        if points:
            self._qdrant_client.upsert(
                collection_name=self._collection_name,
                points=points,
            )
    
    async def delete_character(self, character_id: str) -> int:
        """
        Delete all knowledge for a character.
        
        Args:
            character_id: Character to delete
            
        Returns:
            Number of chunks deleted
        """
        await self._ensure_client()
        
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        result = self._qdrant_client.delete(
            collection_name=self._collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="character_id",
                        match=MatchValue(value=character_id),
                    ),
                ],
            ),
        )
        
        self.logger.info(
            "Deleted character knowledge",
            character_id=character_id,
        )
        
        return result.operation_id if result else 0
