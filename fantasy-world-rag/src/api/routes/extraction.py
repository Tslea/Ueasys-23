"""
Character Extraction API Route.
Uses AI (DeepSeek) to extract character information from uploaded documents.
Also indexes the documents into Qdrant for RAG retrieval.
"""

from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from src.llm import get_analysis_llm
from src.config.logging_config import get_logger
from src.services.document_indexer import DocumentIndexer

router = APIRouter(prefix="/extract-character", tags=["extraction"])
logger = get_logger(__name__)

# Global document indexer instance
_document_indexer: Optional[DocumentIndexer] = None


def get_document_indexer() -> DocumentIndexer:
    """Get or create document indexer singleton."""
    global _document_indexer
    if _document_indexer is None:
        _document_indexer = DocumentIndexer()
    return _document_indexer


class FileContent(BaseModel):
    """File content for extraction."""
    name: str
    content: str
    type: str


class ExtractionRequest(BaseModel):
    """Request body for character extraction."""
    files: List[FileContent]
    # Optional: if provided, documents will be indexed for this character
    character_id: Optional[str] = None
    # If True and character_id is set, index documents into Qdrant
    index_documents: bool = True


class PersonalityExtracted(BaseModel):
    """Extracted personality data."""
    traits: List[str] = []
    values: List[str] = []
    fears: List[str] = []
    desires: List[str] = []
    speaking_style: str = ""
    quirks: List[str] = []


class BackgroundExtracted(BaseModel):
    """Extracted background data."""
    origin: str = ""
    history: str = ""
    key_events: List[str] = []
    relationships: dict = {}


class KnowledgeExtracted(BaseModel):
    """Extracted knowledge data."""
    expertise: List[str] = []
    secrets: List[str] = []
    beliefs: List[str] = []
    opinions: dict = {}


class BehaviorExtracted(BaseModel):
    """Extracted behavior data."""
    goals: List[str] = []
    motivations: List[str] = []
    reactions: dict = {}
    decision_patterns: List[str] = []


class SpeakingStyleExtracted(BaseModel):
    """Extracted speaking style data."""
    tone: str = ""
    vocabulary: str = ""
    patterns: List[str] = []
    phrases: List[str] = []


class CharacterExtracted(BaseModel):
    """Extracted character data - aligned with backend Character model."""
    name: str = ""
    title: str = ""
    description: str = ""
    archetype: str = "hero"  # hero, mentor, guardian, trickster, sage, ruler, creator, innocent, explorer, rebel, lover, jester, everyman, caregiver, magician, outlaw, warrior, shadow
    alignment: str = "true_neutral"  # lawful_good, neutral_good, chaotic_good, etc.
    avatar_url: str = ""
    personality: PersonalityExtracted = PersonalityExtracted()
    speaking_style: SpeakingStyleExtracted = SpeakingStyleExtracted()
    background: BackgroundExtracted = BackgroundExtracted()


class ExtractionResponse(BaseModel):
    """Response from character extraction."""
    success: bool
    data: CharacterExtracted
    confidence: float
    suggestions: List[str]
    # Document indexing info
    documents_indexed: int = 0
    total_chunks: int = 0
    character_id_for_indexing: Optional[str] = None


EXTRACTION_PROMPT = """You are an expert character analyzer. Extract detailed character information from the following text.

Analyze the text and extract as much information as possible about the character, filling in the following structure:

1. **Basic Info**: name, title (honorific/epithet), description, archetype, alignment
2. **Personality**: traits, values, fears, desires, quirks
3. **Speaking Style**: tone, vocabulary, patterns, typical phrases
4. **Background**: origin, history, key events, relationships

For archetype, choose from: hero, mentor, guardian, trickster, sage, ruler, creator, innocent, explorer, rebel, lover, jester, everyman, caregiver, magician, outlaw, warrior, shadow
For alignment, choose from: lawful_good, neutral_good, chaotic_good, lawful_neutral, true_neutral, chaotic_neutral, lawful_evil, neutral_evil, chaotic_evil

Respond in JSON format with the following structure:
{
    "name": "Character Name",
    "title": "The Wise, The Grey, etc.",
    "description": "Brief description",
    "archetype": "mentor",
    "alignment": "neutral_good",
    "personality": {
        "traits": ["trait1", "trait2"],
        "values": ["value1", "value2"],
        "fears": ["fear1", "fear2"],
        "desires": ["desire1", "desire2"],
        "quirks": ["quirk1", "quirk2"]
    },
    "speaking_style": {
        "tone": "How they generally sound (e.g., wise and measured)",
        "vocabulary": "Type of words they use (e.g., archaic, formal)",
        "patterns": ["Repeats for emphasis", "Uses metaphors"],
        "phrases": ["A wizard is never late...", "Fly, you fools!"]
    },
    "background": {
        "origin": "Where they come from",
        "history": "Their life story",
        "key_events": ["event1", "event2"],
        "relationships": {"person1": "relationship description"}
    },
    "confidence": 0.0 to 1.0 (how confident you are in the extraction),
    "suggestions": ["suggestion for improvement 1", "suggestion 2"]
}

TEXT TO ANALYZE:
{text}

Remember to:
- Extract only what's explicitly mentioned or strongly implied
- Use Italian for field values if the source text is in Italian
- Set confidence based on how much information was found
- Provide helpful suggestions for missing or unclear information
- Choose the most appropriate archetype based on the character's role
"""


@router.post("", response_model=ExtractionResponse)
async def extract_character(request: ExtractionRequest) -> ExtractionResponse:
    """
    Extract character information from uploaded files using AI.
    
    This endpoint processes uploaded documents and uses an LLM to
    extract structured character data that can be used to create
    a new character in the system.
    
    If character_id is provided and index_documents=True, the documents
    will also be indexed into Qdrant for RAG retrieval, allowing the
    character to "remember" the content of the uploaded books/documents.
    """
    if not request.files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Combine all file contents
    combined_text = "\n\n---\n\n".join([
        f"File: {f.name}\n\n{f.content}" 
        for f in request.files
    ])
    
    # Store full content for indexing (before truncation)
    full_documents = [
        {"name": f.name, "content": f.content}
        for f in request.files
    ]
    
    # Truncate for LLM extraction if too long
    max_chars = 15000
    extraction_text = combined_text
    if len(extraction_text) > max_chars:
        extraction_text = extraction_text[:max_chars] + "\n\n[Text truncated...]"
    
    documents_indexed = 0
    total_chunks = 0
    
    try:
        # Get DeepSeek provider for analysis (best for extraction)
        llm = get_analysis_llm()
        logger.info("Using analysis LLM for character extraction", provider=type(llm).__name__)
        
        # Generate extraction
        prompt = EXTRACTION_PROMPT.format(text=extraction_text)
        
        response = await llm.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for more consistent extraction
        )
        
        # Parse JSON response
        import json
        import re
        
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
            else:
                json_str = response
        
        try:
            extracted = json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback to basic extraction
            return ExtractionResponse(
                success=False,
                data=CharacterExtracted(),
                confidence=0.0,
                suggestions=["AI extraction failed. Please fill in the details manually."]
            )
        
        # Build response
        confidence = extracted.get("confidence", 0.7)
        suggestions = extracted.get("suggestions", [])
        
        character_data = CharacterExtracted(
            name=extracted.get("name", ""),
            title=extracted.get("title", ""),
            description=extracted.get("description", ""),
            archetype=extracted.get("archetype", "hero"),
            alignment=extracted.get("alignment", "true_neutral"),
            personality=PersonalityExtracted(**extracted.get("personality", {})),
            speaking_style=SpeakingStyleExtracted(**extracted.get("speaking_style", {})),
            background=BackgroundExtracted(**extracted.get("background", {})),
        )
        
        # Index documents into Qdrant if character_id provided
        if request.character_id and request.index_documents:
            try:
                indexer = get_document_indexer()
                results = await indexer.index_multiple_documents(
                    character_id=request.character_id,
                    documents=full_documents,
                )
                
                documents_indexed = len(results)
                total_chunks = sum(r.indexed_chunks for r in results)
                
                logger.info(
                    "Indexed documents for character",
                    character_id=request.character_id,
                    documents=documents_indexed,
                    chunks=total_chunks,
                )
                
                suggestions.append(
                    f"✅ {documents_indexed} document(s) indexed ({total_chunks} chunks). "
                    "The character will remember this content!"
                )
                
            except Exception as idx_error:
                logger.error("Document indexing failed", error=str(idx_error))
                suggestions.append(
                    f"⚠️ Document indexing failed: {str(idx_error)}. "
                    "Character created but won't remember document content."
                )
        
        return ExtractionResponse(
            success=True,
            data=character_data,
            confidence=confidence,
            suggestions=suggestions,
            documents_indexed=documents_indexed,
            total_chunks=total_chunks,
            character_id_for_indexing=request.character_id,
        )
        
    except Exception as e:
        # Return a partial response with error info
        return ExtractionResponse(
            success=False,
            data=CharacterExtracted(),
            confidence=0.0,
            suggestions=[f"Extraction error: {str(e)}. Please fill in details manually."]
        )
