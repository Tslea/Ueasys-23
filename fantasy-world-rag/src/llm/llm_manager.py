"""
LLM Manager - Centralized LLM Provider Management.

This module provides a unified interface for managing multiple LLM providers,
making it easy to switch between models and configure routing.

Usage:
    # Get default provider (for chat)
    llm = LLMManager.get_chat_provider()
    response = await llm.generate("Hello!")
    
    # Get analysis provider (for extraction/reasoning)
    analysis_llm = LLMManager.get_analysis_provider()
    response = await analysis_llm.generate("Analyze this...")
    
    # Get specific provider
    grok = LLMManager.get_provider("grok")
    deepseek = LLMManager.get_provider("deepseek")
    
    # Switch default providers
    LLMManager.set_default_chat_provider("deepseek")
"""

from enum import Enum
from typing import Optional, Type
from functools import lru_cache

from src.llm.base_provider import BaseLLMProvider, LLMConfig
from src.config.settings import get_settings
from src.config.logging_config import get_logger

logger = get_logger(__name__)


class ProviderType(str, Enum):
    """Supported LLM providers."""
    GROK = "grok"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class ModelConfig:
    """Model configuration with metadata."""
    
    # Grok Models
    GROK_4_FAST = {
        "provider": ProviderType.GROK,
        "model": "grok-4-fast",
        "context_window": 131072,
        "cost_per_1k_input": 0.00005,
        "cost_per_1k_output": 0.00025,
        "best_for": ["chat", "real-time", "creative"],
    }
    
    GROK_4 = {
        "provider": ProviderType.GROK,
        "model": "grok-4",
        "context_window": 131072,
        "cost_per_1k_input": 0.0003,
        "cost_per_1k_output": 0.0015,
        "best_for": ["complex", "analysis"],
    }
    
    # DeepSeek Models (V3.2 - December 2024)
    DEEPSEEK_CHAT = {
        "provider": ProviderType.DEEPSEEK,
        "model": "deepseek-chat",
        "version": "V3.2",
        "context_window": 64000,
        "cost_per_1k_input": 0.00014,
        "cost_per_1k_output": 0.00028,
        "best_for": ["analysis", "extraction", "coding"],
    }
    
    DEEPSEEK_REASONER = {
        "provider": ProviderType.DEEPSEEK,
        "model": "deepseek-reasoner",
        "version": "V3.2",
        "context_window": 64000,
        "cost_per_1k_input": 0.00055,
        "cost_per_1k_output": 0.00219,
        "best_for": ["reasoning", "complex-analysis", "agents", "chain-of-thought"],
    }
    
    # OpenAI Models (fallback)
    GPT_4O_MINI = {
        "provider": ProviderType.OPENAI,
        "model": "gpt-4o-mini",
        "context_window": 128000,
        "cost_per_1k_input": 0.00015,
        "cost_per_1k_output": 0.0006,
        "best_for": ["general", "fallback"],
    }


class LLMManager:
    """
    Centralized LLM Provider Manager.
    
    Features:
    - Easy provider switching
    - Automatic routing based on task type
    - Fallback support
    - Cost tracking
    - Singleton instances for efficiency
    """
    
    # Provider instances cache
    _providers: dict[ProviderType, BaseLLMProvider] = {}
    
    # Default routing
    _chat_provider: ProviderType = ProviderType.GROK
    _analysis_provider: ProviderType = ProviderType.DEEPSEEK
    _fallback_provider: ProviderType = ProviderType.OPENAI
    
    @classmethod
    def _get_provider_class(cls, provider_type: ProviderType) -> Type[BaseLLMProvider]:
        """Get provider class by type."""
        if provider_type == ProviderType.GROK:
            from src.llm.grok_provider import GrokProvider
            return GrokProvider
        elif provider_type == ProviderType.DEEPSEEK:
            from src.llm.deepseek_provider import DeepSeekProvider
            return DeepSeekProvider
        elif provider_type == ProviderType.OPENAI:
            from src.llm.openai_provider import OpenAIProvider
            return OpenAIProvider
        elif provider_type == ProviderType.ANTHROPIC:
            from src.llm.anthropic_provider import AnthropicProvider
            return AnthropicProvider
        else:
            raise ValueError(f"Unknown provider: {provider_type}")
    
    @classmethod
    def get_provider(
        cls,
        provider_name: str | ProviderType,
        config: Optional[LLMConfig] = None,
        force_new: bool = False,
    ) -> BaseLLMProvider:
        """
        Get a specific LLM provider.
        
        Args:
            provider_name: Provider name or type
            config: Optional custom configuration
            force_new: Create new instance instead of cached
            
        Returns:
            LLM Provider instance
        """
        if isinstance(provider_name, str):
            provider_type = ProviderType(provider_name.lower())
        else:
            provider_type = provider_name
        
        # Return cached if available and no custom config
        if not force_new and not config and provider_type in cls._providers:
            return cls._providers[provider_type]
        
        try:
            provider_class = cls._get_provider_class(provider_type)
            provider = provider_class(config)
            
            # Cache if no custom config
            if not config:
                cls._providers[provider_type] = provider
            
            logger.info(
                "LLM provider initialized",
                provider=provider_type.value,
                model=provider.config.model,
            )
            
            return provider
            
        except Exception as e:
            logger.error(
                "Failed to initialize provider",
                provider=provider_type.value,
                error=str(e),
            )
            raise
    
    @classmethod
    def get_chat_provider(cls, config: Optional[LLMConfig] = None) -> BaseLLMProvider:
        """
        Get provider for real-time chat/character responses.
        
        Default: Grok 4 Fast (optimized for speed and cost)
        """
        settings = get_settings()
        provider_name = settings.default_chat_provider or cls._chat_provider.value
        
        return cls.get_provider(provider_name, config)
    
    @classmethod
    def get_analysis_provider(cls, config: Optional[LLMConfig] = None) -> BaseLLMProvider:
        """
        Get provider for analysis, extraction, and reasoning.
        
        Default: DeepSeek (optimized for complex analysis)
        """
        settings = get_settings()
        provider_name = settings.default_analysis_provider or cls._analysis_provider.value
        
        return cls.get_provider(provider_name, config)
    
    @classmethod
    def get_agent_provider(cls, config: Optional[LLMConfig] = None) -> BaseLLMProvider:
        """
        Get provider for agent decision making.
        
        Default: DeepSeek Reasoner (best for multi-step reasoning)
        """
        if config is None:
            config = LLMConfig(model="deepseek-reasoner")
        
        return cls.get_provider(ProviderType.DEEPSEEK, config)
    
    @classmethod
    def set_default_chat_provider(cls, provider: str | ProviderType) -> None:
        """Set default provider for chat."""
        if isinstance(provider, str):
            provider = ProviderType(provider.lower())
        cls._chat_provider = provider
        logger.info("Default chat provider set", provider=provider.value)
    
    @classmethod
    def set_default_analysis_provider(cls, provider: str | ProviderType) -> None:
        """Set default provider for analysis."""
        if isinstance(provider, str):
            provider = ProviderType(provider.lower())
        cls._analysis_provider = provider
        logger.info("Default analysis provider set", provider=provider.value)
    
    @classmethod
    async def close_all(cls) -> None:
        """Close all provider connections."""
        for provider in cls._providers.values():
            if hasattr(provider, 'close'):
                await provider.close()
        cls._providers.clear()
    
    @classmethod
    def list_providers(cls) -> list[str]:
        """List available providers."""
        return [p.value for p in ProviderType]
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Optional[dict]:
        """Get information about a specific model."""
        model_configs = {
            "grok-4-fast": ModelConfig.GROK_4_FAST,
            "grok-4": ModelConfig.GROK_4,
            "deepseek-chat": ModelConfig.DEEPSEEK_CHAT,
            "deepseek-reasoner": ModelConfig.DEEPSEEK_REASONER,
            "gpt-4o-mini": ModelConfig.GPT_4O_MINI,
        }
        return model_configs.get(model_name)


# Convenience functions for direct import
def get_chat_llm(config: Optional[LLMConfig] = None) -> BaseLLMProvider:
    """Get LLM for chat (shortcut)."""
    return LLMManager.get_chat_provider(config)


def get_analysis_llm(config: Optional[LLMConfig] = None) -> BaseLLMProvider:
    """Get LLM for analysis (shortcut)."""
    return LLMManager.get_analysis_provider(config)


def get_agent_llm(config: Optional[LLMConfig] = None) -> BaseLLMProvider:
    """Get LLM for agents (shortcut)."""
    return LLMManager.get_agent_provider(config)


def get_llm(provider: str, config: Optional[LLMConfig] = None) -> BaseLLMProvider:
    """Get specific LLM provider (shortcut)."""
    return LLMManager.get_provider(provider, config)
