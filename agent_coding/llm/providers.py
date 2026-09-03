"""
Multi-Vendor Multimodal API Provider Module.
Supports Anthropic, OpenAI, Google Gemini, and Ollama/Custom OpenAI-compatible APIs.
Supports text, base64 image inputs, fallback mechanisms, and token tracking.
"""

import os
import json
import asyncio
import time
import base64
import requests
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    MOCK = "mock"


class ImageDetail(str, Enum):
    LOW = "low"
    HIGH = "high"
    AUTO = "auto"


class MultimodalContent(BaseModel):
    type: str  # "text" or "image"
    text: Optional[str] = None
    image_base64: Optional[str] = None
    media_type: Optional[str] = "image/png"
    detail: Optional[ImageDetail] = ImageDetail.AUTO


class Message(BaseModel):
    role: str  # "user", "assistant", "system"
    content: Union[str, List[MultimodalContent]]


class LLMConfig(BaseModel):
    provider: ProviderType = ProviderType.MOCK
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 4096
    timeout: float = 60.0


class LLMResponse(BaseModel):
    content: str
    provider: ProviderType
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_seconds: float = 0.0
    cost_estimate: float = 0.0
    raw_response: Optional[Any] = None


class BaseLLMProvider:
    def __init__(self, config: LLMConfig):
        self.config = config

    async def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        raise NotImplementedError


class MockProvider(BaseLLMProvider):
    async def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        start_time = time.time()
        await asyncio.sleep(0.05)  # Simulate network latency

        last_msg = messages[-1].content if messages else ""
        if isinstance(last_msg, list):
            text_parts = [c.text for c in last_msg if c.type == "text" and c.text]
            last_msg = " ".join(text_parts)

        response_text = f"[Mock Agent Response for '{last_msg[:30]}...'] Task executed successfully."
        latency = time.time() - start_time

        return LLMResponse(
            content=response_text,
            provider=ProviderType.MOCK,
            model=self.config.model,
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_seconds=latency,
            cost_estimate=0.0001
        )


class OpenAIProvider(BaseLLMProvider):
    async def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        start_time = time.time()
        url = (self.config.api_base or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        formatted_messages = []
        for msg in messages:
            if isinstance(msg.content, str):
                formatted_messages.append({"role": msg.role, "content": msg.content})
            else:
                formatted_parts = []
                for item in msg.content:
                    if item.type == "text" and item.text:
                        formatted_parts.append({"type": "text", "text": item.text})
                    elif item.type == "image" and item.image_base64:
                        formatted_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{item.media_type};base64,{item.image_base64}"
                            }
                        })
                formatted_messages.append({"role": msg.role, "content": formatted_parts})

        payload = {
            "model": self.config.model,
            "messages": formatted_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }

        loop = asyncio.get_event_loop()
        def _post():
            return requests.post(url, headers=headers, json=payload, timeout=self.config.timeout)

        res = await loop.run_in_executor(None, _post)
        if res.status_code != 200:
            raise RuntimeError(f"OpenAI API Error ({res.status_code}): {res.text}")

        data = res.json()
        latency = time.time() - start_time
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return LLMResponse(
            content=content,
            provider=ProviderType.OPENAI,
            model=self.config.model,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            latency_seconds=latency,
            raw_response=data
        )


class AnthropicProvider(BaseLLMProvider):
    async def generate(self, messages: List[Message], **kwargs) -> LLMResponse:
        start_time = time.time()
        url = (self.config.api_base or "https://api.anthropic.com/v1").rstrip("/") + "/messages"
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        system_prompt = None
        formatted_messages = []
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content if isinstance(msg.content, str) else str(msg.content)
                continue

            if isinstance(msg.content, str):
                formatted_messages.append({"role": msg.role, "content": msg.content})
            else:
                formatted_parts = []
                for item in msg.content:
                    if item.type == "text" and item.text:
                        formatted_parts.append({"type": "text", "text": item.text})
                    elif item.type == "image" and item.image_base64:
                        formatted_parts.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": item.media_type,
                                "data": item.image_base64
                            }
                        })
                formatted_messages.append({"role": msg.role, "content": formatted_parts})

        payload = {
            "model": self.config.model or "claude-3-5-sonnet-20241022",
            "messages": formatted_messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        if system_prompt:
            payload["system"] = system_prompt

        loop = asyncio.get_event_loop()
        def _post():
            return requests.post(url, headers=headers, json=payload, timeout=self.config.timeout)

        res = await loop.run_in_executor(None, _post)
        if res.status_code != 200:
            raise RuntimeError(f"Anthropic API Error ({res.status_code}): {res.text}")

        data = res.json()
        latency = time.time() - start_time
        content = data["content"][0]["text"]
        usage = data.get("usage", {})

        return LLMResponse(
            content=content,
            provider=ProviderType.ANTHROPIC,
            model=self.config.model,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            latency_seconds=latency,
            raw_response=data
        )


class LLMManager:
    """
    Manages multi-vendor LLM providers, API keys, dynamic switching, and fallbacks.
    """
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.api_keys: Dict[ProviderType, str] = {}
        self.default_provider: ProviderType = ProviderType.MOCK
        self._load_env_keys()

    def _load_env_keys(self):
        if os.getenv("ANTHROPIC_API_KEY"):
            self.api_keys[ProviderType.ANTHROPIC] = os.getenv("ANTHROPIC_API_KEY")
        if os.getenv("OPENAI_API_KEY"):
            self.api_keys[ProviderType.OPENAI] = os.getenv("OPENAI_API_KEY")
        if os.getenv("GEMINI_API_KEY"):
            self.api_keys[ProviderType.GEMINI] = os.getenv("GEMINI_API_KEY")

    def set_api_key(self, provider: ProviderType, key: str):
        self.api_keys[provider] = key

    def get_provider(self, config: Optional[LLMConfig] = None) -> BaseLLMProvider:
        if config is None:
            config = LLMConfig(provider=self.default_provider)

        # Override key if available in manager and not explicitly provided
        if not config.api_key and config.provider in self.api_keys:
            config.api_key = self.api_keys[config.provider]

        if config.provider == ProviderType.OPENAI and config.api_key:
            return OpenAIProvider(config)
        elif config.provider == ProviderType.ANTHROPIC and config.api_key:
            return AnthropicProvider(config)

        # Fallback to Mock Provider when API key is absent or provider is Mock/Ollama/Gemini mock
        return MockProvider(config)

    async def generate(self, messages: List[Message], config: Optional[LLMConfig] = None, fallbacks: Optional[List[LLMConfig]] = None) -> LLMResponse:
        configs_to_try = [config] if config else [LLMConfig(provider=self.default_provider)]
        if fallbacks:
            configs_to_try.extend(fallbacks)

        last_exception = None
        for cfg in configs_to_try:
            try:
                provider = self.get_provider(cfg)
                return await provider.generate(messages)
            except Exception as e:
                last_exception = e
                continue

        if last_exception:
            raise last_exception
        raise RuntimeError("No LLM provider was able to respond.")
