"""
Whisper STT Provider - Local speech-to-text using faster-whisper.

faster-whisper is a reimplementation of Whisper using CTranslate2,
which is up to 4x faster than openai/whisper with comparable accuracy.

Example:
    >>> stt = WhisperSTT()
    >>> await stt.initialize()
    >>> response = await stt.transcribe(audio_bytes)
"""

import asyncio
import io
import tempfile
from pathlib import Path
from typing import Optional

from src.config.logging_config import get_logger
from src.llm.stt.base import (
    STTProvider, 
    STTConfig, 
    STTResponse, 
    STTLanguage,
    TranscriptionSegment
)

logger = get_logger(__name__)

# Lazy imports
_WhisperModel = None
_torch = None


def _lazy_import_whisper():
    """Lazy import faster-whisper dependencies."""
    global _WhisperModel, _torch
    
    if _WhisperModel is None:
        try:
            from faster_whisper import WhisperModel
            _WhisperModel = WhisperModel
        except ImportError:
            logger.error("faster-whisper not installed")
            raise ImportError(
                "faster-whisper is not installed. Run: pip install faster-whisper"
            )
    
    if _torch is None:
        import torch
        _torch = torch


class WhisperSTT(STTProvider):
    """
    Whisper STT provider using faster-whisper.
    
    Features:
        - Multiple model sizes (tiny, base, small, medium, large)
        - Multi-language support with auto-detection
        - Voice activity detection filtering
        - GPU acceleration with float16
        - CPU fallback
        
    Model sizes and VRAM requirements:
        - tiny: ~1GB
        - base: ~1GB
        - small: ~2GB
        - medium: ~5GB
        - large-v3: ~10GB
        
    Attributes:
        config: STT configuration
        _model: Loaded Whisper model
        _device: Active compute device
    """
    
    # Model size to identifier mapping
    MODEL_SIZES = {
        "tiny": "tiny",
        "base": "base",
        "small": "small",
        "medium": "medium",
        "large": "large-v3",
    }
    
    def __init__(self, config: Optional[STTConfig] = None):
        """Initialize Whisper STT provider."""
        super().__init__(config)
        self._device = None
        
    async def initialize(self) -> None:
        """
        Initialize the Whisper model.
        
        Loads model with appropriate device and precision settings.
        Falls back to CPU if CUDA is unavailable or OOM.
        
        Raises:
            RuntimeError: If model loading fails completely
        """
        if self._initialized:
            return
            
        _lazy_import_whisper()
        
        # Determine device
        device = self.config.device
        if device == "auto":
            device = "cuda" if _torch.cuda.is_available() else "cpu"
        
        # Resolve model name
        model_name = self.MODEL_SIZES.get(self.config.model, self.config.model)
        
        logger.info(
            f"Initializing Whisper STT",
            model=model_name,
            device=device,
            compute_type=self.config.compute_type
        )
        
        try:
            self._model = await asyncio.to_thread(
                _WhisperModel,
                model_name,
                device=device,
                compute_type=self.config.compute_type if device == "cuda" else "int8"
            )
            
            self._device = device
            self._initialized = True
            logger.info(f"Whisper STT initialized on {device}")
            
        except RuntimeError as e:
            if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
                logger.warning(f"CUDA failed, falling back to CPU: {e}")
                
                _torch.cuda.empty_cache()
                
                self._model = await asyncio.to_thread(
                    _WhisperModel,
                    model_name,
                    device="cpu",
                    compute_type="int8"
                )
                
                self._device = "cpu"
                self._initialized = True
                logger.info("Whisper STT initialized on CPU (slower but works)")
            else:
                raise RuntimeError(f"Failed to initialize Whisper: {e}") from e
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
    ) -> STTResponse:
        """
        Transcribe audio bytes to text.
        
        Args:
            audio_data: Raw audio bytes (WAV, MP3, OGG, etc.)
            language: Language hint (None for auto-detection)
            
        Returns:
            STTResponse with transcription
            
        Raises:
            RuntimeError: If transcription fails
        """
        if not self._initialized:
            await self.initialize()
        
        # Write audio to temp file (faster-whisper requires file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = Path(tmp.name)
        
        try:
            return await self.transcribe_file(tmp_path, language)
        finally:
            # Cleanup temp file
            tmp_path.unlink(missing_ok=True)
    
    async def transcribe_file(
        self,
        audio_path: Path,
        language: Optional[str] = None,
    ) -> STTResponse:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language hint (None for auto-detection)
            
        Returns:
            STTResponse with transcription
            
        Raises:
            RuntimeError: If transcription fails
            FileNotFoundError: If audio file doesn't exist
        """
        if not self._initialized:
            await self.initialize()
            
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Resolve language
        lang = language or (
            None if self.config.language == STTLanguage.AUTO 
            else self.config.language.value
        )
        
        logger.debug(
            "Transcribing audio",
            path=str(audio_path),
            language=lang,
            device=self._device
        )
        
        try:
            # Run transcription in thread
            segments, info = await asyncio.to_thread(
                self._transcribe_sync,
                str(audio_path),
                lang
            )
            
            # Process segments
            transcription_segments = []
            full_text_parts = []
            
            for segment in segments:
                transcription_segments.append(
                    TranscriptionSegment(
                        text=segment.text.strip(),
                        start=segment.start,
                        end=segment.end,
                        confidence=getattr(segment, 'avg_logprob', 0.0)
                    )
                )
                full_text_parts.append(segment.text.strip())
            
            full_text = " ".join(full_text_parts)
            
            return STTResponse(
                text=full_text,
                segments=transcription_segments,
                language=info.language,
                language_probability=info.language_probability,
                duration_seconds=info.duration,
                model=f"whisper-{self.config.model}"
            )
            
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                logger.error("CUDA OOM during transcription, clearing cache")
                _torch.cuda.empty_cache()
                raise RuntimeError(
                    "GPU memory exhausted. Try shorter audio or restart service."
                ) from e
            raise
    
    def _transcribe_sync(self, audio_path: str, language: Optional[str]):
        """Synchronous transcription for thread execution."""
        return self._model.transcribe(
            audio_path,
            language=language,
            beam_size=self.config.beam_size,
            vad_filter=self.config.vad_filter,
            vad_parameters={"threshold": self.config.vad_threshold}
        )
    
    def is_available(self) -> bool:
        """
        Check if faster-whisper is available.
        
        Returns:
            True if faster-whisper is installed
        """
        try:
            _lazy_import_whisper()
            return _WhisperModel is not None
        except ImportError:
            return False
    
    async def cleanup(self) -> None:
        """Cleanup model and free GPU memory."""
        if self._model is not None:
            del self._model
            self._model = None
            
            if _torch and _torch.cuda.is_available():
                _torch.cuda.empty_cache()
                
        self._initialized = False
        logger.info("Whisper STT cleaned up")
