import unittest
from pathlib import Path

from alliance_amazon.flatfile.generate import FlatFileOptions, generate_flat_file_rows
from alliance_amazon.listing.generator import GenerationOptions
from alliance_amazon.facts import load_facts_card


class TestFlatFile(unittest.TestCase):
    def test_can_read_template_headers_and_generate_row(self) -> None:
        template = Path("LAB_CHEMICAL (Blank).xlsm")
        self.assertTrue(template.exists())

        facts = load_facts_card(Path("examples/facts_isopropyl_alcohol.json"))
        headers, row = generate_flat_file_rows(
            template_xlsm=template,
            facts=facts,
            listing_options=GenerationOptions(size="1 Gallon"),
            flatfile_options=FlatFileOptions(product_type="LAB_CHEMICAL"),
        )
        self.assertGreaterEqual(len(headers), 50)
        self.assertEqual(len(headers), len(row))
        self.assertIn("::record_action", headers)
        self.assertEqual(row[headers.index("::record_action")], "full_update")

