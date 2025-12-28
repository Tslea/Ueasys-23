"""
Base STT Provider - Abstract base class for STT integrations.

This module provides the base interface for STT providers,
ensuring consistent behavior across different STT services.

Example:
    >>> class MySTTProvider(STTProvider):
    ...     async def transcribe(self, audio: bytes) -> STTResponse:
    ...         # Implementation
    ...         pass
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Literal, List

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger

logger = get_logger(__name__)


class STTLanguage(str, Enum):
    """Supported languages for STT."""
    AUTO = "auto"
    ENGLISH = "en"
    ITALIAN = "it"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    CHINESE = "zh"
    KOREAN = "ko"
    ARABIC = "ar"


class STTConfig(BaseModel):
    """
    Configuration for STT providers.
    
    Attributes:
        model: Model to use (provider-specific)
        language: Expected language (auto-detect if not specified)
        device: Compute device ("cuda", "cpu", "auto")
        compute_type: Computation precision
        beam_size: Beam search size for decoding
        vad_filter: Enable voice activity detection filtering
    """
    model: str = Field(default="base", description="STT model size")
    language: STTLanguage = Field(default=STTLanguage.AUTO, description="Input language")
    device: Literal["cuda", "cpu", "auto"] = Field(default="auto", description="Compute device")
    compute_type: Literal["float16", "float32", "int8"] = Field(
        default="float16", 
        description="Computation precision"
    )
    beam_size: int = Field(default=5, ge=1, le=10, description="Beam search size")
    vad_filter: bool = Field(default=True, description="Enable VAD filtering")
    vad_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="VAD threshold")


class TranscriptionSegment(BaseModel):
    """A segment of transcribed text with timing info."""
    text: str
    start: float  # Start time in seconds
    end: float    # End time in seconds
    confidence: float = 1.0


class STTResponse(BaseModel):
    """
    Response from STT transcription.
    
    Attributes:
        text: Full transcribed text
        segments: List of transcription segments with timing
        language: Detected/used language
        language_probability: Confidence in language detection
        duration_seconds: Audio duration
        model: Model used
        transcribed_at: Timestamp of transcription
    """
    text: str
    segments: List[TranscriptionSegment] = Field(default_factory=list)
    language: str
    language_probability: float = 1.0
    duration_seconds: float
    model: str
    transcribed_at: datetime = Field(default_factory=datetime.utcnow)


class STTProvider(ABC):
    """
    Abstract base class for STT providers.
    
    Subclasses must implement:
        - transcribe(): Transcribe audio to text
        - transcribe_file(): Transcribe audio file
        - is_available(): Check if provider is available
    """
    
    def __init__(self, config: Optional[STTConfig] = None):
        """
        Initialize the STT provider.
        
        Args:
            config: STT configuration. Uses defaults if not provided.
        """
        self.config = config or STTConfig()
        self._initialized = False
        self._model = None
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the STT model.
        
        Should be called before first use. Handles lazy loading
        to avoid loading models until needed.
        
        Raises:
            RuntimeError: If initialization fails
        """
        pass
    
    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
    ) -> STTResponse:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: Raw audio bytes (WAV, MP3, etc.)
            language: Language hint (overrides config)
            
        Returns:
            STTResponse with transcription
            
        Raises:
            RuntimeError: If transcription fails
            ValueError: If audio format is invalid
        """
        pass
    
    @abstractmethod
    async def transcribe_file(
        self,
        audio_path: Path,
        language: Optional[str] = None,
    ) -> STTResponse:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language hint (overrides config)
            
        Returns:
            STTResponse with transcription
            
        Raises:
            RuntimeError: If transcription fails
            FileNotFoundError: If audio file doesn't exist
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
    
    async def cleanup(self) -> None:
        """
        Cleanup resources.
        
        Should be called when provider is no longer needed.
        """
        self._model = None
        self._initialized = False
        logger.info(f"STT provider {self.__class__.__name__} cleaned up")
