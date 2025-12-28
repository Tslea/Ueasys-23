"""
Edge TTS Provider - Microsoft Edge text-to-speech.

Edge TTS uses Microsoft's online TTS service (free, no API key needed).
High quality neural voices with multiple languages and voice personalities.

Example:
    >>> tts = EdgeTTS()
    >>> await tts.initialize()
    >>> response = await tts.generate("Hello world", voice_id="gandalf")
"""

import asyncio
import io
from pathlib import Path
from typing import Optional, Dict

from src.config.logging_config import get_logger
from src.llm.tts.base import TTSProvider, TTSConfig, TTSResponse, AudioFormat

logger = get_logger(__name__)


class EdgeTTS(TTSProvider):
    """
    Edge TTS provider using Microsoft's neural TTS voices.
    
    Features:
        - High quality neural voices
        - Multiple languages (70+ voices)
        - Voice personas for different characters
        - Zero VRAM (cloud-based)
        - No API key required
        
    Voice Mapping:
        Each character can have a mapped voice persona.
        
    Attributes:
        config: TTS configuration
        _voice_map: Character to voice mapping
    """
    
    # Voice mapping for fantasy characters
    # Using English voices with different personas
    DEFAULT_VOICE_MAP: Dict[str, str] = {
        # Wise old characters
        "gandalf": "en-GB-RyanNeural",        # Deep British male
        # Elegant elven characters  
        "galadriel": "en-GB-SoniaNeural",     # Elegant British female
        "legolas": "en-GB-ThomasNeural",      # Young British male
        "elrond": "en-AU-WilliamNeural",      # Wise Australian male
        # Dwarven characters
        "gimli": "en-IE-ConnorNeural",        # Irish male (gruff)
        "thorin": "en-GB-RyanNeural",         # Deep British male
        # Dark/Evil characters
        "smaug": "en-US-GuyNeural",           # Deep American male
        "sauron": "en-US-DavisNeural",        # Dark American male
        "saruman": "en-GB-RyanNeural",        # Deep British male
        # Hobbit characters
        "frodo": "en-GB-OliverNeural",        # Young British male
        "sam": "en-GB-OliverNeural",          # Friendly British male
        "bilbo": "en-GB-ThomasNeural",        # Older British male
        # Human characters
        "aragorn": "en-US-ChristopherNeural", # Noble American male
        "boromir": "en-US-GuyNeural",         # Strong American male
        "eowyn": "en-GB-LibbyNeural",         # Strong British female
        "arwen": "en-GB-MaisieNeural",        # Gentle British female
        # Default
        "default": "en-US-JennyNeural",       # Neutral American female
    }
    
    # Italian voices for Italian mode
    ITALIAN_VOICE_MAP: Dict[str, str] = {
        "gandalf": "it-IT-DiegoNeural",
        "galadriel": "it-IT-ElsaNeural",
        "legolas": "it-IT-GiuseppeNeural",
        "smaug": "it-IT-DiegoNeural",
        "aragorn": "it-IT-GiuseppeNeural",
        "default": "it-IT-IsabellaNeural",
    }
    
    def __init__(self, config: Optional[TTSConfig] = None):
        """Initialize Edge TTS provider."""
        super().__init__(config)
        self._voice_map = self.DEFAULT_VOICE_MAP.copy()
        self._sample_rate = 24000  # Edge TTS default
        
    async def initialize(self) -> None:
        """
        Initialize Edge TTS (minimal setup needed).
        
        Edge TTS is cloud-based, so no model loading required.
        """
        if self._initialized:
            return
            
        try:
            import edge_tts
            self._edge_tts = edge_tts
            self._initialized = True
            logger.info("Edge TTS initialized successfully")
        except ImportError:
            raise RuntimeError(
                "edge-tts is not installed. Run: pip install edge-tts"
            )
    
    def set_voice_map(self, voice_map: Dict[str, str]) -> None:
        """
        Set custom voice mapping for characters.
        
        Args:
            voice_map: Dict mapping character_id to Edge TTS voice name
        """
        self._voice_map.update(voice_map)
        
    def set_language(self, language: str = "en") -> None:
        """
        Set language for voice mapping.
        
        Args:
            language: Language code (en, it, etc.)
        """
        if language == "it":
            self._voice_map = self.ITALIAN_VOICE_MAP.copy()
        else:
            self._voice_map = self.DEFAULT_VOICE_MAP.copy()
    
    async def generate(
        self,
        text: str,
        voice_id: Optional[str] = None,
        voice_clip_path: Optional[Path] = None,  # Ignored for Edge TTS
        language: str = "en",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%"
    ) -> TTSResponse:
        """
        Generate speech from text using Edge TTS.
        
        Args:
            text: Text to convert to speech
            voice_id: Character name to select voice persona
            voice_clip_path: Ignored (Edge TTS doesn't support cloning)
            language: Language code for voice selection
            rate: Speaking rate adjustment (e.g., "+10%", "-20%")
            pitch: Pitch adjustment (e.g., "+5Hz", "-10Hz")
            volume: Volume adjustment (e.g., "+10%", "-5%")
            
        Returns:
            TTSResponse with generated audio
            
        Raises:
            RuntimeError: If generation fails
        """
        if not self._initialized:
            await self.initialize()
        
        # Select voice based on character
        voice = self._get_voice_for_character(voice_id, language)
        
        logger.debug(
            "Generating TTS",
            text_length=len(text),
            voice_id=voice_id,
            voice=voice,
            language=language
        )
        
        try:
            # Generate audio
            communicate = self._edge_tts.Communicate(
                text,
                voice=voice,
                rate=rate,
                pitch=pitch,
                volume=volume
            )
            
            # Collect audio data
            audio_data = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.write(chunk["data"])
            
            audio_bytes = audio_data.getvalue()
            
            # Estimate duration (rough estimate based on text length)
            duration = len(text) * 0.06  # ~60ms per character
            
            return TTSResponse(
                audio_data=audio_bytes,
                sample_rate=self._sample_rate,
                duration_seconds=duration,
                format=AudioFormat.MP3,  # Edge TTS outputs MP3
                voice_id=voice_id or "default",
                model=f"edge-tts-{voice}"
            )
            
        except Exception as e:
            logger.error(f"Edge TTS generation failed: {e}")
            raise RuntimeError(f"TTS generation failed: {e}") from e
    
    def _get_voice_for_character(
        self, 
        voice_id: Optional[str], 
        language: str
    ) -> str:
        """Get the appropriate voice for a character."""
        if language == "it":
            voice_map = self.ITALIAN_VOICE_MAP
        else:
            voice_map = self._voice_map
            
        if voice_id and voice_id.lower() in voice_map:
            return voice_map[voice_id.lower()]
        
        return voice_map.get("default", "en-US-JennyNeural")
    
    async def list_voices(self) -> list[str]:
        """
        List available voices from Edge TTS.
        
        Returns:
            List of voice names
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            voices = await self._edge_tts.list_voices()
            return [v["ShortName"] for v in voices]
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return list(self._voice_map.values())
    
    async def list_character_voices(self) -> Dict[str, str]:
        """
        List character to voice mappings.
        
        Returns:
            Dict of character_id to voice name
        """
        return self._voice_map.copy()
    
    def is_available(self) -> bool:
        """
        Check if Edge TTS is available.
        
        Returns:
            True if edge-tts package is installed
        """
        try:
            import edge_tts
            return True
        except ImportError:
            return False
    
    async def cleanup(self) -> None:
        """Cleanup (minimal for Edge TTS)."""
        self._initialized = False
        logger.info("Edge TTS cleaned up")
