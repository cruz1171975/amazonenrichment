from __future__ import annotations

import json
from dataclasses import dataclass

from .base import LlmClient, LlmRequest, LlmResponse


@dataclass
class MockLlmClient(LlmClient):
    response_text: str

    def generate(self, request: LlmRequest) -> LlmResponse:
        return LlmResponse(text=self.response_text, raw={"mock": True, "model": request.model})


def mock_listing_response_json() -> str:
    """
    Returns a minimal, compliant listing JSON string (used in offline tests).
    """
    payload = {
        "title": "Alliance Chemical Example Product - 1 Gallon",
        "bullets": [
            "Specifications: Example • CAS 67-63-0",
            "Applications: General solvent use",
        ],
        "description": "Example description. Always follow the SDS and use appropriate PPE.",
        "backend_keywords": ["example", "solvent", "chemical"],
        "a_plus_markdown": "# A+ Draft: Example\n\nSafety: Always follow the SDS.",
        "a_plus": {"version": 1, "modules": []},
        "evidence": {
            "title": ["facts.product_name"],
            "bullets": [["facts.chemical_identity.cas_number"], ["facts.applications[0]"]],
            "description": ["facts.safety_summary"],
            "backend_keywords": ["facts.keywords"],
        },
    }
    return json.dumps(payload)
