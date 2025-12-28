"""
Voice Service - Orchestration layer for TTS and STT.

This module coordinates text-to-speech and speech-to-text operations,
providing a unified interface for voice interactions with characters.

Example:
    >>> from src.services.voice_service import VoiceService
    >>> voice = VoiceService()
    >>> await voice.initialize()
    >>> 
    >>> # User speaks → text
    >>> transcription = await voice.transcribe(audio_bytes)
    >>> 
    >>> # Character responds → audio
    >>> audio = await voice.speak("Hello traveler", character_id="gandalf")
"""

import asyncio
from pathlib import Path
from typing import Optional

from src.config.logging_config import get_logger, LoggerMixin
from src.config.settings import get_settings
from src.llm.tts import TTSProvider, TTSConfig, TTSResponse, get_tts_provider
from src.llm.stt import STTProvider, STTConfig, STTResponse, get_stt_provider

logger = get_logger(__name__)
settings = get_settings()


class VoiceService(LoggerMixin):
    """
    Unified voice service for TTS and STT operations.
    
    Provides high-level methods for:
        - Transcribing user speech to text
        - Generating character speech from text
        - Managing voice clips for characters
        
    Features:
        - Lazy initialization (models loaded on first use)
        - Feature flags (disable TTS/STT independently)
        - Error resilience with graceful fallbacks
        - Character-specific voice cloning
        
    Example:
        >>> voice = VoiceService()
        >>> await voice.initialize()
        >>> 
        >>> # Transcribe user input
        >>> user_text = await voice.transcribe(audio_bytes)
        >>> print(user_text.text)  # "What wisdom do you have for me?"
        >>> 
        >>> # Generate character response audio
        >>> response_audio = await voice.speak(
        ...     "Seek not the treasure, but the journey",
        ...     character_id="gandalf"
        ... )
    """
    
    def __init__(
        self,
        tts_provider: Optional[str] = None,
        stt_provider: Optional[str] = None,
        tts_enabled: bool = True,
        stt_enabled: bool = True,
    ):
        """
        Initialize the voice service.
        
        Args:
            tts_provider: TTS provider name ("chatterbox", "elevenlabs")
            stt_provider: STT provider name ("whisper")
            tts_enabled: Enable TTS functionality
            stt_enabled: Enable STT functionality
        """
        self._tts_provider_name = tts_provider or getattr(settings, 'tts_provider', 'chatterbox')
        self._stt_provider_name = stt_provider or getattr(settings, 'stt_provider', 'whisper')
        
        self._tts_enabled = tts_enabled and getattr(settings, 'tts_enabled', True)
        self._stt_enabled = stt_enabled and getattr(settings, 'stt_enabled', True)
        
        self._tts: Optional[TTSProvider] = None
        self._stt: Optional[STTProvider] = None
        self._initialized = False
        
        # Voice clip directory
        self._voice_clip_dir = Path(getattr(settings, 'voice_clip_dir', 'data/voice_clips'))
        
    async def initialize(self) -> None:
        """
        Initialize TTS and STT providers.
        
        Models are loaded lazily, so this method may be slow on first call.
        Subsequent calls are no-ops.
        
        Raises:
            RuntimeError: If critical provider fails to initialize
        """
        if self._initialized:
            return
            
        init_tasks = []
        
        # Initialize TTS
        if self._tts_enabled:
            try:
                self._tts = get_tts_provider(self._tts_provider_name)
                init_tasks.append(self._init_tts())
            except Exception as e:
                logger.warning(f"TTS provider unavailable: {e}")
                self._tts_enabled = False
        
        # Initialize STT
        if self._stt_enabled:
            try:
                self._stt = get_stt_provider(self._stt_provider_name)
                init_tasks.append(self._init_stt())
            except Exception as e:
                logger.warning(f"STT provider unavailable: {e}")
                self._stt_enabled = False
        
        # Run initialization in parallel
        if init_tasks:
            results = await asyncio.gather(*init_tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Provider initialization failed: {result}")
        
        self._initialized = True
        
        logger.info(
            "VoiceService initialized",
            tts_enabled=self._tts_enabled,
            tts_provider=self._tts_provider_name if self._tts_enabled else None,
            stt_enabled=self._stt_enabled,
            stt_provider=self._stt_provider_name if self._stt_enabled else None
        )
    
    async def _init_tts(self) -> None:
        """Initialize TTS provider with error handling."""
        try:
            await self._tts.initialize()
            logger.info(f"TTS provider initialized: {self._tts_provider_name}")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self._tts_enabled = False
            raise
    
    async def _init_stt(self) -> None:
        """Initialize STT provider with error handling."""
        try:
            await self._stt.initialize()
            logger.info(f"STT provider initialized: {self._stt_provider_name}")
        except Exception as e:
            logger.error(f"Failed to initialize STT: {e}")
            self._stt_enabled = False
            raise
    
    # =========================================================================
    # Speech-to-Text (User Input)
    # =========================================================================
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
    ) -> STTResponse:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Raw audio bytes (WAV, MP3, etc.)
            language: Language hint for better accuracy
            
        Returns:
            STTResponse with transcription
            
        Raises:
            RuntimeError: If STT is disabled or fails
        """
        if not self._stt_enabled:
            raise RuntimeError("Speech-to-text is not enabled")
            
        if not self._initialized:
            await self.initialize()
        
        logger.debug(
            "Transcribing audio",
            audio_size=len(audio_data),
            language=language
        )
        
        try:
            result = await self._stt.transcribe(audio_data, language)
            
            logger.info(
                "Transcription complete",
                text_length=len(result.text),
                language=result.language,
                duration=result.duration_seconds
            )
            
            return result
            
        except Exception as e:
            logger.error("Transcription failed", error=str(e))
            raise
    
    async def transcribe_file(
        self,
        audio_path: Path,
        language: Optional[str] = None,
    ) -> STTResponse:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language hint
            
        Returns:
            STTResponse with transcription
        """
        if not self._stt_enabled:
            raise RuntimeError("Speech-to-text is not enabled")
            
        if not self._initialized:
            await self.initialize()
        
        return await self._stt.transcribe_file(audio_path, language)
    
    # =========================================================================
    # Text-to-Speech (Character Output)
    # =========================================================================
    
    async def speak(
        self,
        text: str,
        character_id: Optional[str] = None,
        voice_clip_path: Optional[Path] = None,
    ) -> TTSResponse:
        """
        Generate speech from text using character's voice.
        
        Args:
            text: Text to convert to speech
            character_id: Character name for voice selection
            voice_clip_path: Optional direct path to voice clip
            
        Returns:
            TTSResponse with audio data
            
        Raises:
            RuntimeError: If TTS is disabled or fails
        """
        if not self._tts_enabled:
            raise RuntimeError("Text-to-speech is not enabled")
            
        if not self._initialized:
            await self.initialize()
        
        # Try to find character voice clip if not provided
        if voice_clip_path is None and character_id:
            voice_clip_path = self._get_character_voice_clip(character_id)
        
        logger.debug(
            "Generating speech",
            text_length=len(text),
            character=character_id,
            voice_clip=str(voice_clip_path) if voice_clip_path else None
        )
        
        try:
            result = await self._tts.generate(
                text=text,
                voice_id=character_id,
                voice_clip_path=voice_clip_path
            )
            
            logger.info(
                "Speech generated",
                duration=result.duration_seconds,
                character=character_id
            )
            
            return result
            
        except Exception as e:
            logger.error("Speech generation failed", error=str(e))
            raise
    
    async def speak_to_file(
        self,
        text: str,
        output_path: Path,
        character_id: Optional[str] = None,
        voice_clip_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate speech and save to file.
        
        Args:
            text: Text to convert
            output_path: Path to save audio
            character_id: Character name
            voice_clip_path: Optional voice clip path
            
        Returns:
            Path to saved audio file
        """
        if not self._tts_enabled:
            raise RuntimeError("Text-to-speech is not enabled")
            
        if not self._initialized:
            await self.initialize()
            
        if voice_clip_path is None and character_id:
            voice_clip_path = self._get_character_voice_clip(character_id)
        
        return await self._tts.generate_to_file(
            text=text,
            output_path=output_path,
            voice_id=character_id,
            voice_clip_path=voice_clip_path
        )
    
    # =========================================================================
    # Voice Management
    # =========================================================================
    
    def _get_character_voice_clip(self, character_id: str) -> Optional[Path]:
        """
        Get the voice clip path for a character.
        
        Args:
            character_id: Character identifier
            
        Returns:
            Path to voice clip if exists, None otherwise
        """
        if not self._voice_clip_dir.exists():
            return None
            
        # Try common extensions
        for ext in [".wav", ".mp3", ".ogg", ".flac"]:
            clip_path = self._voice_clip_dir / f"{character_id}{ext}"
            if clip_path.exists():
                return clip_path
        
        return None
    
    async def list_available_voices(self) -> list[str]:
        """
        List available voices (voice clips + provider voices).
        
        Returns:
            List of voice identifiers
        """
        voices = set()
        
        # Get voice clips from directory
        if self._voice_clip_dir.exists():
            for ext in [".wav", ".mp3", ".ogg", ".flac"]:
                voices.update(f.stem for f in self._voice_clip_dir.glob(f"*{ext}"))
        
        # Get provider voices
        if self._tts_enabled and self._tts:
            try:
                provider_voices = await self._tts.list_voices()
                voices.update(provider_voices)
            except Exception:
                pass
        
        return sorted(voices)
    
    def has_voice_clip(self, character_id: str) -> bool:
        """
        Check if a character has a voice clip.
        
        Args:
            character_id: Character identifier
            
        Returns:
            True if voice clip exists
        """
        return self._get_character_voice_clip(character_id) is not None
    
    # =========================================================================
    # Status & Cleanup
    # =========================================================================
    
    @property
    def tts_enabled(self) -> bool:
        """Check if TTS is enabled and available."""
        return self._tts_enabled
    
    @property
    def stt_enabled(self) -> bool:
        """Check if STT is enabled and available."""
        return self._stt_enabled
    
    def get_status(self) -> dict:
        """
        Get service status.
        
        Returns:
            Status dictionary
        """
        return {
            "initialized": self._initialized,
            "tts": {
                "enabled": self._tts_enabled,
                "provider": self._tts_provider_name if self._tts_enabled else None,
                "available": self._tts.is_available() if self._tts else False,
            },
            "stt": {
                "enabled": self._stt_enabled,
                "provider": self._stt_provider_name if self._stt_enabled else None,
                "available": self._stt.is_available() if self._stt else False,
            },
            "voice_clip_dir": str(self._voice_clip_dir),
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources and free memory."""
        cleanup_tasks = []
        
        if self._tts:
            cleanup_tasks.append(self._tts.cleanup())
            
        if self._stt:
            cleanup_tasks.append(self._stt.cleanup())
            
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self._initialized = False
        logger.info("VoiceService cleaned up")


# Singleton instance for easy access
_voice_service: Optional[VoiceService] = None


def get_voice_service() -> VoiceService:
    """
    Get the global voice service instance.
    
    Returns:
        VoiceService singleton
    """
    global _voice_service
    
    if _voice_service is None:
        _voice_service = VoiceService()
    
    return _voice_service


async def init_voice_service() -> VoiceService:
    """
    Initialize and return the global voice service.
    
    Returns:
        Initialized VoiceService
    """
    service = get_voice_service()
    await service.initialize()
    return service
