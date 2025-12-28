"""
STT (Speech-to-Text) Providers.

This module provides speech-to-text capabilities with multiple provider support.
Currently supports Whisper (local via faster-whisper).

Example:
    >>> from src.llm.stt import get_stt_provider
    >>> stt = get_stt_provider()
    >>> result = await stt.transcribe(audio_bytes)
"""

from src.llm.stt.base import STTProvider, STTConfig, STTResponse
from src.llm.stt.whisper import WhisperSTT

__all__ = [
    "STTProvider",
    "STTConfig",
    "STTResponse",
    "WhisperSTT",
    "get_stt_provider",
]


def get_stt_provider(provider: str = "whisper") -> STTProvider:
    """
    Factory function to get the appropriate STT provider.
    
    Args:
        provider: Provider name ("whisper")
        
    Returns:
        STTProvider instance
        
    Raises:
        ValueError: If provider is not supported
    """
    providers = {
        "whisper": WhisperSTT,
    }
    
    if provider not in providers:
        raise ValueError(f"Unknown STT provider: {provider}. Supported: {list(providers.keys())}")
    
    return providers[provider]()
