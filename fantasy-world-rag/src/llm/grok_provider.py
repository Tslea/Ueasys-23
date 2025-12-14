"""
Grok Provider - xAI Grok 4 Fast Integration.

Uses Grok for fast, cost-effective character responses.
API compatible with OpenAI format.
"""

import time
from typing import Any, AsyncIterator, Optional

import httpx

from src.llm.base_provider import (
    BaseLLMProvider,
    LLMConfig,
    LLMResponse,
    Message,
    TokenUsage,
)
from src.config.settings import get_settings


class GrokProvider(BaseLLMProvider):
    """
    Grok LLM Provider using xAI API.
    
    Grok 4 Fast is optimized for:
    - Fast response times
    - Cost-effective token usage
    - Real-time character interactions
    
    API Format: OpenAI-compatible
    Base URL: https://api.x.ai/v1
    """
    
    # Grok models
    GROK_4_FAST = "grok-4-fast"
    GROK_4 = "grok-4"
    GROK_3 = "grok-3"
    
    DEFAULT_MODEL = GROK_4_FAST
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize Grok provider."""
        super().__init__(config)
        
        settings = get_settings()
        self._api_key = settings.grok_api_key
        self._base_url = "https://api.x.ai/v1"
        
        if not self._api_key:
            raise ValueError("GROK_API_KEY not configured")
        
        # Set default model if not specified
        if self._config.model == "gpt-4o-mini":
            self._config.model = self.DEFAULT_MODEL
        
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate response using Grok."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return await self._call_api(messages, **kwargs)
    
    async def generate_chat(
        self,
        messages: list[Message],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate response from conversation."""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        return await self._call_api(formatted_messages, **kwargs)
    
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream response from Grok."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        async for chunk in self._stream_api(messages, **kwargs):
            yield chunk
    
    async def _call_api(
        self,
        messages: list[dict],
        **kwargs: Any,
    ) -> LLMResponse:
        """Make API call to Grok."""
        start_time = time.time()
        
        payload = {
            "model": kwargs.get("model", self._config.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self._config.temperature),
            "max_tokens": kwargs.get("max_tokens", self._config.max_tokens),
            "top_p": kwargs.get("top_p", self._config.top_p),
        }
        
        if self._config.stop_sequences:
            payload["stop"] = self._config.stop_sequences
        
        try:
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            usage = data.get("usage", {})
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", self._config.model),
                finish_reason=data["choices"][0].get("finish_reason", "stop"),
                usage=TokenUsage(
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                ),
                latency_ms=latency_ms,
                metadata={"provider": "grok"},
            )
            
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Grok API error",
                status=e.response.status_code,
                detail=e.response.text,
            )
            raise
        except Exception as e:
            self.logger.error("Grok generation failed", error=str(e))
            raise
    
    async def _stream_api(
        self,
        messages: list[dict],
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream API call to Grok."""
        payload = {
            "model": kwargs.get("model", self._config.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self._config.temperature),
            "max_tokens": kwargs.get("max_tokens", self._config.max_tokens),
            "stream": True,
        }
        
        try:
            async with self._client.stream(
                "POST",
                "/chat/completions",
                json=payload,
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        
                        import json
                        data = json.loads(data_str)
                        
                        if data["choices"][0].get("delta", {}).get("content"):
                            yield data["choices"][0]["delta"]["content"]
                            
        except Exception as e:
            self.logger.error("Grok streaming failed", error=str(e))
            raise
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
