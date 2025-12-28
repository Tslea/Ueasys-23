"""
Chatterbox TTS Provider - Local text-to-speech using Chatterbox.

Chatterbox is a state-of-the-art open-source TTS model by Resemble AI
with zero-shot voice cloning capabilities.

Example:
    >>> tts = ChatterboxTTS()
    >>> await tts.initialize()
    >>> response = await tts.generate("Hello world", voice_id="gandalf")
"""

import asyncio
import io
from pathlib import Path
from typing import Optional

from src.config.logging_config import get_logger
from src.llm.tts.base import TTSProvider, TTSConfig, TTSResponse, AudioFormat

logger = get_logger(__name__)

# Lazy imports to avoid loading torch until needed
_torch = None
_torchaudio = None
_ChatterboxTurboTTS = None
_ChatterboxTTS = None


def _lazy_import_chatterbox():
    """Lazy import Chatterbox and torch dependencies."""
    global _torch, _torchaudio, _ChatterboxTurboTTS, _ChatterboxTTS
    
    if _torch is None:
        import torch
        _torch = torch
        
    if _torchaudio is None:
        import torchaudio
        _torchaudio = torchaudio
        
    if _ChatterboxTurboTTS is None:
        try:
            from chatterbox.tts_turbo import ChatterboxTurboTTS
            _ChatterboxTurboTTS = ChatterboxTurboTTS
        except ImportError:
            logger.warning("ChatterboxTurboTTS not available")
            
    if _ChatterboxTTS is None:
        try:
            from chatterbox.tts import ChatterboxTTS as _CB_TTS
            _ChatterboxTTS = _CB_TTS
        except ImportError:
            logger.warning("ChatterboxTTS not available")


class ChatterboxTTS(TTSProvider):
    """
    Chatterbox TTS provider for local text-to-speech.
    
    Features:
        - Zero-shot voice cloning from 10s audio clip
        - Paralinguistic tags ([laugh], [cough], etc.)
        - Low VRAM usage with float16
        - CPU fallback if GPU unavailable
        
    Attributes:
        config: TTS configuration
        _model: Loaded Chatterbox model
        _device: Active compute device
    """
    
    def __init__(self, config: Optional[TTSConfig] = None):
        """Initialize Chatterbox TTS provider."""
        super().__init__(config)
        self._device = None
        self._sample_rate = None
        
    async def initialize(self) -> None:
        """
        Initialize the Chatterbox model.
        
        Loads model with appropriate device and precision settings.
        Falls back to CPU if CUDA is unavailable or OOM.
        
        Raises:
            RuntimeError: If model loading fails completely
        """
        if self._initialized:
            return
            
        _lazy_import_chatterbox()
        
        if _ChatterboxTurboTTS is None and _ChatterboxTTS is None:
            raise RuntimeError(
                "Chatterbox is not installed. Run: pip install chatterbox-tts"
            )
        
        # Determine device
        device = self.config.device
        if device == "auto":
            device = "cuda" if _torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing Chatterbox TTS on device: {device}")
        
        try:
            # Try to load Turbo model (smaller, faster)
            if self.config.model == "turbo" and _ChatterboxTurboTTS:
                self._model = await asyncio.to_thread(
                    _ChatterboxTurboTTS.from_pretrained,
                    device=device
                )
                logger.info("Loaded Chatterbox Turbo model")
            else:
                # Fall back to standard model
                self._model = await asyncio.to_thread(
                    _ChatterboxTTS.from_pretrained,
                    device=device
                )
                logger.info("Loaded Chatterbox standard model")
            
            # Apply float16 for VRAM savings
            if device == "cuda" and self.config.use_float16:
                self._model.half()
                logger.info("Applied float16 precision for VRAM savings")
                
            self._device = device
            self._sample_rate = self._model.sr
            self._initialized = True
            
        except RuntimeError as e:
            if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
                logger.warning(f"CUDA failed, falling back to CPU: {e}")
                
                # Retry on CPU
                _torch.cuda.empty_cache()
                
                if self.config.model == "turbo" and _ChatterboxTurboTTS:
                    self._model = await asyncio.to_thread(
                        _ChatterboxTurboTTS.from_pretrained,
                        device="cpu"
                    )
                else:
                    self._model = await asyncio.to_thread(
                        _ChatterboxTTS.from_pretrained,
                        device="cpu"
                    )
                
                self._device = "cpu"
                self._sample_rate = self._model.sr
                self._initialized = True
                logger.info("Loaded Chatterbox on CPU (slower but works)")
            else:
                raise RuntimeError(f"Failed to initialize Chatterbox: {e}") from e
    
    async def generate(
        self,
        text: str,
        voice_id: Optional[str] = None,
        voice_clip_path: Optional[Path] = None,
    ) -> TTSResponse:
        """
        Generate speech from text using Chatterbox.
        
        Args:
            text: Text to convert to speech. Can include paralinguistic tags
                  like [laugh], [cough], [chuckle] for Turbo model.
            voice_id: Character name to use voice clip for cloning
            voice_clip_path: Direct path to voice clip (overrides voice_id)
            
        Returns:
            TTSResponse with generated audio
            
        Raises:
            RuntimeError: If generation fails
        """
        if not self._initialized:
            await self.initialize()
        
        # Resolve voice clip path
        clip_path = voice_clip_path
        if clip_path is None and voice_id:
            clip_path = self._get_voice_clip_path(voice_id)
            
        if clip_path and not clip_path.exists():
            logger.warning(f"Voice clip not found: {clip_path}, using default voice")
            clip_path = None
        
        logger.debug(
            "Generating TTS",
            text_length=len(text),
            voice_id=voice_id,
            voice_clip=str(clip_path) if clip_path else None,
            device=self._device
        )
        
        try:
            # Generate in thread to avoid blocking
            wav = await asyncio.to_thread(
                self._generate_sync,
                text,
                clip_path
            )
            
            # Convert to bytes
            audio_bytes = await self._wav_to_bytes(wav)
            duration = wav.shape[-1] / self._sample_rate
            
            return TTSResponse(
                audio_data=audio_bytes,
                sample_rate=self._sample_rate,
                duration_seconds=duration,
                format=self.config.audio_format,
                voice_id=voice_id or "default",
                model=f"chatterbox-{self.config.model}"
            )
            
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                logger.error("CUDA OOM during generation, clearing cache")
                _torch.cuda.empty_cache()
                raise RuntimeError(
                    "GPU memory exhausted. Try shorter text or restart service."
                ) from e
            raise
    
    def _generate_sync(self, text: str, clip_path: Optional[Path]) -> "torch.Tensor":
        """Synchronous generation for thread execution."""
        kwargs = {}
        
        if clip_path:
            kwargs["audio_prompt_path"] = str(clip_path)
        
        # Add exaggeration for standard model
        if self.config.model != "turbo":
            kwargs["exaggeration"] = self.config.exaggeration
            kwargs["cfg_weight"] = self.config.cfg_weight
        
        return self._model.generate(text, **kwargs)
    
    async def _wav_to_bytes(self, wav: "torch.Tensor") -> bytes:
        """Convert wav tensor to bytes."""
        buffer = io.BytesIO()
        
        # Ensure correct shape: (channels, samples)
        if wav.dim() == 1:
            wav = wav.unsqueeze(0)
        
        await asyncio.to_thread(
            _torchaudio.save,
            buffer,
            wav.cpu(),
            self._sample_rate,
            format=self.config.audio_format.value
        )
        
        buffer.seek(0)
        return buffer.read()
    
    async def list_voices(self) -> list[str]:
        """
        List available voice clips for cloning.
        
        Returns:
            List of voice identifiers (file stems)
        """
        voice_dir = self.config.voice_clip_dir
        
        if not voice_dir.exists():
            return ["default"]
        
        voices = ["default"]
        for ext in [".wav", ".mp3", ".ogg", ".flac"]:
            voices.extend([f.stem for f in voice_dir.glob(f"*{ext}")])
        
        return list(set(voices))
    
    def is_available(self) -> bool:
        """
        Check if Chatterbox is available.
        
        Returns:
            True if chatterbox-tts is installed
        """
        try:
            _lazy_import_chatterbox()
            return _ChatterboxTurboTTS is not None or _ChatterboxTTS is not None
        except Exception:
            return False
    
    async def cleanup(self) -> None:
        """Cleanup model and free GPU memory."""
        if self._model is not None:
            del self._model
            self._model = None
            
            if _torch and _torch.cuda.is_available():
                _torch.cuda.empty_cache()
                
        self._initialized = False
        logger.info("Chatterbox TTS cleaned up")
