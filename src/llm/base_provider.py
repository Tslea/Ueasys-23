"""
Base LLM Provider - Abstract base class for LLM integrations.

This module provides the base interface for LLM providers,
ensuring consistent behavior across different LLM services.

Example:
    >>> class MyProvider(BaseLLMProvider):
    ...     async def generate(self, prompt: str) -> LLMResponse:
    ...         # Implementation
    ...         pass
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional, AsyncIterator

from pydantic import BaseModel, Field

from src.config.logging_config import get_logger, LoggerMixin
from src.config.settings import get_settings

logger = get_logger(__name__)


class LLMModel(str, Enum):
    """Supported LLM models."""
    # OpenAI
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"
    
    # Anthropic
    CLAUDE_35_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Local/Other
    LOCAL = "local"


class LLMConfig(BaseModel):
    """
    Configuration for LLM providers.
    
    Attributes:
        model: Model to use
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
        top_p: Top-p sampling parameter
        frequency_penalty: Frequency penalty
        presence_penalty: Presence penalty
        stop_sequences: Sequences to stop generation
    """
    model: str = "gpt-4o-mini"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=128000)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    stop_sequences: list[str] = Field(default_factory=list)
    
    # Additional provider-specific settings
    extra: dict[str, Any] = Field(default_factory=dict)


class TokenUsage(BaseModel):
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class LLMResponse(BaseModel):
    """
    Response from an LLM provider.
    
    Attributes:
        content: Generated text content
        model: Model that generated the response
        finish_reason: Why generation stopped
        usage: Token usage statistics
        latency_ms: Response latency in milliseconds
        metadata: Additional response metadata
    """
    content: str
    model: str
    finish_reason: str = "stop"
    usage: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class Message(BaseModel):
    """A message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None  # For multi-character scenarios


class BaseLLMProvider(ABC, LoggerMixin):
    """
    Abstract base class for LLM providers.
    
    Provides a consistent interface for different LLM services
    with support for both single-turn and multi-turn conversations.
    
    Subclasses must implement:
        - generate(): Generate a response from a prompt
        - generate_chat(): Generate from a conversation
        - stream_generate(): Stream a response
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize the provider.
        
        Args:
            config: Optional LLM configuration
        """
        self._settings = get_settings()
        self._config = config or LLMConfig()
        
        self.logger.info(
            "Initialized LLM provider",
            provider=self.__class__.__name__,
            model=self._config.model,
        )
    
    @property
    def config(self) -> LLMConfig:
        """Get current configuration."""
        return self._config
    
    def update_config(self, **kwargs: Any) -> None:
        """Update configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a response from a prompt.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with generated content
        """
        pass
    
    @abstractmethod
    async def generate_chat(
        self,
        messages: list[Message],
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a response from a conversation.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with generated content
        """
        pass
    
    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream a response from a prompt.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
            
        Yields:
            String chunks of the response
        """
        pass
    
    async def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate with automatic retry on failure.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_retries: Maximum retry attempts
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with generated content
            
        Raises:
            Exception: If all retries fail
        """
        import asyncio
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await self.generate(prompt, system_prompt, **kwargs)
            except Exception as e:
                last_error = e
                self.logger.warning(
                    "LLM generation failed, retrying",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=str(e),
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise last_error or Exception("All retries failed")
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        This is a rough estimate. Subclasses may override
        with model-specific tokenizers.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token
        return len(text) // 4
    
    def validate_prompt_length(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> bool:
        """
        Check if prompt fits within context window.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            True if prompt fits, False otherwise
        """
        total_tokens = self.count_tokens(prompt)
        if system_prompt:
            total_tokens += self.count_tokens(system_prompt)
        
        # Reserve space for response
        max_input = 128000 - self._config.max_tokens
        
        return total_tokens < max_input
