"""
TTS (Text-to-Speech) Providers.

This module provides text-to-speech capabilities with multiple provider support.
Currently supports Edge TTS (default, cloud), Coqui TTS (local), and ElevenLabs (cloud).

Example:
    >>> from src.llm.tts import get_tts_provider
    >>> tts = get_tts_provider()
    >>> audio = await tts.generate("Hello world", voice_id="gandalf")
"""

from src.llm.tts.base import TTSProvider, TTSConfig, TTSResponse
from src.llm.tts.edge import EdgeTTS
from src.llm.tts.coqui import CoquiTTS
from src.llm.tts.chatterbox import ChatterboxTTS
from src.llm.tts.elevenlabs import ElevenLabsTTS

__all__ = [
    "TTSProvider",
    "TTSConfig", 
    "TTSResponse",
    "EdgeTTS",
    "CoquiTTS",
    "ChatterboxTTS",
    "ElevenLabsTTS",
    "get_tts_provider",
]


def get_tts_provider(provider: str = "edge") -> TTSProvider:
    """
    Factory function to get the appropriate TTS provider.
    
    Args:
        provider: Provider name ("edge", "coqui", "chatterbox", "elevenlabs")
        
    Returns:
        TTSProvider instance
        
    Raises:
        ValueError: If provider is not supported
    """
    providers = {
        "edge": EdgeTTS,
        "coqui": CoquiTTS,
        "chatterbox": ChatterboxTTS,
        "elevenlabs": ElevenLabsTTS,
    }
    
    if provider not in providers:
        raise ValueError(f"Unknown TTS provider: {provider}. Supported: {list(providers.keys())}")
    
    return providers[provider]()
