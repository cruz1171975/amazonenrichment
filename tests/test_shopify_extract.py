import unittest

from alliance_amazon.shopify.fetch import ShopifySkuFetchResult
from alliance_amazon.shopify.extract import build_facts_from_shopify


class TestShopifyExtract(unittest.TestCase):
    def test_build_facts_from_shopify_filters_keywords_and_uses_option2(self) -> None:
        fetched = ShopifySkuFetchResult(
            sku="AC-TEST-1G",
            product={
                "id": "gid://shopify/Product/1",
                "title": "Isopropyl Alcohol 99% Technical Grade",
                "handle": "isopropyl-alcohol",
                "vendor": "Alliance Chemical",
                "tags": "ipa, disinfect",  # disinfect should be blocked
                "description": "",
                "descriptionHtml": "",
                "variants": {
                    "edges": [
                        {"node": {"sku": "AC-TEST-1G", "selectedOptions": [{"name": "Color", "value": "N/A"}, {"name": "Size", "value": "1 Gallon"}]}},
                        {"node": {"sku": "AC-TEST-5G", "selectedOptions": [{"name": "Color", "value": "N/A"}, {"name": "Size", "value": "5 Gallon"}]}},
                    ]
                },
            },
            variant={
                "id": "gid://shopify/ProductVariant/1",
                "sku": "AC-TEST-1G",
                "selectedOptions": [{"name": "Color", "value": "N/A"}, {"name": "Size", "value": "1 Gallon"}],
            },
            product_metafields={
                "product_details.cas_number": "67-63-0",
                "filters.percentage": "99%",
                "chem.keywords": "ipa disinfect solvent",
            },
            variant_metafields={},
        )
        built = build_facts_from_shopify(fetched)
        self.assertEqual(built.facts["sku"], "AC-TEST-1G")
        self.assertEqual(built.report["size_from_option2"], "1 Gallon")
        self.assertIn("1 Gallon", built.facts["packaging"]["sizes_available"])
        self.assertIn("5 Gallon", built.facts["packaging"]["sizes_available"])
        # blocked keyword should appear in report
        self.assertTrue(any("disinfect" in k.lower() for k in built.report["blocked_keywords"]))

