"""
Tests for Grok and DeepSeek providers.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.llm.grok_provider import GrokProvider
from src.llm.deepseek_provider import DeepSeekProvider
from src.llm.base_provider import LLMConfig, Message


class TestGrokProvider:
    """Tests for GrokProvider."""
    
    def test_init_default_config(self):
        """Should initialize with default config."""
        with patch.object(GrokProvider, "_load_api_key", return_value="test-key"):
            provider = GrokProvider()
            assert provider.config.model == "grok-4-fast"
            assert provider.base_url == "https://api.x.ai/v1"
    
    def test_init_custom_config(self):
        """Should use custom config when provided."""
        config = LLMConfig(model="grok-4", temperature=0.5, max_tokens=2000)
        with patch.object(GrokProvider, "_load_api_key", return_value="test-key"):
            provider = GrokProvider(config)
            assert provider.config.model == "grok-4"
            assert provider.config.temperature == 0.5
    
    def test_get_available_models(self):
        """Should return available Grok models."""
        with patch.object(GrokProvider, "_load_api_key", return_value="test-key"):
            provider = GrokProvider()
            models = provider.get_available_models()
            assert "grok-4-fast" in models
            assert "grok-4" in models
            assert "grok-3-fast" in models
    
    @pytest.mark.asyncio
    async def test_generate(self):
        """Should generate text response."""
        mock_response = {
            "choices": [{"message": {"content": "Hello, I am Grok!"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }
        
        with patch.object(GrokProvider, "_load_api_key", return_value="test-key"):
            provider = GrokProvider()
            
            with patch.object(provider._client, "post", new_callable=AsyncMock) as mock_post:
                mock_post.return_value = MagicMock(json=lambda: mock_response)
                
                result = await provider.generate("Hello!")
                assert result == "Hello, I am Grok!"
    
    @pytest.mark.asyncio
    async def test_generate_chat(self):
        """Should generate chat response."""
        mock_response = {
            "choices": [{"message": {"content": "I am Grok, at your service."}}],
            "usage": {"prompt_tokens": 15, "completion_tokens": 25}
        }
        
        messages = [
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Who are you?"),
        ]
        
        with patch.object(GrokProvider, "_load_api_key", return_value="test-key"):
            provider = GrokProvider()
            
            with patch.object(provider._client, "post", new_callable=AsyncMock) as mock_post:
                mock_post.return_value = MagicMock(json=lambda: mock_response)
                
                response = await provider.generate_chat(messages)
                assert response.content == "I am Grok, at your service."
                assert response.model == "grok-4-fast"


class TestDeepSeekProvider:
    """Tests for DeepSeekProvider."""
    
    def test_init_default_config(self):
        """Should initialize with default config."""
        with patch.object(DeepSeekProvider, "_load_api_key", return_value="test-key"):
            provider = DeepSeekProvider()
            assert provider.config.model == "deepseek-chat"
            assert provider.base_url == "https://api.deepseek.com"
    
    def test_init_custom_config(self):
        """Should use custom config when provided."""
        config = LLMConfig(model="deepseek-reasoner", temperature=0.2)
        with patch.object(DeepSeekProvider, "_load_api_key", return_value="test-key"):
            provider = DeepSeekProvider(config)
            assert provider.config.model == "deepseek-reasoner"
            assert provider.config.temperature == 0.2
    
    def test_get_available_models(self):
        """Should return available DeepSeek models."""
        with patch.object(DeepSeekProvider, "_load_api_key", return_value="test-key"):
            provider = DeepSeekProvider()
            models = provider.get_available_models()
            assert "deepseek-chat" in models
            assert "deepseek-reasoner" in models
    
    @pytest.mark.asyncio
    async def test_generate(self):
        """Should generate text response."""
        mock_response = {
            "choices": [{"message": {"content": "The analysis shows..."}}],
            "usage": {"prompt_tokens": 50, "completion_tokens": 100}
        }
        
        with patch.object(DeepSeekProvider, "_load_api_key", return_value="test-key"):
            provider = DeepSeekProvider()
            
            with patch.object(provider._client, "post", new_callable=AsyncMock) as mock_post:
                mock_post.return_value = MagicMock(json=lambda: mock_response)
                
                result = await provider.generate("Analyze this text")
                assert result == "The analysis shows..."
    
    @pytest.mark.asyncio
    async def test_analyze_document(self):
        """Should analyze document and return structured data."""
        mock_response = {
            "choices": [{"message": {"content": '{"name": "Test Character"}'}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50}
        }
        
        with patch.object(DeepSeekProvider, "_load_api_key", return_value="test-key"):
            provider = DeepSeekProvider()
            
            with patch.object(provider._client, "post", new_callable=AsyncMock) as mock_post:
                mock_post.return_value = MagicMock(json=lambda: mock_response)
                
                result = await provider.analyze_document(
                    document="Character description...",
                    analysis_type="character_extraction",
                )
                
                assert "name" in result
                assert result["name"] == "Test Character"


class TestProviderIntegration:
    """Integration-style tests for providers."""
    
    def test_grok_provider_inherits_base(self):
        """GrokProvider should inherit from BaseLLMProvider."""
        from src.llm.base_provider import BaseLLMProvider
        with patch.object(GrokProvider, "_load_api_key", return_value="test-key"):
            provider = GrokProvider()
            assert isinstance(provider, BaseLLMProvider)
    
    def test_deepseek_provider_inherits_base(self):
        """DeepSeekProvider should inherit from BaseLLMProvider."""
        from src.llm.base_provider import BaseLLMProvider
        with patch.object(DeepSeekProvider, "_load_api_key", return_value="test-key"):
            provider = DeepSeekProvider()
            assert isinstance(provider, BaseLLMProvider)
    
    def test_providers_have_required_methods(self):
        """Providers should implement all required methods."""
        with patch.object(GrokProvider, "_load_api_key", return_value="test-key"):
            grok = GrokProvider()
            assert hasattr(grok, "generate")
            assert hasattr(grok, "generate_chat")
            assert hasattr(grok, "stream_generate")
        
        with patch.object(DeepSeekProvider, "_load_api_key", return_value="test-key"):
            deepseek = DeepSeekProvider()
            assert hasattr(deepseek, "generate")
            assert hasattr(deepseek, "generate_chat")
            assert hasattr(deepseek, "stream_generate")
            assert hasattr(deepseek, "analyze_document")


class TestErrorHandling:
    """Tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_grok_api_error(self):
        """Should handle API errors gracefully."""
        with patch.object(GrokProvider, "_load_api_key", return_value="test-key"):
            provider = GrokProvider()
            
            with patch.object(provider._client, "post", new_callable=AsyncMock) as mock_post:
                mock_post.side_effect = httpx.HTTPStatusError(
                    "Error",
                    request=MagicMock(),
                    response=MagicMock(status_code=500)
                )
                
                with pytest.raises(httpx.HTTPStatusError):
                    await provider.generate("Test")
    
    @pytest.mark.asyncio
    async def test_deepseek_api_error(self):
        """Should handle API errors gracefully."""
        with patch.object(DeepSeekProvider, "_load_api_key", return_value="test-key"):
            provider = DeepSeekProvider()
            
            with patch.object(provider._client, "post", new_callable=AsyncMock) as mock_post:
                mock_post.side_effect = httpx.HTTPStatusError(
                    "Error",
                    request=MagicMock(),
                    response=MagicMock(status_code=429)
                )
                
                with pytest.raises(httpx.HTTPStatusError):
                    await provider.generate("Test")
