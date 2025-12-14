"""
OpenAI Provider - OpenAI API integration.

This module provides OpenAI API integration for the LLM system.

Example:
    >>> from src.llm import OpenAIProvider
    >>> provider = OpenAIProvider()
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


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI API provider.
    
    Supports GPT-4, GPT-4 Turbo, and GPT-3.5 Turbo models.
    
    Example:
        >>> provider = OpenAIProvider(config=LLMConfig(
        ...     model="gpt-4o",
        ...     temperature=0.7
        ... ))
        >>> response = await provider.generate(
        ...     "Tell me about the Ring of Power",
        ...     system_prompt="You are Gandalf the Grey."
        ... )
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            config: Optional LLM configuration
        """
        super().__init__(config)
        
        self._settings = get_settings()
        self._client = None
        
        # Set default model if not specified
        if not self._config.model or self._config.model == "gpt-4o-mini":
            self._config.model = self._settings.llm_model
    
    async def _ensure_client(self) -> None:
        """Ensure OpenAI client is initialized."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                
                self._client = AsyncOpenAI(
                    api_key=self._settings.openai_api_key,
                )
            except Exception as e:
                self.logger.error(
                    "Failed to initialize OpenAI client",
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
        Generate a response using OpenAI API.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            LLMResponse with generated content
        """
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))
        
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
        
        # Build request parameters
        params = {
            "model": kwargs.get("model", self._config.model),
            "messages": [
                {"role": m.role, "content": m.content}
                for m in messages
            ],
            "temperature": kwargs.get("temperature", self._config.temperature),
            "max_tokens": kwargs.get("max_tokens", self._config.max_tokens),
            "top_p": kwargs.get("top_p", self._config.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self._config.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self._config.presence_penalty),
        }
        
        if self._config.stop_sequences:
            params["stop"] = self._config.stop_sequences
        
        self.logger.debug(
            "Calling OpenAI API",
            model=params["model"],
            num_messages=len(messages),
        )
        
        try:
            response = await self._client.chat.completions.create(**params)
            
            latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Extract response data
            choice = response.choices[0]
            usage = response.usage
            
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                finish_reason=choice.finish_reason or "stop",
                usage=TokenUsage(
                    prompt_tokens=usage.prompt_tokens if usage else 0,
                    completion_tokens=usage.completion_tokens if usage else 0,
                    total_tokens=usage.total_tokens if usage else 0,
                ),
                latency_ms=latency_ms,
                metadata={
                    "id": response.id,
                    "created": response.created,
                },
            )
            
        except Exception as e:
            self.logger.error(
                "OpenAI API error",
                error=str(e),
            )
            raise
    
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream a response from OpenAI.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
            
        Yields:
            String chunks of the response
        """
        await self._ensure_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        params = {
            "model": kwargs.get("model", self._config.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self._config.temperature),
            "max_tokens": kwargs.get("max_tokens", self._config.max_tokens),
            "stream": True,
        }
        
        try:
            stream = await self._client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(
                "OpenAI streaming error",
                error=str(e),
            )
            raise
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens using tiktoken.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Token count
        """
        try:
            import tiktoken
            
            # Get encoding for model
            try:
                encoding = tiktoken.encoding_for_model(self._config.model)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")
            
            return len(encoding.encode(text))
        except ImportError:
            # Fallback to rough estimate
            return super().count_tokens(text)
