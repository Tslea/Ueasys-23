"""
Voice API Routes - Endpoints for TTS and STT operations.

This module provides REST endpoints for voice interactions:
    - POST /api/v1/voice/transcribe - Convert speech to text
    - POST /api/v1/voice/speak - Convert text to speech
    - GET /api/v1/voice/voices - List available voices
    - GET /api/v1/voice/status - Get voice service status

Example:
    >>> # Transcribe audio
    >>> response = requests.post(
    ...     "/api/v1/voice/transcribe",
    ...     files={"audio": open("user_audio.wav", "rb")}
    ... )
    >>> print(response.json()["text"])
    
    >>> # Generate speech
    >>> response = requests.post(
    ...     "/api/v1/voice/speak",
    ...     json={"text": "Hello traveler", "character_id": "gandalf"}
    ... )
    >>> # Returns audio bytes
"""

import base64
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from src.config.logging_config import get_logger
from src.config.settings import get_settings
from src.services.voice_service import get_voice_service, VoiceService

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================

class TranscribeResponse(BaseModel):
    """Response from transcription endpoint."""
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")
    language_probability: float = Field(..., description="Language detection confidence")
    duration_seconds: float = Field(..., description="Audio duration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "What wisdom do you have for me, Gandalf?",
                "language": "en",
                "language_probability": 0.98,
                "duration_seconds": 3.5
            }
        }


class SpeakRequest(BaseModel):
    """Request for speech generation."""
    text: str = Field(..., description="Text to convert to speech", max_length=5000)
    character_id: Optional[str] = Field(None, description="Character voice to use")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "A wizard is never late, nor is he early. He arrives precisely when he means to.",
                "character_id": "gandalf"
            }
        }


class SpeakResponse(BaseModel):
    """Response from speech generation (JSON mode)."""
    audio_base64: str = Field(..., description="Base64-encoded audio data")
    sample_rate: int = Field(..., description="Audio sample rate")
    duration_seconds: float = Field(..., description="Audio duration")
    format: str = Field(..., description="Audio format (wav, mp3, etc.)")
    voice_id: str = Field(..., description="Voice used")


class VoiceStatusResponse(BaseModel):
    """Voice service status."""
    initialized: bool
    tts: dict
    stt: dict
    voice_clip_dir: str


class VoiceListResponse(BaseModel):
    """List of available voices."""
    voices: list[str]
    count: int


# =============================================================================
# Helper Functions
# =============================================================================

def _get_voice_service() -> VoiceService:
    """Get voice service, checking if enabled."""
    voice_service = get_voice_service()
    
    # Check feature flags
    tts_enabled = getattr(settings, 'tts_enabled', True)
    stt_enabled = getattr(settings, 'stt_enabled', True)
    
    if not tts_enabled and not stt_enabled:
        raise HTTPException(
            status_code=503,
            detail="Voice features are disabled"
        )
    
    return voice_service


# =============================================================================
# Endpoints
# =============================================================================

@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    summary="Transcribe audio to text",
    description="Convert speech audio to text using Whisper STT"
)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, OGG, etc.)"),
    language: Optional[str] = Query(None, description="Language hint (e.g., 'en', 'it')")
):
    """
    Transcribe audio file to text.
    
    Accepts audio files in common formats (WAV, MP3, OGG, FLAC).
    Language can be auto-detected or specified for better accuracy.
    
    Returns:
        TranscribeResponse with transcribed text
    """
    voice_service = _get_voice_service()
    
    if not voice_service.stt_enabled:
        raise HTTPException(
            status_code=503,
            detail="Speech-to-text is not enabled"
        )
    
    # Read audio data
    audio_data = await audio.read()
    
    if not audio_data:
        raise HTTPException(
            status_code=400,
            detail="Empty audio file"
        )
    
    logger.info(
        "Transcription request",
        filename=audio.filename,
        size=len(audio_data),
        content_type=audio.content_type,
        language=language
    )
    
    try:
        result = await voice_service.transcribe(audio_data, language)
        
        return TranscribeResponse(
            text=result.text,
            language=result.language,
            language_probability=result.language_probability,
            duration_seconds=result.duration_seconds
        )
        
    except Exception as e:
        logger.error("Transcription failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post(
    "/speak",
    summary="Generate speech from text",
    description="Convert text to speech using character voice"
)
async def generate_speech(
    request: SpeakRequest,
    format: str = Query("wav", description="Output format: wav, mp3"),
    return_json: bool = Query(False, description="Return JSON with base64 instead of binary")
):
    """
    Generate speech from text.
    
    Uses character's voice clip for voice cloning if available.
    Can return raw audio bytes or JSON with base64-encoded audio.
    
    Returns:
        Audio bytes (default) or SpeakResponse JSON
    """
    voice_service = _get_voice_service()
    
    if not voice_service.tts_enabled:
        raise HTTPException(
            status_code=503,
            detail="Text-to-speech is not enabled"
        )
    
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    logger.info(
        "Speech generation request",
        text_length=len(request.text),
        character_id=request.character_id,
        format=format
    )
    
    try:
        result = await voice_service.speak(
            text=request.text,
            character_id=request.character_id
        )
        
        if return_json:
            return SpeakResponse(
                audio_base64=base64.b64encode(result.audio_data).decode(),
                sample_rate=result.sample_rate,
                duration_seconds=result.duration_seconds,
                format=result.format.value,
                voice_id=result.voice_id
            )
        
        # Return raw audio
        media_type = {
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "ogg": "audio/ogg",
            "flac": "audio/flac"
        }.get(result.format.value, "audio/wav")
        
        return Response(
            content=result.audio_data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=speech.{result.format.value}",
                "X-Audio-Duration": str(result.duration_seconds),
                "X-Audio-Sample-Rate": str(result.sample_rate),
                "X-Voice-Id": result.voice_id
            }
        )
        
    except Exception as e:
        logger.error("Speech generation failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Speech generation failed: {str(e)}"
        )


@router.get(
    "/voices",
    response_model=VoiceListResponse,
    summary="List available voices",
    description="Get list of available voice IDs for speech generation"
)
async def list_voices():
    """
    List available voices.
    
    Returns voices from:
        - Voice clip directory (character voice clips)
        - TTS provider built-in voices
    """
    voice_service = _get_voice_service()
    
    try:
        voices = await voice_service.list_available_voices()
        
        return VoiceListResponse(
            voices=voices,
            count=len(voices)
        )
        
    except Exception as e:
        logger.error("Failed to list voices", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list voices: {str(e)}"
        )


@router.get(
    "/status",
    response_model=VoiceStatusResponse,
    summary="Get voice service status",
    description="Check status of TTS and STT providers"
)
async def get_voice_status():
    """
    Get voice service status.
    
    Returns initialization state and provider availability.
    """
    voice_service = _get_voice_service()
    
    status = voice_service.get_status()
    
    return VoiceStatusResponse(**status)


@router.post(
    "/speak/{character_id}",
    summary="Generate speech for specific character",
    description="Shortcut endpoint for character-specific speech"
)
async def speak_as_character(
    character_id: str,
    text: str = Query(..., description="Text to speak", max_length=5000)
):
    """
    Generate speech as a specific character.
    
    Convenience endpoint that uses character's voice clip.
    
    Args:
        character_id: Character identifier (gandalf, galadriel, etc.)
        text: Text to convert to speech
        
    Returns:
        Audio bytes
    """
    voice_service = _get_voice_service()
    
    if not voice_service.tts_enabled:
        raise HTTPException(
            status_code=503,
            detail="Text-to-speech is not enabled"
        )
    
    # Check if character has voice clip
    if not voice_service.has_voice_clip(character_id):
        logger.warning(f"No voice clip for character: {character_id}")
    
    try:
        result = await voice_service.speak(
            text=text,
            character_id=character_id
        )
        
        return Response(
            content=result.audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename={character_id}_speech.wav",
                "X-Audio-Duration": str(result.duration_seconds),
                "X-Character-Id": character_id
            }
        )
        
    except Exception as e:
        logger.error(f"Speech generation failed for {character_id}", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Speech generation failed: {str(e)}"
        )
