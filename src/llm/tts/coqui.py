"""
Coqui TTS Provider - Local text-to-speech using Coqui TTS (XTTS).

Coqui TTS is an open-source TTS library with multi-language support
and zero-shot voice cloning capabilities via XTTS model.

Example:
    >>> tts = CoquiTTS()
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
_TTS = None


def _lazy_import_coqui():
    """Lazy import Coqui TTS and torch dependencies."""
    global _torch, _TTS
    
    if _torch is None:
        import torch
        _torch = torch
        
    if _TTS is None:
        try:
            from TTS.api import TTS
            _TTS = TTS
        except ImportError:
            logger.warning("Coqui TTS not available")


class CoquiTTS(TTSProvider):
    """
    Coqui TTS provider for local text-to-speech with voice cloning.
    
    Features:
        - Zero-shot voice cloning from short audio clip (XTTS v2)
        - Multi-language support (17+ languages)
        - Low VRAM usage with appropriate model selection
        - CPU fallback if GPU unavailable
        
    Models:
        - xtts_v2: Best quality, voice cloning, ~4GB VRAM
        - tts_models/en/vctk/vits: Faster, no cloning, ~1GB VRAM
        
    Attributes:
        config: TTS configuration
        _model: Loaded Coqui TTS model
        _device: Active compute device
    """
    
    # Default XTTS v2 model for voice cloning
    XTTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
    # Faster model without cloning
    FAST_MODEL = "tts_models/en/vctk/vits"
    
    def __init__(self, config: Optional[TTSConfig] = None):
        """Initialize Coqui TTS provider."""
        super().__init__(config)
        self._device = None
        self._sample_rate = 24000  # XTTS default
        self._supports_cloning = True
        
    async def initialize(self) -> None:
        """
        Initialize the Coqui TTS model.
        
        Loads XTTS v2 model for voice cloning support.
        Falls back to CPU if CUDA is unavailable or OOM.
        
        Raises:
            RuntimeError: If model loading fails completely
        """
        if self._initialized:
            return
            
        _lazy_import_coqui()
        
        if _TTS is None:
            raise RuntimeError(
                "Coqui TTS is not installed. Run: pip install TTS"
            )
        
        # Determine device
        device = self.config.device
        if device == "auto":
            device = "cuda" if _torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing Coqui TTS on device: {device}")
        
        # Select model based on config
        model_name = self.XTTS_MODEL
        if self.config.model == "fast":
            model_name = self.FAST_MODEL
            self._supports_cloning = False
            self._sample_rate = 22050
        
        try:
            # Load model
            self._model = await asyncio.to_thread(
                self._load_model,
                model_name,
                device
            )
            
            self._device = device
            self._initialized = True
            logger.info(f"Loaded Coqui TTS model: {model_name}")
            
        except RuntimeError as e:
            if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
                logger.warning(f"CUDA failed, falling back to CPU: {e}")
                
                # Retry on CPU
                if _torch.cuda.is_available():
                    _torch.cuda.empty_cache()
                
                self._model = await asyncio.to_thread(
                    self._load_model,
                    model_name,
                    "cpu"
                )
                
                self._device = "cpu"
                self._initialized = True
                logger.info("Loaded Coqui TTS on CPU (slower but works)")
            else:
                raise RuntimeError(f"Failed to initialize Coqui TTS: {e}") from e
    
    def _load_model(self, model_name: str, device: str):
        """Load the TTS model synchronously."""
        # Coqui TTS uses gpu=True/False instead of device string
        use_gpu = device == "cuda"
        
        tts = _TTS(model_name, gpu=use_gpu)
        
        return tts
    
    async def generate(
        self,
        text: str,
        voice_id: Optional[str] = None,
        voice_clip_path: Optional[Path] = None,
        language: str = "en"
    ) -> TTSResponse:
        """
        Generate speech from text using Coqui TTS.
        
        Args:
            text: Text to convert to speech
            voice_id: Character name to use voice clip for cloning
            voice_clip_path: Direct path to voice clip (overrides voice_id)
            language: Language code (en, it, es, fr, de, etc.)
            
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
            device=self._device,
            language=language
        )
        
        try:
            # Generate in thread to avoid blocking
            wav = await asyncio.to_thread(
                self._generate_sync,
                text,
                clip_path,
                language
            )
            
            # Convert to bytes
            audio_bytes = self._wav_to_bytes(wav)
            duration = len(wav) / self._sample_rate
            
            return TTSResponse(
                audio_data=audio_bytes,
                sample_rate=self._sample_rate,
                duration_seconds=duration,
                format=self.config.audio_format,
                voice_id=voice_id or "default",
                model="coqui-xtts-v2" if self._supports_cloning else "coqui-vits"
            )
            
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                logger.error("CUDA OOM during generation, clearing cache")
                _torch.cuda.empty_cache()
                raise RuntimeError(
                    "GPU memory exhausted. Try shorter text or restart service."
                ) from e
            raise
    
    def _generate_sync(
        self, 
        text: str, 
        clip_path: Optional[Path],
        language: str
    ) -> list:
        """Synchronous generation for thread execution."""
        
        if self._supports_cloning and clip_path:
            # XTTS with voice cloning
            wav = self._model.tts(
                text=text,
                speaker_wav=str(clip_path),
                language=language
            )
        elif self._supports_cloning:
            # XTTS without cloning - use default speaker
            # Get first available speaker
            speakers = self._model.speakers
            speaker = speakers[0] if speakers else None
            
            wav = self._model.tts(
                text=text,
                speaker=speaker,
                language=language
            )
        else:
            # VITS model (no cloning support)
            wav = self._model.tts(text=text)
        
        return wav
    
    def _wav_to_bytes(self, wav: list) -> bytes:
        """Convert wav list to bytes."""
        import wave
        import struct
        
        buffer = io.BytesIO()
        
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self._sample_rate)
            
            # Convert float to int16
            audio_int16 = [int(max(-32768, min(32767, s * 32767))) for s in wav]
            wav_file.writeframes(struct.pack(f'{len(audio_int16)}h', *audio_int16))
        
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
        Check if Coqui TTS is available.
        
        Returns:
            True if TTS package is installed
        """
        try:
            _lazy_import_coqui()
            return _TTS is not None
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
        logger.info("Coqui TTS cleaned up")
