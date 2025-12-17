import json
import unittest
from pathlib import Path

from alliance_amazon.compliance.scanner import ScanConfig, scan_listing_fields, scan_text


class TestComplianceScanner(unittest.TestCase):
    def test_bad_listing_triggers_hard_findings(self) -> None:
        payload = json.loads(Path("examples/bad_listing.json").read_text(encoding="utf-8"))
        findings = scan_listing_fields(payload, config=ScanConfig())
        self.assertTrue(any(f.severity == "hard" for f in findings))

    def test_grade_unverified_is_hard(self) -> None:
        findings = scan_text("Food Grade", config=ScanConfig(), field="title")
        self.assertTrue(any(f.rule_id.startswith("RULE-GRADE") for f in findings))

    def test_grade_allowed_from_product_name(self) -> None:
        findings = scan_text(
            "Food Grade",
            config=ScanConfig(allow_grade_terms_from_product_name="Citric Acid Food Grade"),
            field="title",
        )
        self.assertFalse(any(f.rule_id.startswith("RULE-GRADE") for f in findings))

