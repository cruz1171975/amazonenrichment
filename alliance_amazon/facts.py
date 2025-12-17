from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .utils import load_json


_GRADE_TERMS = [
    "Laboratory Grade",
    "Technical Grade",
    "Food Grade",
    "ACS Grade",
    "Reagent Grade",
    "Pharmaceutical Grade",
    "Industrial Grade",
    "USP Grade",
    "FCC Grade",
    "NF Grade",
]


@dataclass(frozen=True)
class FactsIssue:
    severity: str  # "error" | "warn"
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"severity": self.severity, "path": self.path, "message": self.message}


class FactsValidationError(ValueError):
    pass


def _as_dict(obj: Any) -> dict[str, Any] | None:
    if isinstance(obj, dict):
        return obj
    return None


def _get_str(data: dict[str, Any], key: str) -> str | None:
    val = data.get(key)
    if val is None:
        return None
    if not isinstance(val, str):
        return None
    s = val.strip()
    return s if s else None


def _iter_strings(values: Any) -> Iterable[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for v in values:
        if isinstance(v, str):
            s = v.strip()
            if s:
                out.append(s)
    return out


def validate_facts_card(data: Any) -> list[FactsIssue]:
    issues: list[FactsIssue] = []
    if not isinstance(data, dict):
        return [FactsIssue("error", "$", "Facts card must be a JSON object")]

    sku = _get_str(data, "sku")
    if not sku:
        issues.append(FactsIssue("error", "sku", "Required"))

    product_name = _get_str(data, "product_name")
    if not product_name:
        issues.append(FactsIssue("error", "product_name", "Required (Shopify title)"))

    brand = _get_str(data, "brand")
    if not brand:
        issues.append(FactsIssue("error", "brand", "Required"))

    specs = data.get("specifications") if isinstance(data.get("specifications"), dict) else {}
    grade = specs.get("grade") if isinstance(specs, dict) else None
    if grade is not None and not isinstance(grade, str):
        issues.append(FactsIssue("error", "specifications.grade", "Must be a string or null"))
    if isinstance(grade, str) and grade.strip():
        grade_s = grade.strip()
        if not product_name or grade_s.lower() not in product_name.lower():
            issues.append(
                FactsIssue(
                    "error",
                    "specifications.grade",
                    "Grade may only be used if it appears in product_name (Shopify title)",
                )
            )
        else:
            allowed = [g for g in _GRADE_TERMS if g.lower() in product_name.lower()]
            if allowed and grade_s.lower() not in {a.lower() for a in allowed}:
                issues.append(
                    FactsIssue(
                        "warn",
                        "specifications.grade",
                        f"Grade does not match a known grade term; allowed based on product_name: {allowed}",
                    )
                )

    cas = None
    chemical = data.get("chemical_identity")
    if isinstance(chemical, dict):
        cas = _get_str(chemical, "cas_number")
    if not cas:
        issues.append(FactsIssue("warn", "chemical_identity.cas_number", "Recommended"))

    apps = _iter_strings(data.get("applications"))
    if not apps:
        issues.append(FactsIssue("warn", "applications", "Recommended (helps generate bullets/keywords)"))

    safety = data.get("safety_summary")
    if not isinstance(safety, dict):
        issues.append(FactsIssue("warn", "safety_summary", "Recommended"))
    else:
        signal = _get_str(safety, "signal_word")
        if not signal:
            issues.append(FactsIssue("warn", "safety_summary.signal_word", "Recommended"))

    return issues


def load_facts_card(path: Path) -> dict[str, Any]:
    data = load_json(path)
    issues = validate_facts_card(data)
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        msg = "\n".join(f"{e.path}: {e.message}" for e in errors)
        raise FactsValidationError(f"Invalid facts card:\n{msg}")
    return data


def facts_from_shopify_product_dump(
    *,
    product_payload: Any,
    sku: str,
    brand: str = "Alliance Chemical",
    metafields_payload: Any | None = None,
) -> dict[str, Any]:
    """
    Convert a Shopify Admin API product payload (from a file) into a facts card.

    This is intentionally file-based (no network) to support restricted environments.
    """
    sku = sku.strip()
    if not sku:
        raise ValueError("sku is required")

    product_obj = _as_dict(product_payload)
    if product_obj and "product" in product_obj and isinstance(product_obj["product"], dict):
        product_obj = product_obj["product"]
    if not isinstance(product_obj, dict):
        raise ValueError("Unsupported Shopify product payload shape")

    title = _get_str(product_obj, "title") or ""
    variants = product_obj.get("variants")
    variant_match: dict[str, Any] | None = None
    if isinstance(variants, list):
        for v in variants:
            if isinstance(v, dict) and _get_str(v, "sku") and _get_str(v, "sku") == sku:
                variant_match = v
                break

    if variant_match is None:
        raise ValueError(f"SKU not found in Shopify product variants: {sku}")

    tags_raw = _get_str(product_obj, "tags") or ""
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    metafields: list[dict[str, Any]] = []
    if isinstance(metafields_payload, dict) and "metafields" in metafields_payload:
        mf = metafields_payload.get("metafields")
        if isinstance(mf, list):
            metafields = [m for m in mf if isinstance(m, dict)]
    elif isinstance(metafields_payload, list):
        metafields = [m for m in metafields_payload if isinstance(m, dict)]

    def mf_value(namespace: str, key: str) -> Any | None:
        for m in metafields:
            if m.get("namespace") == namespace and m.get("key") == key:
                return m.get("value")
        return None

    cas_number = mf_value("product_specs", "cas_number")
    purity_percentage = mf_value("product_specs", "purity_percentage")
    concentration = mf_value("product_specs", "concentration")
    physical_form = mf_value("product_specs", "physical_form")
    backend_keywords = mf_value("amazon", "backend_keywords")

    def _as_str(v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return None

    keywords_secondary = tags[:]
    if isinstance(backend_keywords, str) and backend_keywords.strip():
        # Keep as long_tail tokens; generator will filter and truncate.
        keywords_secondary.extend([t for t in backend_keywords.replace("\n", " ").split(" ") if t.strip()])

    facts: dict[str, Any] = {
        "sku": sku,
        "asin": None,
        "product_name": title or sku,
        "brand": brand,
        "chemical_identity": {
            "chemical_name": _as_str(mf_value("product_specs", "chemical_name")),
            "iupac_name": _as_str(mf_value("product_specs", "iupac_name")),
            "cas_number": _as_str(cas_number),
            "other_names": [],
        },
        "specifications": {
            "purity": _as_str(purity_percentage),
            "concentration": _as_str(concentration),
            "grade": None,
            "appearance": None,
            "odor": None,
            "ph": None,
            "specific_gravity": None,
            "boiling_point": None,
            "flash_point": None,
            "solubility": None,
        },
        "packaging": {
            "container_type": None,
            "sizes_available": [],
            "units_per_case": None,
            "shipping_weight": _as_str(variant_match.get("weight")) if isinstance(variant_match, dict) else None,
        },
        "applications": [],
        "certifications": [],
        "compatible_materials": [],
        "incompatible_materials": [],
        "storage": {
            "temperature": None,
            "conditions": None,
            "shelf_life": None,
            "special_requirements": None,
        },
        "safety_summary": {
            "signal_word": None,
            "primary_hazards": [],
            "ppe_required": [],
        },
        "approved_marketing_claims": [],
        "keywords": {
            "primary": [],
            "secondary": keywords_secondary,
            "application": [],
            "long_tail": [],
        },
        "sds_link": None,
        "tds_link": None,
        "last_updated": None,
        "updated_by": None,
    }

    if physical_form:
        facts["specifications"]["appearance"] = physical_form

    return facts
