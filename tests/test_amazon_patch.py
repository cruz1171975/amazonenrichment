import unittest

from alliance_amazon.amazon.patch import PatchBuildOptions, build_listings_item_patch


class TestAmazonPatch(unittest.TestCase):
    def test_build_patch_contains_expected_attributes(self) -> None:
        listing = {
            "title": "Alliance Chemical Example - 1 Gallon",
            "bullets": ["One", "Two"],
            "description": "Desc",
            "backend_search_terms": "keyword1 keyword2 keyword3",
        }
        body = build_listings_item_patch(
            listing=listing,
            options=PatchBuildOptions(marketplace_id="ATVPDKIKX0DER", language_tag="en_US", product_type=None),
        )
        paths = [p["path"] for p in body["patches"]]
        self.assertIn("/attributes/item_name", paths)
        self.assertIn("/attributes/bullet_point", paths)
        self.assertIn("/attributes/product_description", paths)
        self.assertIn("/attributes/generic_keyword", paths)

