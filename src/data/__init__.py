"""
Data Module - Data Loading and Management

This module handles loading characters, world knowledge,
and other data from files.
"""

from .character_loader import (
    CharacterLoader,
    get_character_loader
)

__all__ = [
    "CharacterLoader",
    "get_character_loader"
]
