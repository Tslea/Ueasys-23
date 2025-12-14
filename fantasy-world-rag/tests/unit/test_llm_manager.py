"""
Tests for LLM Manager and Provider System.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.llm.llm_manager import (
    LLMManager,
    ProviderType,
    ModelConfig,
    get_chat_llm,
    get_analysis_llm,
    get_agent_llm,
    get_llm,
)
from src.llm.base_provider import LLMConfig, BaseLLMProvider


class TestProviderType:
    """Tests for ProviderType enum."""
    
    def test_provider_types_exist(self):
        """All expected provider types should exist."""
        assert ProviderType.GROK == "grok"
        assert ProviderType.DEEPSEEK == "deepseek"
        assert ProviderType.OPENAI == "openai"
        assert ProviderType.ANTHROPIC == "anthropic"


class TestModelConfig:
    """Tests for model configurations."""
    
    def test_grok_4_fast_config(self):
        """Grok 4 Fast should have correct configuration."""
        config = ModelConfig.GROK_4_FAST
        assert config["provider"] == ProviderType.GROK
        assert config["model"] == "grok-4-fast"
        assert "chat" in config["best_for"]
    
    def test_deepseek_chat_config(self):
        """DeepSeek Chat should have correct configuration."""
        config = ModelConfig.DEEPSEEK_CHAT
        assert config["provider"] == ProviderType.DEEPSEEK
        assert config["model"] == "deepseek-chat"
        assert "analysis" in config["best_for"]


class TestLLMManager:
    """Tests for LLMManager."""
    
    def test_list_providers(self):
        """Should list all available providers."""
        providers = LLMManager.list_providers()
        assert "grok" in providers
        assert "deepseek" in providers
        assert "openai" in providers
        assert "anthropic" in providers
    
    def test_get_model_info(self):
        """Should return model info for known models."""
        info = LLMManager.get_model_info("grok-4-fast")
        assert info is not None
        assert info["model"] == "grok-4-fast"
        
        info = LLMManager.get_model_info("unknown-model")
        assert info is None
    
    @patch("src.llm.llm_manager.GrokProvider")
    def test_get_grok_provider(self, mock_grok):
        """Should return Grok provider."""
        # Clear cache
        LLMManager._providers.clear()
        
        mock_instance = MagicMock()
        mock_instance.config = LLMConfig(model="grok-4-fast")
        mock_grok.return_value = mock_instance
        
        provider = LLMManager.get_provider("grok")
        assert provider is not None
    
    @patch("src.llm.llm_manager.DeepSeekProvider")
    def test_get_deepseek_provider(self, mock_deepseek):
        """Should return DeepSeek provider."""
        # Clear cache
        LLMManager._providers.clear()
        
        mock_instance = MagicMock()
        mock_instance.config = LLMConfig(model="deepseek-chat")
        mock_deepseek.return_value = mock_instance
        
        provider = LLMManager.get_provider(ProviderType.DEEPSEEK)
        assert provider is not None
    
    def test_set_default_chat_provider(self):
        """Should update default chat provider."""
        original = LLMManager._chat_provider
        LLMManager.set_default_chat_provider("deepseek")
        assert LLMManager._chat_provider == ProviderType.DEEPSEEK
        # Reset
        LLMManager._chat_provider = original
    
    def test_set_default_analysis_provider(self):
        """Should update default analysis provider."""
        original = LLMManager._analysis_provider
        LLMManager.set_default_analysis_provider("grok")
        assert LLMManager._analysis_provider == ProviderType.GROK
        # Reset
        LLMManager._analysis_provider = original


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    @patch.object(LLMManager, "get_chat_provider")
    def test_get_chat_llm(self, mock_method):
        """get_chat_llm should call LLMManager.get_chat_provider."""
        get_chat_llm()
        mock_method.assert_called_once()
    
    @patch.object(LLMManager, "get_analysis_provider")
    def test_get_analysis_llm(self, mock_method):
        """get_analysis_llm should call LLMManager.get_analysis_provider."""
        get_analysis_llm()
        mock_method.assert_called_once()
    
    @patch.object(LLMManager, "get_agent_provider")
    def test_get_agent_llm(self, mock_method):
        """get_agent_llm should call LLMManager.get_agent_provider."""
        get_agent_llm()
        mock_method.assert_called_once()
    
    @patch.object(LLMManager, "get_provider")
    def test_get_llm(self, mock_method):
        """get_llm should call LLMManager.get_provider."""
        get_llm("grok")
        mock_method.assert_called_once_with("grok", None)


class TestProviderCaching:
    """Tests for provider caching."""
    
    @patch("src.llm.llm_manager.GrokProvider")
    def test_provider_caching(self, mock_grok):
        """Providers should be cached."""
        # Clear cache
        LLMManager._providers.clear()
        
        mock_instance = MagicMock()
        mock_instance.config = LLMConfig(model="grok-4-fast")
        mock_grok.return_value = mock_instance
        
        # First call
        provider1 = LLMManager.get_provider("grok")
        # Second call
        provider2 = LLMManager.get_provider("grok")
        
        # Should be same instance
        assert provider1 is provider2
        # Constructor called only once
        assert mock_grok.call_count == 1
    
    @patch("src.llm.llm_manager.GrokProvider")
    def test_force_new_provider(self, mock_grok):
        """force_new should create new provider instance."""
        # Clear cache
        LLMManager._providers.clear()
        
        mock_grok.return_value = MagicMock()
        mock_grok.return_value.config = LLMConfig(model="grok-4-fast")
        
        # First call
        LLMManager.get_provider("grok")
        # Force new
        LLMManager.get_provider("grok", force_new=True)
        
        # Constructor called twice
        assert mock_grok.call_count == 2


class TestCustomConfig:
    """Tests for custom configuration."""
    
    @patch("src.llm.llm_manager.GrokProvider")
    def test_custom_config_not_cached(self, mock_grok):
        """Custom config providers should not be cached."""
        # Clear cache
        LLMManager._providers.clear()
        
        mock_grok.return_value = MagicMock()
        mock_grok.return_value.config = LLMConfig(model="custom")
        
        custom_config = LLMConfig(model="grok-4", temperature=0.9)
        
        # Get with custom config
        LLMManager.get_provider("grok", custom_config)
        
        # Should not be in cache
        assert ProviderType.GROK not in LLMManager._providers


@pytest.mark.asyncio
class TestAsyncMethods:
    """Tests for async methods."""
    
    async def test_close_all(self):
        """Should close all providers."""
        # Clear existing
        LLMManager._providers.clear()
        
        # Add mock providers
        mock_provider = AsyncMock()
        mock_provider.close = AsyncMock()
        LLMManager._providers[ProviderType.GROK] = mock_provider
        
        await LLMManager.close_all()
        
        mock_provider.close.assert_called_once()
        assert len(LLMManager._providers) == 0
