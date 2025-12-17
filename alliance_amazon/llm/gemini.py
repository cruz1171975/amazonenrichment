from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from .base import LlmClient, LlmRequest, LlmResponse


@dataclass
class GeminiClient(LlmClient):
    """
    Minimal client for the Google Generative Language API (Gemini).

    This is intentionally dependency-free; network access and API keys are required at runtime.
    """

    api_key: str | None = None
    api_base: str = "https://generativelanguage.googleapis.com"
    api_version: str = "v1beta"
    timeout_s: float = 60.0

    def generate(self, request: LlmRequest) -> LlmResponse:
        api_key = self.api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY (set env var or pass api_key)")

        model = request.model.strip()
        if not model:
            raise ValueError("model is required")

        url = (
            f"{self.api_base}/{self.api_version}/models/"
            f"{urllib.parse.quote(model, safe='')}:generateContent?key={urllib.parse.quote(api_key)}"
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": request.prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048,
            },
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
            raise RuntimeError(f"Gemini API HTTP error: {e.code}: {detail}") from e
        except Exception as e:
            raise RuntimeError(f"Gemini API request failed: {e}") from e

        text = _extract_text(raw)
        return LlmResponse(text=text, raw=raw)


def _extract_text(raw: dict) -> str:
    # Typical response: candidates[0].content.parts[0].text
    try:
        candidates = raw.get("candidates") or []
        if not candidates:
            return ""
        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        texts = []
        for p in parts:
            if isinstance(p, dict) and isinstance(p.get("text"), str):
                texts.append(p["text"])
        return "".join(texts).strip()
    except Exception:
        return ""
