"""
Free Model Auto-Discovery and Dynamic Refresh Module.
Fetches, lists, and auto-updates available free-tier models from providers (Google Gemini, OpenRouter, HuggingFace, Ollama, etc.).
"""

import time
import requests
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    MOCK = "mock"


class FreeModelInfo(BaseModel):
    model_id: str
    provider: ProviderType
    display_name: str
    description: str
    context_window: int = 8192
    supports_vision: bool = False
    is_free: bool = True


class FreeModelDiscoverer:
    """
    Auto-discovers free LLM models across multiple AI companies & platforms.
    """
    def __init__(self):
        self._cached_models: List[FreeModelInfo] = []
        self._last_refresh: float = 0.0
        self.cache_ttl_seconds: float = 3600.0  # 1 hour cache TTL

    @staticmethod
    def fetch_known_free_models() -> List[FreeModelInfo]:
        """
        Returns built-in list of popular guaranteed free-tier / free-access LLMs across vendors.
        """
        return [
            # Google Gemini Free Tier
            FreeModelInfo(
                model_id="gemini-1.5-flash",
                provider=ProviderType.GEMINI,
                display_name="Gemini 1.5 Flash (Free Tier)",
                description="Google's fast multimodal model with generous free tier RPM/TPM limits.",
                context_window=1000000,
                supports_vision=True
            ),
            FreeModelInfo(
                model_id="gemini-2.0-flash-exp",
                provider=ProviderType.GEMINI,
                display_name="Gemini 2.0 Flash Experimental (Free)",
                description="Google's latest experimental multimodal model with high speed and zero cost.",
                context_window=1000000,
                supports_vision=True
            ),
            # Ollama Local Free Models
            FreeModelInfo(
                model_id="ollama/qwen2.5-coder",
                provider=ProviderType.OLLAMA,
                display_name="Qwen 2.5 Coder (Ollama Local / Free)",
                description="Open-weights top coding model running locally or self-hosted for free.",
                context_window=32768,
                supports_vision=False
            ),
            FreeModelInfo(
                model_id="ollama/llama3.2-vision",
                provider=ProviderType.OLLAMA,
                display_name="Llama 3.2 Vision (Ollama Local / Free)",
                description="Open multimodal model running locally without API key requirements.",
                context_window=128000,
                supports_vision=True
            ),
            # OpenRouter Free Tier
            FreeModelInfo(
                model_id="openrouter/meta-llama/llama-3.3-70b-instruct:free",
                provider=ProviderType.OPENAI,
                display_name="Llama 3.3 70B Instruct (OpenRouter Free)",
                description="State-of-the-art open model hosted for free via OpenRouter API.",
                context_window=131072,
                supports_vision=False
            ),
            FreeModelInfo(
                model_id="openrouter/google/gemini-2.0-flash-exp:free",
                provider=ProviderType.OPENAI,
                display_name="Gemini 2.0 Flash Exp (OpenRouter Free)",
                description="Gemini 2.0 Flash access provided free of charge on OpenRouter.",
                context_window=1000000,
                supports_vision=True
            ),
            # Mock Provider
            FreeModelInfo(
                model_id="mock-agent-free",
                provider=ProviderType.MOCK,
                display_name="Mock Agent Engine (Offline Free)",
                description="Built-in offline agent simulator for testing without internet or keys.",
                context_window=16384,
                supports_vision=True
            )
        ]

    def refresh_free_models(self, force: bool = False) -> List[FreeModelInfo]:
        """
        Dynamically refreshes and updates free models from online endpoints & registries.
        """
        now = time.time()
        if not force and self._cached_models and (now - self._last_refresh < self.cache_ttl_seconds):
            return self._cached_models

        models = self.fetch_known_free_models()

        # Dynamic query to OpenRouter free models API endpoint if online
        try:
            res = requests.get("https://openrouter.ai/api/v1/models", timeout=5.0)
            if res.status_code == 200:
                data = res.json()
                for item in data.get("data", []):
                    m_id = item.get("id", "")
                    if m_id.endswith(":free"):
                        models.append(
                            FreeModelInfo(
                                model_id=f"openrouter/{m_id}",
                                provider=ProviderType.OPENAI,
                                display_name=f"{item.get('name', m_id)} (Free API)",
                                description=item.get("description", "Free model on OpenRouter platform")[:120],
                                context_window=item.get("context_length", 32768),
                                supports_vision="vision" in m_id.lower() or "multimodal" in m_id.lower()
                            )
                        )
        except Exception:
            pass  # Fallback gracefully to offline known free models

        self._cached_models = models
        self._last_refresh = now
        return self._cached_models
