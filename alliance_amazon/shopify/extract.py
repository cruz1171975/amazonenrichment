from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from ..compliance.scanner import ScanConfig, scan_text
from ..keywords import filter_keywords
from .fetch import ShopifySkuFetchResult, parse_metafield_value


_KNOWN_GRADE_TERMS = [
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


def _clean(s: Any) -> str:
    if not isinstance(s, str):
        return ""
    return " ".join(s.strip().split())

def _as_str_list(value: Any) -> list[str]:
    parsed = parse_metafield_value(value)
    out: list[str] = []
    if isinstance(parsed, list):
        for x in parsed:
            s = _clean(x)
            if s:
                out.append(s)
        return out
    if isinstance(parsed, str):
        s = parsed.strip()
        if not s:
            return []
        # Comma-separated
        if "," in s:
            parts = [p.strip() for p in s.split(",")]
            return [p for p in parts if p]
        return [s]
    return out


def _option2_value(variant: dict[str, Any]) -> str:
    opts = variant.get("selectedOptions")
    if not isinstance(opts, list):
        return ""
    values = []
    for o in opts:
        if isinstance(o, dict) and isinstance(o.get("value"), str):
            values.append(o["value"])
    if len(values) >= 2:
        return _clean(values[1])
    return ""


def _extract_sizes(product: dict[str, Any]) -> list[str]:
    variants = (product.get("variants") or {}).get("edges") or []
    out: list[str] = []
    seen = set()
    for edge in variants:
        node = (edge or {}).get("node") or {}
        opts = node.get("selectedOptions")
        if not isinstance(opts, list):
            continue
        values = []
        for o in opts:
            if isinstance(o, dict) and isinstance(o.get("value"), str):
                values.append(o["value"])
        if len(values) >= 2:
            v = _clean(values[1])
            if v and v.lower() not in seen:
                seen.add(v.lower())
                out.append(v)
    return out


def _grade_allowed(product_name: str, grade: str) -> str:
    if not grade:
        return ""
    pn = product_name.lower()
    for g in _KNOWN_GRADE_TERMS:
        if grade.lower() == g.lower() and g.lower() in pn:
            return g
    # If the metafield grade isn't an exact known term, only allow if it's exactly present in title.
    if grade.lower() in pn:
        return grade
    return ""

def _extract_percent_from_title(title: str) -> str:
    # Matches "40%" or "40 %"
    m = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", title)
    if not m:
        return ""
    return f"{m.group(1)}%"


def _derive_chemical_name_from_title(title: str) -> str:
    t = _clean(title)
    if not t:
        return ""
    # Remove trailing % and any grade phrases
    t = re.sub(r"\d{1,3}(?:\.\d+)?\s*%", "", t, flags=re.IGNORECASE)
    for g in _KNOWN_GRADE_TERMS:
        t = re.sub(re.escape(g), "", t, flags=re.IGNORECASE)
    t = " ".join(t.split())
    return t.strip(" -–—")


def _split_keywords(value: Any) -> list[str]:
    parsed = parse_metafield_value(value)
    out: list[str] = []
    if isinstance(parsed, list):
        for x in parsed:
            s = _clean(x)
            if s:
                out.append(s)
        return out
    if isinstance(parsed, str):
        s = parsed.replace("\n", " ").replace("\t", " ").strip()
        # Allow comma-separated or space-separated.
        if "," in s:
            parts = [p.strip() for p in s.split(",")]
        else:
            parts = [p.strip() for p in s.split(" ")]
        return [p for p in parts if p]
    return out


def _redact_hard_terms(text: str, *, product_name_for_grade: str) -> tuple[str, list[str]]:
    config = ScanConfig(allow_grade_terms_from_product_name=product_name_for_grade)
    findings = scan_text(text, config=config, field="text")
    removed: list[str] = []
    redacted = text
    # Remove both hard and soft blocklist terms from Shopify sources by default.
    for f in findings:
        # Remove exact matched substring occurrences (case-insensitive match already given in f.match).
        m = f.match
        if not m:
            continue
        removed.append(m)
        redacted = redacted.replace(m, "")
        redacted = redacted.replace(m.lower(), "")
        redacted = redacted.replace(m.upper(), "")
    redacted = " ".join(redacted.split())
    return redacted, removed


@dataclass(frozen=True)
class ShopifyFactsBuildResult:
    facts: dict[str, Any]
    report: dict[str, Any]


def build_facts_from_shopify(fetch: ShopifySkuFetchResult) -> ShopifyFactsBuildResult:
    product = fetch.product
    variant = fetch.variant
    mfp = {k: parse_metafield_value(v) for k, v in fetch.product_metafields.items()}

    raw_title = _clean(product.get("title"))
    safe_title, removed_from_title = _redact_hard_terms(raw_title, product_name_for_grade=raw_title or "")

    vendor = _clean(product.get("vendor"))
    brand = vendor or "Alliance Chemical"

    cas = _clean(mfp.get("product_details.cas_number"))
    formula = _clean(mfp.get("product_details.formula"))
    mw = _clean(mfp.get("product_details.molecular_weight"))
    flash = _clean(mfp.get("product_details.flash_point"))
    form = _clean(mfp.get("product_details.form") or mfp.get("filters.form"))
    solubility = _clean(mfp.get("product_details.solubility"))
    appearance = _clean(mfp.get("product_details.appearance"))
    mp = _clean(mfp.get("product_details.melting_point"))
    bp = _clean(mfp.get("product_details.boiling_point"))
    sg = _clean(mfp.get("custom.specific_gravity"))
    grade_raw = _clean(mfp.get("product_details.grade") or mfp.get("filters.grade"))
    grade = _grade_allowed(raw_title, grade_raw)

    purity = _clean(mfp.get("filters.percentage"))
    purity_val = purity if purity and purity.endswith("%") else ""
    percent_from_title = _extract_percent_from_title(raw_title)
    if not purity_val and percent_from_title:
        # Treat percent in title as concentration for solutions.
        concentration_val = percent_from_title
    else:
        concentration_val = ""

    sds = _clean(mfp.get("custom.safety_data_sheet"))
    industries = _as_str_list(mfp.get("filters.industry"))
    shipping_group = _clean(mfp.get("shipperhq.shipperhq_shipping_group"))
    dim_group = _clean(mfp.get("shipperhq.shipperhq_dim_group"))

    mvv = {k: parse_metafield_value(v) for k, v in fetch.variant_metafields.items()}
    dims = {
        "length_in": _clean(mvv.get("global.LENGTH")),
        "width_in": _clean(mvv.get("global.WIDTH")),
        "height_in": _clean(mvv.get("global.HEIGHT")),
    }

    # Optional Shopify descriptions as facts (will still be compliance-scanned later).
    raw_pd = _clean(mfp.get("product_details.product_description"))
    raw_seo_desc = _clean(mfp.get("product_details.seo_description"))
    safe_pd, removed_pd = _redact_hard_terms(raw_pd, product_name_for_grade=raw_title)
    safe_seo_desc, removed_seo_desc = _redact_hard_terms(raw_seo_desc, product_name_for_grade=raw_title)

    def extract_uses(text: str) -> list[str]:
        # Extracts phrases after "used in/used for" up to the next period.
        m = re.search(r"(?i)\bused\s+(?:in|for)\s+([^.]{5,200})(?:\.|$)", text)
        if not m:
            return []
        chunk = m.group(1)
        chunk = chunk.replace(" and ", ", ")
        parts = [p.strip(" .;:-") for p in chunk.split(",")]
        out = []
        for p in parts:
            p = _clean(p)
            if p:
                out.append(p)
        return out

    uses = []
    uses.extend(extract_uses(safe_seo_desc))
    uses.extend(extract_uses(safe_pd))

    sizes = _extract_sizes(product)
    size = _option2_value(variant)
    if size and size.lower() not in {s.lower() for s in sizes}:
        sizes = [size] + sizes

    # Keywords sources
    kw1 = _split_keywords(mfp.get("chem.keywords"))
    kw2 = _split_keywords(mfp.get("shopify--discovery--product_search_boost.queries"))
    kw3 = _split_keywords(product.get("tags"))
    raw_keywords = [*kw1, *kw2, *kw3]
    safe_keywords, blocked_keywords = filter_keywords(
        raw_keywords, allow_grade_terms_from_product_name=raw_title
    )

    chemical_name = _clean(mfp.get("product_details.chemical_name")) or _derive_chemical_name_from_title(raw_title)

    facts: dict[str, Any] = {
        "sku": fetch.sku,
        "asin": None,
        # Grade gating uses Shopify product title; we pass the sanitized title for generation
        # but keep raw title in the report.
        "product_name": safe_title or raw_title or fetch.sku,
        "brand": brand,
        "chemical_identity": {
            "chemical_name": chemical_name or None,
            "iupac_name": None,
            "cas_number": cas or None,
            "other_names": [],
        },
        "specifications": {
            "purity": purity_val or None,
            "concentration": concentration_val or None,
            "grade": grade or None,
            "appearance": appearance or (form or None),
            "odor": None,
            "ph": None,
            "specific_gravity": sg or None,
            "boiling_point": bp or None,
            "flash_point": flash or None,
            "solubility": solubility or None,
        },
        "packaging": {
            "container_type": None,
            "sizes_available": sizes,
            "units_per_case": None,
            "shipping_weight": None,
            "dimensions": {k: v for k, v in dims.items() if v},
            "shipping_group": shipping_group or None,
            "dim_group": dim_group or None,
        },
        "applications": [*industries, *uses],
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
            "secondary": safe_keywords[:25],
            "application": [],
            "long_tail": [],
        },
        "sds_link": sds or None,
        "tds_link": None,
        "last_updated": None,
        "updated_by": "shopify_import",
        "product_details": {
            "formula": formula or None,
            "molecular_weight": mw or None,
            "melting_point": mp or None,
            "product_description": safe_pd or None,
            "seo_description": safe_seo_desc or None,
        },
    }

    missing: list[str] = []
    if not facts["product_name"]:
        missing.append("product_name")
    if not facts["chemical_identity"]["cas_number"]:
        missing.append("chemical_identity.cas_number")
    if not facts["specifications"]["purity"] and not facts["specifications"]["concentration"]:
        missing.append("specifications.purity_or_concentration")
    if not sizes:
        missing.append("packaging.sizes_available")

    report = {
        "shopify_raw_title": raw_title,
        "shopify_safe_title": facts["product_name"],
        "removed_from_title": removed_from_title,
        "blocked_keywords": blocked_keywords,
        "removed_from_descriptions": list({*removed_pd, *removed_seo_desc}),
        "missing_recommended_fields": missing,
        "size_from_option2": size,
        "sizes_available_from_option2": sizes,
        "metafields_seen": sorted(fetch.product_metafields.keys()),
    }
    return ShopifyFactsBuildResult(facts=facts, report=report)
