import unittest
from pathlib import Path

from alliance_amazon.facts import load_facts_card
from alliance_amazon.listing.generator import GenerationOptions, generate_listing
from alliance_amazon.llm.mock import MockLlmClient, mock_listing_response_json
from alliance_amazon.llm.runner import generate_listing_with_llm


class TestLlmRunner(unittest.TestCase):
    def test_llm_rewrite_with_mock_passes(self) -> None:
        facts = load_facts_card(Path("examples/facts_isopropyl_alcohol.json"))
        base = generate_listing(facts, options=GenerationOptions(size="1 Gallon"))
        client = MockLlmClient(response_text=mock_listing_response_json())
        result = generate_listing_with_llm(
            facts=facts,
            base_listing={
                "title": base["title"],
                "bullets": base["bullets"],
                "description": base["description"],
                "backend_search_terms": base["backend_search_terms"],
                "a_plus_markdown": base.get("a_plus_markdown", ""),
                "a_plus": base.get("a_plus", {}),
            },
            client=client,
            model="gemini-3-flash-preview",
        )
        self.assertEqual(result.compliance_status, "pass")
        self.assertFalse(result.used_fallback)

