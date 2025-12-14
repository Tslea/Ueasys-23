"""
Configuration module for Fantasy World RAG.

This module provides centralized configuration management using Pydantic settings.
"""

from src.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
