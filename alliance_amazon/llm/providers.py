from __future__ import annotations

from .base import LlmClient
from .gemini import GeminiClient
from .mock import MockLlmClient, mock_listing_response_json


def make_llm_client(provider: str) -> LlmClient:
    p = (provider or "").strip().lower()
    if p in ("gemini", "google"):
        return GeminiClient()
    if p in ("mock", "test"):
        return MockLlmClient(response_text=mock_listing_response_json())
    raise ValueError(f"Unknown LLM provider: {provider!r}")

