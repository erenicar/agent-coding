"""
Unit tests for Free Model Auto-Discovery and Dynamic Refresh.
"""

import pytest
from agent_coding.llm import LLMManager, FreeModelDiscoverer, FreeModelInfo, ProviderType


def test_known_free_models_list():
    discoverer = FreeModelDiscoverer()
    known = discoverer.fetch_known_free_models()

    assert len(known) > 0
    assert any(m.provider == ProviderType.GEMINI for m in known)
    assert any(m.provider == ProviderType.OLLAMA for m in known)
    assert any(m.supports_vision for m in known)


def test_refresh_free_models():
    discoverer = FreeModelDiscoverer()
    models = discoverer.refresh_free_models(force=force_refresh if 'force_refresh' in locals() else True)

    assert isinstance(models, list)
    assert len(models) >= len(discoverer.fetch_known_free_models())
    for m in models:
        assert isinstance(m, FreeModelInfo)
        assert m.is_free is True


def test_llm_manager_get_free_models():
    manager = LLMManager()
    free_models = manager.get_free_models()

    assert isinstance(free_models, list)
    assert len(free_models) > 0
