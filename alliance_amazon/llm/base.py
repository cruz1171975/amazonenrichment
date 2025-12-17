from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LlmRequest:
    model: str
    prompt: str


@dataclass(frozen=True)
class LlmResponse:
    text: str
    raw: dict | None = None


class LlmClient:
    def generate(self, request: LlmRequest) -> LlmResponse:  # pragma: no cover
        raise NotImplementedError

