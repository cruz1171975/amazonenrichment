import json
import unittest
from pathlib import Path

from alliance_amazon.facts import facts_from_shopify_product_dump, load_facts_card, validate_facts_card
from alliance_amazon.listing.generator import GenerationOptions, generate_listing


class TestFactsAndListing(unittest.TestCase):
    def test_example_facts_validate(self) -> None:
        data = json.loads(Path("examples/facts_isopropyl_alcohol.json").read_text(encoding="utf-8"))
        issues = validate_facts_card(data)
        self.assertFalse([i for i in issues if i.severity == "error"])

    def test_listing_generation_passes_compliance(self) -> None:
        facts = load_facts_card(Path("examples/facts_isopropyl_alcohol.json"))
        listing = generate_listing(facts, options=GenerationOptions(size="1 Gallon"))
        self.assertEqual(listing["compliance_status"], "pass")

    def test_shopify_import(self) -> None:
        product_payload = json.loads(Path("examples/shopify_product_example.json").read_text(encoding="utf-8"))
        metafields_payload = json.loads(
            Path("examples/shopify_metafields_example.json").read_text(encoding="utf-8")
        )
        facts = facts_from_shopify_product_dump(
            product_payload=product_payload,
            metafields_payload=metafields_payload,
            sku="AC-IPA-99-1G",
        )
        issues = validate_facts_card(facts)
        self.assertFalse([i for i in issues if i.severity == "error"])

