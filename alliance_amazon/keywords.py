from __future__ import annotations

from typing import Any

from .compliance.scanner import ScanConfig, scan_text


def suggest_keywords(facts: dict[str, Any]) -> dict[str, list[str]]:
    def clean(s: Any) -> str:
        if not isinstance(s, str):
            return ""
        return " ".join(s.strip().split())

    def as_list(v: Any) -> list[str]:
        if not isinstance(v, list):
            return []
        out: list[str] = []
        for item in v:
            s = clean(item)
            if s:
                out.append(s)
        return out

    product_name = clean(facts.get("product_name"))
    chemical = facts.get("chemical_identity") if isinstance(facts.get("chemical_identity"), dict) else {}
    chemical_name = clean(chemical.get("chemical_name") if isinstance(chemical, dict) else "")
    other_names = as_list(chemical.get("other_names") if isinstance(chemical, dict) else [])
    cas = clean(chemical.get("cas_number") if isinstance(chemical, dict) else "")

    keywords = facts.get("keywords") if isinstance(facts.get("keywords"), dict) else {}
    primary = as_list(keywords.get("primary") if isinstance(keywords, dict) else [])
    secondary = as_list(keywords.get("secondary") if isinstance(keywords, dict) else [])
    application = as_list(keywords.get("application") if isinstance(keywords, dict) else [])
    long_tail = as_list(keywords.get("long_tail") if isinstance(keywords, dict) else [])

    if not primary:
        if chemical_name:
            primary.append(chemical_name)
    secondary.extend(other_names)
    if cas:
        secondary.append(cas)

    # Very lightweight derivation from product_name (minus brand).
    if product_name:
        secondary.append(product_name)

    apps = as_list(facts.get("applications"))
    application.extend(apps)

    # De-dupe while keeping order.
    def dedupe(items: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for it in items:
            key = it.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
        return out

    return {
        "primary": dedupe(primary),
        "secondary": dedupe(secondary),
        "application": dedupe(application),
        "long_tail": dedupe(long_tail),
    }


def filter_keywords(
    keywords: list[str], *, allow_grade_terms_from_product_name: str | None
) -> tuple[list[str], list[str]]:
    config = ScanConfig(allow_grade_terms_from_product_name=allow_grade_terms_from_product_name)
    safe: list[str] = []
    blocked: list[str] = []
    for k in keywords:
        s = " ".join(str(k).split()).strip()
        if not s:
            continue
        findings = scan_text(s, config=config, field="keyword")
        if any(f.severity == "hard" for f in findings):
            blocked.append(s)
        else:
            safe.append(s)
    return safe, blocked

