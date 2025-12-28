"""
Base TTS Provider - Abstract base class for TTS integrations.

This module provides the base interface for TTS providers,
ensuring consistent behavior across different TTS services.

Example:
    >>> class MyTTSProvider(TTSProvider):
    ...     async def generate(self, text: str, voice_id: str) -> TTSResponse:
    ...         # Implementation
    ...         pass
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Literal

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger

logger = get_logger(__name__)


class AudioFormat(str, Enum):
    """Supported audio output formats."""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"


class TTSConfig(BaseModel):
    """
    Configuration for TTS providers.
    
    Attributes:
        model: Model to use (provider-specific)
        sample_rate: Audio sample rate (Hz)
        audio_format: Output audio format
        voice_clip_dir: Directory containing voice clips for cloning
        device: Compute device ("cuda", "cpu", "auto")
        use_float16: Use float16 for reduced VRAM usage
    """
    model: str = Field(default="turbo", description="TTS model variant")
    sample_rate: int = Field(default=24000, description="Audio sample rate")
    audio_format: AudioFormat = Field(default=AudioFormat.WAV, description="Output format")
    voice_clip_dir: Path = Field(
        default=Path("data/voice_clips"), 
        description="Directory for voice clips"
    )
    device: Literal["cuda", "cpu", "auto"] = Field(
        default="auto", 
        description="Compute device"
    )
    use_float16: bool = Field(default=True, description="Use float16 for lower VRAM")
    exaggeration: float = Field(default=0.5, ge=0.0, le=1.0, description="Voice exaggeration")
    cfg_weight: float = Field(default=0.5, ge=0.0, le=1.0, description="CFG weight")


class TTSResponse(BaseModel):
    """
    Response from TTS generation.
    
    Attributes:
        audio_data: Raw audio bytes
        sample_rate: Audio sample rate
        duration_seconds: Audio duration
        format: Audio format
        voice_id: Voice used for generation
        model: Model used
        generated_at: Timestamp of generation
    """
    audio_data: bytes
    sample_rate: int
    duration_seconds: float
    format: AudioFormat
    voice_id: str
    model: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True


class TTSProvider(ABC):
    """
    Abstract base class for TTS providers.
    
    Subclasses must implement:
        - generate(): Generate speech from text
        - list_voices(): List available voices
        - is_available(): Check if provider is available
    """
    
    def __init__(self, config: Optional[TTSConfig] = None):
        """
        Initialize the TTS provider.
        
        Args:
            config: TTS configuration. Uses defaults if not provided.
        """
        self.config = config or TTSConfig()
        self._initialized = False
        self._model = None
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the TTS model.
        
        Should be called before first use. Handles lazy loading
        to avoid loading models until needed.
        
        Raises:
            RuntimeError: If initialization fails
        """
        pass
    
    @abstractmethod
    async def generate(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        voice_clip_path: Optional[Path] = None,
    ) -> TTSResponse:
        """
        Generate speech from text.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice identifier (character name or voice preset)
            voice_clip_path: Optional path to voice clip for cloning
            
        Returns:
            TTSResponse with audio data
            
        Raises:
            RuntimeError: If generation fails
            ValueError: If voice_id is invalid
        """
        pass
    
    @abstractmethod
    async def list_voices(self) -> list[str]:
        """
        List available voices.
        
        Returns:
            List of voice identifiers
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is available and properly configured.
        
        Returns:
            True if provider can be used
        """
        pass
    
    async def generate_to_file(
        self,
        text: str,
        output_path: Path,
        voice_id: Optional[str] = None,
        voice_clip_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate speech and save to file.
        
        Args:
            text: Text to convert
            output_path: Path to save audio file
            voice_id: Voice identifier
            voice_clip_path: Optional voice clip for cloning
            
        Returns:
            Path to saved audio file
        """
        response = await self.generate(text, voice_id, voice_clip_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.audio_data)
        
        logger.info(
            "TTS audio saved",
            path=str(output_path),
            duration=response.duration_seconds,
            voice=voice_id
        )
        
        return output_path
    
    def _get_voice_clip_path(self, voice_id: str) -> Optional[Path]:
        """
        Get the voice clip path for a character.
        
        Args:
            voice_id: Character/voice identifier
            
        Returns:
            Path to voice clip if exists, None otherwise
        """
        clip_dir = self.config.voice_clip_dir
        
        # Try common extensions
        for ext in [".wav", ".mp3", ".ogg", ".flac"]:
            clip_path = clip_dir / f"{voice_id}{ext}"
            if clip_path.exists():
                return clip_path
        
        return None
    
    async def cleanup(self) -> None:
        """
        Cleanup resources.
        
        Should be called when provider is no longer needed.
        """
        self._model = None
        self._initialized = False
        logger.info(f"TTS provider {self.__class__.__name__} cleaned up")
