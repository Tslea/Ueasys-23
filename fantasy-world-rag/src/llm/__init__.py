"""
LLM module for Fantasy World RAG.

This module provides LLM integration:
- Base LLM Provider interface
- Centralized LLM Manager with easy provider switching
- Grok Provider (xAI) - Fast, cost-effective for chat
- DeepSeek Provider - Best for analysis and reasoning
- OpenAI Provider - Fallback option
- Anthropic Provider - Alternative option
- Prompt Templates

Usage:
    # Easy way - use the manager
    from src.llm import get_chat_llm, get_analysis_llm
    
    chat_llm = get_chat_llm()  # Returns Grok by default
    analysis_llm = get_analysis_llm()  # Returns DeepSeek by default
    
    # Direct access
    from src.llm import LLMManager, ProviderType
    grok = LLMManager.get_provider(ProviderType.GROK)
"""

from src.llm.base_provider import BaseLLMProvider, LLMConfig, LLMResponse, Message
from src.llm.openai_provider import OpenAIProvider
from src.llm.anthropic_provider import AnthropicProvider
from src.llm.grok_provider import GrokProvider
from src.llm.deepseek_provider import DeepSeekProvider
from src.llm.llm_manager import (
    LLMManager,
    ProviderType,
    ModelConfig,
    get_chat_llm,
    get_analysis_llm,
    get_agent_llm,
    get_llm,
)
from src.llm.prompt_templates import PromptTemplates, CharacterPromptBuilder

__all__ = [
    # Base classes
    "BaseLLMProvider",
    "LLMConfig",
    "LLMResponse",
    "Message",
    # Manager
    "LLMManager",
    "ProviderType",
    "ModelConfig",
    # Providers
    "GrokProvider",
    "DeepSeekProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    # Convenience functions
    "get_chat_llm",
    "get_analysis_llm",
    "get_agent_llm",
    "get_llm",
    # Templates
    "PromptTemplates",
    "CharacterPromptBuilder",
]
