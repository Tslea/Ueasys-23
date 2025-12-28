"""
Document Indexer Service.
Indexes uploaded documents into Qdrant for RAG retrieval.

When a user uploads books/documents for a character, this service:
1. Chunks the document into smaller pieces
2. Creates embeddings for each chunk
3. Stores them in Qdrant associated with the character_id

This allows the character to "remember" the content of uploaded documents.
"""

import re
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.config.settings import get_settings
from src.rag.knowledge_indexer import KnowledgeTier, KnowledgeChunk

logger = get_logger(__name__)


class DocumentChunk(BaseModel):
    """A chunk from an uploaded document."""
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    character_id: str
    document_name: str
    content: str
    chunk_index: int
    total_chunks: int
    tier: KnowledgeTier = KnowledgeTier.KNOWLEDGE
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentIndexingResult(BaseModel):
    """Result of document indexing."""
    document_name: str
    total_chunks: int
    indexed_chunks: int
    failed_chunks: int
    character_id: str


class DocumentIndexer(LoggerMixin):
    """
    Indexes uploaded documents into Qdrant for character knowledge.
    
    This service handles:
    - Text chunking with overlap
    - Embedding generation
    - Qdrant indexing with character_id association
    
    Example:
        >>> indexer = DocumentIndexer()
        >>> result = await indexer.index_document(
        ...     character_id="babbo-natale-123",
        ...     document_name="storia_babbo_natale.txt",
        ...     content="C'era una volta al Polo Nord..."
        ... )
    """
    
    def __init__(
        self,
        collection_name: str = "fantasy_characters",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        self._settings = get_settings()
        self._collection_name = collection_name
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        
        # Lazy initialization
        self._qdrant_client = None
        self._embed_function = None
        
        self.logger.info(
            "Initialized DocumentIndexer",
            collection=collection_name,
            chunk_size=chunk_size,
            overlap=chunk_overlap,
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
                self.logger.error("Failed to initialize Qdrant client", error=str(e))
                raise
    
    def _is_openai_configured(self) -> bool:
        """Check if OpenAI API key is properly configured."""
        key = self._settings.openai_api_key
        return bool(key and key not in ["", "sk-your-openai-api-key", "sk-your-api-key"])
    
    async def _ensure_embedder(self) -> None:
        """Ensure embedding function is initialized."""
        if self._embed_function is None:
            try:
                # Determine which provider to use
                use_openai = (
                    self._settings.embedding_provider == "openai" 
                    and self._is_openai_configured()
                )
                use_local = (
                    self._settings.embedding_provider == "local"
                    or not self._is_openai_configured()  # Fallback to local if OpenAI not configured
                )
                
                if use_openai:
                    from openai import AsyncOpenAI
                    
                    client = AsyncOpenAI(api_key=self._settings.openai_api_key)
                    self.logger.info("Using OpenAI embeddings", model=self._settings.embedding_model)
                    
                    async def embed(texts: list[str]) -> list[list[float]]:
                        response = await client.embeddings.create(
                            model=self._settings.embedding_model,
                            input=texts,
                        )
                        return [item.embedding for item in response.data]
                    
                    self._embed_function = embed
                    
                elif use_local:
                    # Use sentence-transformers for local embeddings (free, no API key needed)
                    from sentence_transformers import SentenceTransformer
                    
                    model = SentenceTransformer(self._settings.local_embedding_model)
                    self.logger.info(
                        "Using local embeddings (sentence-transformers)",
                        model=self._settings.local_embedding_model
                    )
                    
                    async def local_embed(texts: list[str]) -> list[list[float]]:
                        embeddings = model.encode(texts, convert_to_numpy=True)
                        return [emb.tolist() for emb in embeddings]
                    
                    self._embed_function = local_embed
                    
            except Exception as e:
                self.logger.error("Failed to initialize embedder", error=str(e))
                raise
    
    def _chunk_text(self, text: str) -> list[str]:
        """
        Split text into overlapping chunks.
        
        Uses sentence boundaries when possible to avoid
        cutting in the middle of sentences.
        """
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) <= self._chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self._chunk_size
            
            if end < len(text):
                # Try to find a sentence boundary
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                last_boundary = max(last_period, last_newline)
                
                if last_boundary > start + self._chunk_size // 2:
                    end = last_boundary + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start with overlap
            start = end - self._chunk_overlap
            # Ensure we always make progress to avoid infinite loop
            if start <= (end - self._chunk_size):
                start = end
        
        return chunks
    
    async def index_document(
        self,
        character_id: str,
        document_name: str,
        content: str,
        tier: KnowledgeTier = KnowledgeTier.KNOWLEDGE,
        metadata: Optional[dict[str, Any]] = None,
    ) -> DocumentIndexingResult:
        """
        Index a single document for a character.
        
        Args:
            character_id: The character this document belongs to
            document_name: Name of the document
            content: Full text content of the document
            tier: Knowledge tier (default: KNOWLEDGE)
            metadata: Additional metadata
            
        Returns:
            DocumentIndexingResult with indexing statistics
        """
        await self._ensure_client()
        await self._ensure_embedder()
        
        self.logger.info(
            "Indexing document",
            character_id=character_id,
            document=document_name,
            content_length=len(content),
        )
        
        # Chunk the document
        text_chunks = self._chunk_text(content)
        total_chunks = len(text_chunks)
        
        if total_chunks == 0:
            return DocumentIndexingResult(
                document_name=document_name,
                total_chunks=0,
                indexed_chunks=0,
                failed_chunks=0,
                character_id=character_id,
            )
        
        # Create document chunks
        doc_chunks = [
            DocumentChunk(
                character_id=character_id,
                document_name=document_name,
                content=chunk,
                chunk_index=i,
                total_chunks=total_chunks,
                tier=tier,
                metadata={
                    **(metadata or {}),
                    "source": "uploaded_document",
                    "document_name": document_name,
                    "indexed_at": datetime.now().isoformat(),
                },
            )
            for i, chunk in enumerate(text_chunks)
        ]
        
        # Generate embeddings
        indexed = 0
        failed = 0
        batch_size = 50
        
        for i in range(0, len(doc_chunks), batch_size):
            batch = doc_chunks[i:i + batch_size]
            
            try:
                texts = [c.content for c in batch]
                embeddings = await self._embed_function(texts)
                
                # Prepare points for Qdrant
                from qdrant_client.models import PointStruct
                
                points = [
                    PointStruct(
                        id=chunk.chunk_id,
                        vector=embedding,
                        payload={
                            "character_id": chunk.character_id,
                            "tier": chunk.tier.value,
                            "content": chunk.content,
                            "document_name": chunk.document_name,
                            "chunk_index": chunk.chunk_index,
                            "total_chunks": chunk.total_chunks,
                            "source": "uploaded_document",
                            **chunk.metadata,
                        },
                    )
                    for chunk, embedding in zip(batch, embeddings)
                ]
                
                # Upsert to Qdrant
                self._qdrant_client.upsert(
                    collection_name=self._collection_name,
                    points=points,
                )
                
                indexed += len(batch)
                
            except Exception as e:
                self.logger.error(
                    "Failed to index batch",
                    error=str(e),
                    batch_start=i,
                )
                failed += len(batch)
        
        self.logger.info(
            "Document indexing complete",
            character_id=character_id,
            document=document_name,
            indexed=indexed,
            failed=failed,
        )
        
        return DocumentIndexingResult(
            document_name=document_name,
            total_chunks=total_chunks,
            indexed_chunks=indexed,
            failed_chunks=failed,
            character_id=character_id,
        )
    
    async def index_multiple_documents(
        self,
        character_id: str,
        documents: list[dict[str, str]],
    ) -> list[DocumentIndexingResult]:
        """
        Index multiple documents for a character.
        
        Args:
            character_id: The character ID
            documents: List of {"name": ..., "content": ...}
            
        Returns:
            List of indexing results
        """
        results = []
        
        for doc in documents:
            result = await self.index_document(
                character_id=character_id,
                document_name=doc.get("name", "unknown"),
                content=doc.get("content", ""),
            )
            results.append(result)
        
        return results
    
    async def delete_character_documents(self, character_id: str) -> int:
        """
        Delete all indexed documents for a character.
        
        Args:
            character_id: The character ID
            
        Returns:
            Number of points deleted
        """
        await self._ensure_client()
        
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Delete all points with this character_id
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
            "Deleted character documents",
            character_id=character_id,
        )
        
        return result
    
    async def get_character_document_count(self, character_id: str) -> int:
        """Get count of indexed chunks for a character."""
        await self._ensure_client()
        
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        result = self._qdrant_client.count(
            collection_name=self._collection_name,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="character_id",
                        match=MatchValue(value=character_id),
                    ),
                ],
            ),
        )
        
        return result.count
