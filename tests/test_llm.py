"""
Unit tests for Multi-Vendor LLM Manager and Providers.
"""

import pytest
import asyncio
from agent_coding.llm import LLMManager, LLMConfig, ProviderType, Message, MultimodalContent


@pytest.mark.asyncio
async def test_llm_manager_generate():
    manager = LLMManager()
    config = LLMConfig(provider=ProviderType.MOCK, model="test-model")
    messages = [Message(role="user", content="Hello LLM")]

    response = await manager.generate(messages, config=config)

    assert response is not None
    assert response.provider == ProviderType.MOCK
    assert "Mock Agent Response" in response.content
    assert response.total_tokens > 0


@pytest.mark.asyncio
async def test_llm_manager_multimodal_content():
    manager = LLMManager()
    config = LLMConfig(provider=ProviderType.MOCK)
    messages = [
        Message(
            role="user",
            content=[
                MultimodalContent(type="text", text="Inspect this image"),
                MultimodalContent(type="image", image_base64="aW1hZ2VfZGF0YQ==")
            ]
        )
    ]

    response = await manager.generate(messages, config=config)

    assert response is not None
    assert "Inspect this image" in response.content


def test_set_api_key():
    manager = LLMManager()
    manager.set_api_key(ProviderType.ANTHROPIC, "test-anthropic-key")
    assert manager.api_keys[ProviderType.ANTHROPIC] == "test-anthropic-key"
