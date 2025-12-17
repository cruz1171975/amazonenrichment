from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ..compliance.scanner import ScanConfig, scan_listing_fields
from ..compliance.scanner import scan_text
from ..facts import validate_facts_card
from .amazon_fields import (
    BACKEND_SEARCH_TERMS_BYTE_LIMIT,
    BULLET_CHAR_LIMIT,
    DESCRIPTION_CHAR_LIMIT,
    TITLE_CHAR_LIMIT,
)


def _get(d: dict[str, Any], *keys: str) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def _clean(s: Any) -> str:
    if not isinstance(s, str):
        return ""
    return " ".join(s.strip().split())


def _join_nonempty(parts: Iterable[str], sep: str = " - ") -> str:
    out = [p for p in (_clean(x) for x in parts) if p]
    return sep.join(out)


def _truncate_chars(s: str, limit: int) -> str:
    s = s.strip()
    if len(s) <= limit:
        return s
    return s[: max(0, limit - 1)].rstrip() + "…"


def _truncate_utf8_bytes_space_separated(s: str, limit: int) -> str:
    tokens = [t for t in s.split() if t]
    out: list[str] = []
    for tok in tokens:
        candidate = (" ".join(out + [tok])).strip()
        if len(candidate.encode("utf-8")) <= limit:
            out.append(tok)
        else:
            break
    return " ".join(out).strip()


def _dedupe_keep_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        s = _clean(it)
        if not s:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out


def _format_cas(cas: str) -> str:
    cas = _clean(cas)
    if not cas:
        return ""
    return f"CAS {cas}"


def _pick_size(facts: dict[str, Any], preferred: str | None) -> str:
    sizes = _get(facts, "packaging", "sizes_available")
    sizes_list = [s for s in sizes if isinstance(s, str) and s.strip()] if isinstance(sizes, list) else []
    if preferred:
        pref = preferred.strip().lower()
        for s in sizes_list:
            if s.strip().lower() == pref:
                return s.strip()
        return preferred.strip()
    return sizes_list[0].strip() if sizes_list else ""


def _grade_allowed_from_product_name(product_name: str) -> set[str]:
    lower = product_name.lower()
    allowed = set()
    for g in (
        "laboratory grade",
        "technical grade",
        "food grade",
        "acs grade",
        "reagent grade",
        "pharmaceutical grade",
        "industrial grade",
        "usp grade",
        "fcc grade",
        "nf grade",
    ):
        if g in lower:
            allowed.add(g)
    return allowed


def _safe_grade(facts: dict[str, Any]) -> str:
    product_name = _clean(facts.get("product_name"))
    grade = _clean(_get(facts, "specifications", "grade"))
    if not grade:
        return ""
    if grade.lower() in _grade_allowed_from_product_name(product_name):
        return grade
    return ""


def _build_title(facts: dict[str, Any], size: str) -> str:
    brand = _clean(facts.get("brand")) or "Alliance Chemical"
    product_name = _clean(facts.get("product_name"))
    chemical_name = _clean(_get(facts, "chemical_identity", "chemical_name"))
    purity = _clean(_get(facts, "specifications", "purity"))
    concentration = _clean(_get(facts, "specifications", "concentration"))
    grade = _safe_grade(facts)

    def contains(haystack: str, needle: str) -> bool:
        return needle and haystack and needle.lower() in haystack.lower()

    spec_bits: list[str] = []
    if purity:
        if not contains(product_name, purity) and not contains(chemical_name, purity):
            spec_bits.append(purity)
    elif concentration:
        if not contains(product_name, concentration) and not contains(chemical_name, concentration):
            spec_bits.append(concentration)
    if grade:
        if not contains(product_name, grade) and not contains(chemical_name, grade):
            spec_bits.append(grade)

    base_name = product_name or chemical_name
    title = _join_nonempty(
        [
            brand,
            base_name,
            " ".join(spec_bits) if spec_bits else "",
            size,
        ],
        sep=" ",
    )
    return _truncate_chars(title, TITLE_CHAR_LIMIT)


def _build_bullets(facts: dict[str, Any], size: str) -> list[str]:
    chemical_name = _clean(_get(facts, "chemical_identity", "chemical_name"))
    cas = _clean(_get(facts, "chemical_identity", "cas_number"))
    purity = _clean(_get(facts, "specifications", "purity"))
    concentration = _clean(_get(facts, "specifications", "concentration"))
    appearance = _clean(_get(facts, "specifications", "appearance"))
    flash_point = _clean(_get(facts, "specifications", "flash_point"))
    boiling_point = _clean(_get(facts, "specifications", "boiling_point"))
    specific_gravity = _clean(_get(facts, "specifications", "specific_gravity"))
    solubility = _clean(_get(facts, "specifications", "solubility"))
    product_details = _get(facts, "product_details") if isinstance(_get(facts, "product_details"), dict) else {}
    formula = _clean(product_details.get("formula") if isinstance(product_details, dict) else "")
    molecular_weight = _clean(product_details.get("molecular_weight") if isinstance(product_details, dict) else "")
    melting_point = _clean(product_details.get("melting_point") if isinstance(product_details, dict) else "")
    container = _clean(_get(facts, "packaging", "container_type"))
    dims = _get(facts, "packaging", "dimensions") if isinstance(_get(facts, "packaging", "dimensions"), dict) else {}
    length_in = _clean(dims.get("length_in") if isinstance(dims, dict) else "")
    width_in = _clean(dims.get("width_in") if isinstance(dims, dict) else "")
    height_in = _clean(dims.get("height_in") if isinstance(dims, dict) else "")
    applications = _dedupe_keep_order(_get(facts, "applications") or [])
    marketing = _dedupe_keep_order(_get(facts, "approved_marketing_claims") or [])
    safety = _get(facts, "safety_summary") if isinstance(_get(facts, "safety_summary"), dict) else {}
    signal_word = _clean(safety.get("signal_word") if isinstance(safety, dict) else "")
    hazards = _dedupe_keep_order(safety.get("primary_hazards") if isinstance(safety, dict) else [])
    ppe = _dedupe_keep_order(safety.get("ppe_required") if isinstance(safety, dict) else [])
    sds_link = _clean(facts.get("sds_link"))

    bullet1_bits: list[str] = []
    if chemical_name:
        bullet1_bits.append(chemical_name)
    if purity:
        bullet1_bits.append(purity)
    elif concentration:
        bullet1_bits.append(concentration)
    if cas:
        bullet1_bits.append(_format_cas(cas))
    if formula:
        bullet1_bits.append(f"Formula: {formula}")
    if molecular_weight:
        bullet1_bits.append(f"Molecular weight: {molecular_weight}")
    if appearance:
        bullet1_bits.append(f"Appearance: {appearance}")
    b1 = _join_nonempty(bullet1_bits, sep=" • ")

    b2 = ""
    if applications:
        b2 = "Applications: " + "; ".join(applications[:6])

    b3 = ""
    sds_bullet_used = False
    if marketing:
        b3 = "Features: " + "; ".join(marketing[:4])
    elif sds_link:
        b3 = "Documentation: SDS available"
        sds_bullet_used = True

    b4_bits: list[str] = []
    if size:
        b4_bits.append(f"Size: {size}")
    if container:
        b4_bits.append(f"Container: {container}")
    if length_in or width_in or height_in:
        dim_parts = []
        if length_in:
            dim_parts.append(f"L {length_in} in")
        if width_in:
            dim_parts.append(f"W {width_in} in")
        if height_in:
            dim_parts.append(f"H {height_in} in")
        if dim_parts:
            b4_bits.append("Dimensions: " + " × ".join(dim_parts))
    b4 = _join_nonempty(b4_bits, sep=" • ")

    b5_bits: list[str] = []
    if signal_word:
        b5_bits.append(f"Safety: {signal_word}")
    spec_bits: list[str] = []
    if flash_point:
        spec_bits.append(f"Flash point: {flash_point}")
    if boiling_point:
        spec_bits.append(f"Boiling point: {boiling_point}")
    if melting_point:
        spec_bits.append(f"Melting point: {melting_point}")
    if specific_gravity:
        spec_bits.append(f"Specific gravity: {specific_gravity}")
    if solubility:
        spec_bits.append(f"Solubility: {solubility}")
    if spec_bits:
        b5_bits.append("Specs: " + "; ".join(spec_bits[:5]))
    if hazards:
        b5_bits.append("Hazards: " + "; ".join(hazards[:4]))
    if ppe:
        b5_bits.append("PPE: " + "; ".join(ppe[:4]))
    if sds_link and not sds_bullet_used:
        b5_bits.append("SDS available")
    b5 = _join_nonempty(b5_bits, sep=" • ")

    bullets = [b for b in [b1, b2, b3, b4, b5] if b]
    # Ensure 5 bullets when possible using purely factual fallbacks.
    if len(bullets) < 5:
        sku = _clean(facts.get("sku"))
        brand = _clean(facts.get("brand"))
        for extra in [f"Brand: {brand}" if brand else "", f"SKU: {sku}" if sku else ""]:
            if extra and extra not in bullets:
                bullets.append(extra)
            if len(bullets) >= 5:
                break
    bullets = bullets[:5]
    return [_truncate_chars(b, BULLET_CHAR_LIMIT) for b in bullets]


def _build_description(facts: dict[str, Any], size: str, *, html: bool) -> str:
    product_name = _clean(facts.get("product_name"))
    chemical_name = _clean(_get(facts, "chemical_identity", "chemical_name"))
    cas = _clean(_get(facts, "chemical_identity", "cas_number"))
    specs = _get(facts, "specifications") if isinstance(_get(facts, "specifications"), dict) else {}
    purity = _clean(specs.get("purity") if isinstance(specs, dict) else "")
    concentration = _clean(specs.get("concentration") if isinstance(specs, dict) else "")
    grade = _safe_grade(facts)
    appearance = _clean(specs.get("appearance") if isinstance(specs, dict) else "")
    flash_point = _clean(specs.get("flash_point") if isinstance(specs, dict) else "")
    boiling_point = _clean(specs.get("boiling_point") if isinstance(specs, dict) else "")
    specific_gravity = _clean(specs.get("specific_gravity") if isinstance(specs, dict) else "")
    solubility = _clean(specs.get("solubility") if isinstance(specs, dict) else "")
    product_details = _get(facts, "product_details") if isinstance(_get(facts, "product_details"), dict) else {}
    formula = _clean(product_details.get("formula") if isinstance(product_details, dict) else "")
    molecular_weight = _clean(product_details.get("molecular_weight") if isinstance(product_details, dict) else "")
    melting_point = _clean(product_details.get("melting_point") if isinstance(product_details, dict) else "")
    applications = _dedupe_keep_order(_get(facts, "applications") or [])
    storage = _get(facts, "storage") if isinstance(_get(facts, "storage"), dict) else {}
    conditions = _clean(storage.get("conditions") if isinstance(storage, dict) else "")
    temp = _clean(storage.get("temperature") if isinstance(storage, dict) else "")
    special = _clean(storage.get("special_requirements") if isinstance(storage, dict) else "")
    safety = _get(facts, "safety_summary") if isinstance(_get(facts, "safety_summary"), dict) else {}
    ppe = _dedupe_keep_order(safety.get("ppe_required") if isinstance(safety, dict) else [])
    sds_link = _clean(facts.get("sds_link"))

    name_line = product_name or chemical_name or "Chemical product"
    identity_line = _join_nonempty(
        [chemical_name, _format_cas(cas) if cas else ""], sep=" • "
    )
    grade_line = grade
    strength_line = purity or concentration

    spec_rows: list[str] = []
    if formula:
        spec_rows.append(f"Formula: {formula}")
    if molecular_weight:
        spec_rows.append(f"Molecular weight: {molecular_weight}")
    if appearance:
        spec_rows.append(f"Appearance: {appearance}")
    if solubility:
        spec_rows.append(f"Solubility: {solubility}")
    if specific_gravity:
        spec_rows.append(f"Specific gravity: {specific_gravity}")
    if flash_point:
        spec_rows.append(f"Flash point: {flash_point}")
    if boiling_point:
        spec_rows.append(f"Boiling point: {boiling_point}")
    if melting_point:
        spec_rows.append(f"Melting point: {melting_point}")

    apps_line = ""
    if applications:
        apps_line = "Common applications: " + ", ".join(applications[:10]) + "."

    storage_lines = [x for x in [conditions, temp, special] if x]
    storage_line = "Storage: " + " ".join(storage_lines) if storage_lines else ""

    sds_line = "Documentation: SDS available." if sds_link else ""
    ppe_line = (
        "Safety: Use appropriate PPE and follow the SDS and label directions."
        if not ppe
        else "Safety: Use appropriate PPE such as "
        + ", ".join(ppe[:8])
        + ", and follow the SDS and label directions."
    )

    if html:
        parts = [f"<p><b>{name_line}</b></p>"]
        if identity_line:
            parts.append(f"<p>{identity_line}</p>")
        if strength_line or grade_line or size:
            parts.append(
                "<p>"
                + _join_nonempty(
                    [
                        f"Strength: {strength_line}" if strength_line else "",
                        f"Grade: {grade_line}" if grade_line else "",
                        f"Size: {size}" if size else "",
                    ],
                    sep=" • ",
                )
                + "</p>"
            )
        if spec_rows:
            parts.append("<p><b>Specifications</b></p>")
            parts.append("<ul>" + "".join([f"<li>{r}</li>" for r in spec_rows[:10]]) + "</ul>")
        if apps_line:
            parts.append(f"<p>{apps_line}</p>")
        if storage_line:
            parts.append(f"<p>{storage_line}</p>")
        if sds_line:
            parts.append(f"<p>{sds_line}</p>")
        parts.append(f"<p>{ppe_line}</p>")
        desc = "\n".join([p for p in parts if p and p != "<p></p>"])
    else:
        parts: list[str] = []
        parts.append(name_line)
        if identity_line:
            parts.append(identity_line)
        overview_bits = _join_nonempty(
            [
                f"Strength: {strength_line}" if strength_line else "",
                f"Grade: {grade_line}" if grade_line else "",
                f"Size: {size}" if size else "",
            ],
            sep=" • ",
        )
        if overview_bits:
            parts.append(overview_bits)
        if spec_rows:
            parts.append("Specifications:\n- " + "\n- ".join(spec_rows[:10]))
        if apps_line:
            parts.append(apps_line)
        if storage_line:
            parts.append(storage_line)
        if sds_line:
            parts.append(sds_line)
        parts.append(ppe_line)
        desc = "\n\n".join([p for p in parts if p])

    return _truncate_chars(desc, DESCRIPTION_CHAR_LIMIT)


def _build_backend_search_terms(facts: dict[str, Any], *, product_name: str) -> str:
    keywords = _get(facts, "keywords") if isinstance(_get(facts, "keywords"), dict) else {}
    primary = keywords.get("primary") if isinstance(keywords, dict) else []
    secondary = keywords.get("secondary") if isinstance(keywords, dict) else []
    application = keywords.get("application") if isinstance(keywords, dict) else []
    long_tail = keywords.get("long_tail") if isinstance(keywords, dict) else []
    tokens = _dedupe_keep_order([*primary, *secondary, *application, *long_tail])
    config = ScanConfig(allow_grade_terms_from_product_name=product_name)
    safe_tokens: list[str] = []
    for t in tokens:
        token_findings = scan_text(t, config=config, field="backend_token")
        if any(f.severity == "hard" for f in token_findings):
            continue
        safe_tokens.append(t)
    safe = " ".join(safe_tokens)
    return _truncate_utf8_bytes_space_separated(safe, BACKEND_SEARCH_TERMS_BYTE_LIMIT)


@dataclass(frozen=True)
class GenerationOptions:
    size: str | None = None
    html_description: bool = False
    include_debug: bool = False


def generate_listing(facts: dict[str, Any], *, options: GenerationOptions) -> dict[str, Any]:
    facts_issues = validate_facts_card(facts)
    errors = [i for i in facts_issues if i.severity == "error"]
    if errors:
        raise ValueError(
            "Facts card failed validation:\n" + "\n".join(f"{e.path}: {e.message}" for e in errors)
        )

    size = _pick_size(facts, options.size)
    title = _build_title(facts, size)
    bullets = _build_bullets(facts, size)
    description = _build_description(facts, size, html=options.html_description)
    product_name = _clean(facts.get("product_name"))
    backend = _build_backend_search_terms(facts, product_name=product_name)

    a_plus_markdown = _build_a_plus_markdown(facts)
    a_plus = _build_a_plus_structure(facts)

    listing = {
        "title": title,
        "bullets": bullets,
        "description": description,
        "backend_search_terms": backend,
        "a_plus_markdown": a_plus_markdown,
        "a_plus": a_plus,
        "metadata": {
            "sku": _clean(facts.get("sku")),
            "asin": facts.get("asin"),
            "product_name": product_name,
            "size": size,
            "generator": "alliance_amazon",
        },
    }

    findings = scan_listing_fields(
        listing, config=ScanConfig(allow_grade_terms_from_product_name=product_name)
    )
    listing["compliance_findings"] = [f.to_dict() for f in findings]
    listing["compliance_status"] = "fail" if any(f.severity == "hard" for f in findings) else "pass"
    if options.include_debug:
        listing["debug"] = {"facts_issues": [i.to_dict() for i in facts_issues], "facts": facts}
    return listing


def _build_a_plus_markdown(facts: dict[str, Any]) -> str:
    product_name = _clean(facts.get("product_name"))
    chemical_name = _clean(_get(facts, "chemical_identity", "chemical_name"))
    cas = _clean(_get(facts, "chemical_identity", "cas_number"))
    applications = _dedupe_keep_order(_get(facts, "applications") or [])
    marketing = _dedupe_keep_order(_get(facts, "approved_marketing_claims") or [])
    safety = _get(facts, "safety_summary") if isinstance(_get(facts, "safety_summary"), dict) else {}
    hazards = _dedupe_keep_order(safety.get("primary_hazards") if isinstance(safety, dict) else [])
    ppe = _dedupe_keep_order(safety.get("ppe_required") if isinstance(safety, dict) else [])

    headline = product_name or chemical_name or "Alliance Chemical"
    sub = _join_nonempty([chemical_name, _format_cas(cas) if cas else ""], sep=" • ")

    lines: list[str] = []
    lines.append(f"# A+ Draft: {headline}")
    if sub:
        lines.append(sub)
    lines.append("")
    if marketing:
        lines.append("## Key Features")
        for m in marketing[:6]:
            lines.append(f"- {m}")
        lines.append("")
    if applications:
        lines.append("## Common Applications")
        lines.append(", ".join(applications[:10]) + ".")
        lines.append("")
    lines.append("## Safety & Handling")
    if hazards:
        lines.append("Hazards: " + "; ".join(hazards[:6]) + ".")
    if ppe:
        lines.append("Use appropriate PPE such as " + ", ".join(ppe[:8]) + ".")
    lines.append("Always follow the SDS and label directions.")
    lines.append("")
    lines.append("## Images Needed (Suggestions)")
    lines.append("- Front label / hero image")
    lines.append("- Spec callouts (purity/concentration/CAS if applicable)")
    lines.append("- Application collage (uses without regulated efficacy claims)")
    lines.append("- Safety callout (PPE / storage iconography)")
    return "\n".join(lines).strip()


def _build_a_plus_structure(facts: dict[str, Any]) -> dict[str, Any]:
    product_name = _clean(facts.get("product_name"))
    marketing = _dedupe_keep_order(_get(facts, "approved_marketing_claims") or [])
    applications = _dedupe_keep_order(_get(facts, "applications") or [])
    return {
        "version": 1,
        "modules": [
            {
                "type": "hero",
                "headline": product_name,
                "subheadline": "Facts-based product information (draft)",
            },
            {
                "type": "features",
                "items": marketing[:6],
            },
            {
                "type": "applications",
                "items": applications[:10],
            },
            {
                "type": "safety",
                "note": "Always follow the SDS and label directions. Use appropriate PPE.",
            },
        ],
    }
