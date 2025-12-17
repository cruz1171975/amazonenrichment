from __future__ import annotations

import json
from typing import Any


def build_listing_rewrite_prompt(
    *,
    facts: dict[str, Any],
    base_listing: dict[str, Any],
    forbidden_terms: list[str],
    hard_rules: list[str],
) -> str:
    """
    Prompt an LLM to rewrite copy while staying within strict compliance rules.

    Output MUST be JSON only (no markdown fences).
    """
    product_name = str(facts.get("product_name") or "").strip()
    allowed_grades = [t for t in ["Laboratory Grade", "Technical Grade", "Food Grade", "ACS Grade", "Reagent Grade", "Pharmaceutical Grade", "Industrial Grade", "USP Grade", "FCC Grade", "NF Grade"] if t.lower() in product_name.lower()]
    allowed_grades_line = ", ".join(allowed_grades) if allowed_grades else "(none)"

    return "\n".join(
        [
            "You are writing Amazon listing copy for a chemical product.",
            "You MUST follow these rules:",
            *[f"- {r}" for r in hard_rules],
            f"- Grade allowlist for this SKU (derived from facts.product_name): {allowed_grades_line}. If (none), do not output any grade wording or grade variants (e.g., lab-grade, reagent-grade, ACS, USP, food grade).",
            "",
            "Forbidden terms/phrases (do not output any of these, even indirectly):",
            *[f"- {t}" for t in forbidden_terms],
            "",
            "You may ONLY use claims that are present in the facts card or base listing.",
            "Do not add new certifications, grades, safety claims, medical claims, antimicrobial claims, or guarantees.",
            "Maintain a professional, technical tone. No hype, no superlatives.",
            "",
            "Return JSON ONLY with these keys:",
            '  "title" (<=200 chars), "bullets" (array of 1-5 strings, <=250 chars each),',
            '  "description" (<=2000 chars), "backend_keywords" (array of tokens / short phrases; 2-3 words max each),',
            '  "a_plus_markdown" (optional), "a_plus" (optional object),',
            '  "evidence" (object mapping each field to facts paths used).',
            "",
            "FACTS CARD JSON:",
            json.dumps(facts, ensure_ascii=False),
            "",
            "BASE LISTING JSON (safe starting point):",
            json.dumps(
                {
                    "title": base_listing.get("title"),
                    "bullets": base_listing.get("bullets"),
                    "description": base_listing.get("description"),
                    "backend_search_terms": base_listing.get("backend_search_terms"),
                    "a_plus_markdown": base_listing.get("a_plus_markdown"),
                    "a_plus": base_listing.get("a_plus"),
                },
                ensure_ascii=False,
            ),
            "",
            "Now rewrite for clarity and SEO while staying compliant and within limits.",
            "Return JSON only.",
        ]
    )
