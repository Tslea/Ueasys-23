"""
Anthropic Provider - Anthropic Claude API integration.

This module provides Anthropic Claude API integration for the LLM system.

Example:
    >>> from src.llm import AnthropicProvider
    >>> provider = AnthropicProvider()
    >>> response = await provider.generate("Hello, who are you?")
"""

from datetime import datetime
from typing import Any, Optional, AsyncIterator

from src.config.logging_config import get_logger
from src.config.settings import get_settings
from src.llm.base_provider import (
    BaseLLMProvider,
    LLMConfig,
    LLMResponse,
    Message,
    TokenUsage,
)

logger = get_logger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude API provider.
    
    Supports Claude 3.5 Sonnet, Claude 3 Opus, and Claude 3 Haiku models.
    
    Example:
        >>> provider = AnthropicProvider(config=LLMConfig(
        ...     model="claude-3-5-sonnet-20241022",
        ...     temperature=0.7
        ... ))
        >>> response = await provider.generate(
        ...     "Tell me about the Ring of Power",
        ...     system_prompt="You are Gandalf the Grey."
        ... )
    """
    
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize the Anthropic provider.
        
        Args:
            config: Optional LLM configuration
        """
        super().__init__(config)
        
        self._settings = get_settings()
        self._client = None
        
        # Set default model if not Claude model
        if not self._config.model.startswith("claude"):
            self._config.model = self.DEFAULT_MODEL
    
    async def _ensure_client(self) -> None:
        """Ensure Anthropic client is initialized."""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                
                self._client = AsyncAnthropic(
                    api_key=self._settings.anthropic_api_key,
                )
            except Exception as e:
                self.logger.error(
                    "Failed to initialize Anthropic client",
                    error=str(e),
                )
                raise
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a response using Anthropic API.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            LLMResponse with generated content
        """
        messages = [Message(role="user", content=prompt)]
        
        # Anthropic handles system prompt separately
        kwargs["system_prompt"] = system_prompt
        
        return await self.generate_chat(messages, **kwargs)
    
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
        await self._ensure_client()
        
        start_time = datetime.now()
        
        # Convert messages to Anthropic format
        # Anthropic doesn't use system role in messages
        anthropic_messages = []
        system_prompt = kwargs.pop("system_prompt", None)
        
        for msg in messages:
            if msg.role == "system":
                # Use as system prompt if not already set
                if not system_prompt:
                    system_prompt = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })
        
        # Ensure alternating user/assistant messages
        # Anthropic requires this pattern
        cleaned_messages = self._ensure_alternating_messages(anthropic_messages)
        
        # Build request parameters
        params = {
            "model": kwargs.get("model", self._config.model),
            "messages": cleaned_messages,
            "max_tokens": kwargs.get("max_tokens", self._config.max_tokens),
            "temperature": kwargs.get("temperature", self._config.temperature),
        }
        
        if system_prompt:
            params["system"] = system_prompt
        
        if self._config.stop_sequences:
            params["stop_sequences"] = self._config.stop_sequences
        
        self.logger.debug(
            "Calling Anthropic API",
            model=params["model"],
            num_messages=len(cleaned_messages),
        )
        
        try:
            response = await self._client.messages.create(**params)
            
            latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Extract response content
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text
            
            return LLMResponse(
                content=content,
                model=response.model,
                finish_reason=response.stop_reason or "end_turn",
                usage=TokenUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                ),
                latency_ms=latency_ms,
                metadata={
                    "id": response.id,
                    "type": response.type,
                },
            )
            
        except Exception as e:
            self.logger.error(
                "Anthropic API error",
                error=str(e),
            )
            raise
    
    def _ensure_alternating_messages(
        self,
        messages: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        """
        Ensure messages alternate between user and assistant.
        
        Anthropic requires this pattern. Merges consecutive messages
        from the same role.
        
        Args:
            messages: List of messages
            
        Returns:
            Cleaned message list
        """
        if not messages:
            return [{"role": "user", "content": "Hello"}]
        
        cleaned = []
        
        for msg in messages:
            if cleaned and cleaned[-1]["role"] == msg["role"]:
                # Merge with previous message
                cleaned[-1]["content"] += "\n\n" + msg["content"]
            else:
                cleaned.append(msg.copy())
        
        # Ensure starts with user
        if cleaned and cleaned[0]["role"] != "user":
            cleaned.insert(0, {"role": "user", "content": "[Continuing conversation]"})
        
        return cleaned
    
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream a response from Anthropic.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
            
        Yields:
            String chunks of the response
        """
        await self._ensure_client()
        
        params = {
            "model": kwargs.get("model", self._config.model),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", self._config.max_tokens),
            "temperature": kwargs.get("temperature", self._config.temperature),
        }
        
        if system_prompt:
            params["system"] = system_prompt
        
        try:
            async with self._client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            self.logger.error(
                "Anthropic streaming error",
                error=str(e),
            )
            raise
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for Claude.
        
        Claude uses a different tokenizer than GPT models.
        This provides a rough estimate.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        # Claude's tokenizer is roughly similar to GPT
        # ~4 characters per token is a reasonable estimate
        return len(text) // 4
