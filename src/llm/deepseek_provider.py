"""
DeepSeek Provider - DeepSeek AI Integration (V3.2).

Uses DeepSeek V3.2 for:
- Document analysis and extraction
- Complex reasoning tasks
- Agent decision making
- Cost-effective analysis operations
- Chain-of-Thought reasoning

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


class DeepSeekProvider(BaseLLMProvider):
    """
    DeepSeek LLM Provider (V3.2).
    
    DeepSeek V3.2 is optimized for:
    - Complex reasoning and analysis
    - Document understanding
    - Code generation
    - Multi-step problem solving
    - Chain-of-Thought reasoning
    
    Models (V3.2 - December 2024):
    - deepseek-chat: General chat model V3.2
    - deepseek-reasoner: Enhanced reasoning V3.2 with CoT
    
    API Format: OpenAI-compatible
    Base URL: https://api.deepseek.com/v1
    """
    
    # DeepSeek V3.2 models
    DEEPSEEK_CHAT = "deepseek-chat"          # V3.2 general purpose
    DEEPSEEK_REASONER = "deepseek-reasoner"  # V3.2 with Chain-of-Thought
    
    DEFAULT_MODEL = DEEPSEEK_CHAT
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize DeepSeek provider."""
        super().__init__(config)
        
        settings = get_settings()
        self._api_key = settings.deepseek_api_key
        self._base_url = "https://api.deepseek.com/v1"
        
        if not self._api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
        
        # Set default model if not specified
        if self._config.model == "gpt-4o-mini":
            self._config.model = self.DEFAULT_MODEL
        
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,  # Longer timeout for reasoning tasks
        )
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate response using DeepSeek."""
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
        """Stream response from DeepSeek."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        async for chunk in self._stream_api(messages, **kwargs):
            yield chunk
    
    async def generate_with_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate response using DeepSeek Reasoner (R1).
        
        Best for complex analysis, document extraction,
        and multi-step reasoning tasks.
        """
        # Force reasoner model
        kwargs["model"] = self.DEEPSEEK_REASONER
        
        return await self.generate(prompt, system_prompt, **kwargs)
    
    async def extract_structured_data(
        self,
        content: str,
        schema_description: str,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Extract structured data from text using DeepSeek.
        
        Args:
            content: Text to extract data from
            schema_description: Description of expected output format
            
        Returns:
            LLMResponse with extracted data
        """
        system_prompt = """You are a data extraction expert. 
Extract information from the provided text and return it in the specified format.
Be thorough but only include information that is explicitly stated or strongly implied.
Return valid JSON."""
        
        prompt = f"""Extract data from the following text according to this schema:

SCHEMA:
{schema_description}

TEXT TO ANALYZE:
{content}

Return the extracted data as valid JSON."""
        
        return await self.generate(prompt, system_prompt, **kwargs)
    
    async def _call_api(
        self,
        messages: list[dict],
        **kwargs: Any,
    ) -> LLMResponse:
        """Make API call to DeepSeek."""
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
        
        # Add frequency/presence penalties if set
        if self._config.frequency_penalty != 0:
            payload["frequency_penalty"] = self._config.frequency_penalty
        if self._config.presence_penalty != 0:
            payload["presence_penalty"] = self._config.presence_penalty
        
        try:
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            usage = data.get("usage", {})
            
            # Handle reasoning_content for R1 model
            content = data["choices"][0]["message"]["content"]
            reasoning_content = data["choices"][0]["message"].get("reasoning_content")
            
            metadata = {"provider": "deepseek"}
            if reasoning_content:
                metadata["reasoning"] = reasoning_content
            
            return LLMResponse(
                content=content,
                model=data.get("model", self._config.model),
                finish_reason=data["choices"][0].get("finish_reason", "stop"),
                usage=TokenUsage(
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                ),
                latency_ms=latency_ms,
                metadata=metadata,
            )
            
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "DeepSeek API error",
                status=e.response.status_code,
                detail=e.response.text,
            )
            raise
        except Exception as e:
            self.logger.error("DeepSeek generation failed", error=str(e))
            raise
    
    async def _stream_api(
        self,
        messages: list[dict],
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream API call to DeepSeek."""
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
                        
                        delta = data["choices"][0].get("delta", {})
                        if delta.get("content"):
                            yield delta["content"]
                            
        except Exception as e:
            self.logger.error("DeepSeek streaming failed", error=str(e))
            raise
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
