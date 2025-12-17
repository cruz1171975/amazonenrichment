from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ..compliance.scanner import ScanConfig, scan_listing_fields
from ..listing.generator import GenerationOptions, generate_listing
from .template import AmazonTemplateSheet


def _clean(s: Any) -> str:
    if not isinstance(s, str):
        return ""
    return " ".join(s.strip().split())


def _chunk_terms_to_n_fields(terms: str, *, n: int, max_bytes_each: int) -> list[str]:
    tokens = [t for t in terms.split() if t]
    fields: list[str] = []
    i = 0
    for _ in range(n):
        cur: list[str] = []
        while i < len(tokens):
            candidate = " ".join(cur + [tokens[i]])
            if len(candidate.encode("utf-8")) <= max_bytes_each:
                cur.append(tokens[i])
                i += 1
            else:
                break
        fields.append(" ".join(cur))
    return fields


def _find_first_header(attribute_keys: list[str], prefix: str) -> str | None:
    for k in attribute_keys:
        if k.startswith(prefix):
            return k
    return None


def _find_all_headers(attribute_keys: list[str], prefix: str) -> list[str]:
    return [k for k in attribute_keys if k.startswith(prefix)]


@dataclass(frozen=True)
class FlatFileOptions:
    product_type: str = "LAB_CHEMICAL"
    marketplace_id: str = "ATVPDKIKX0DER"
    record_action: str = "full_update"
    sheet_name: str = "Template"
    output_format: str = "tsv"  # "tsv" | "csv"
    allow_noncompliant: bool = False
    generic_keyword_fields: int = 5
    generic_keyword_max_bytes_each: int = 50


def generate_flat_file_rows(
    *,
    template_xlsm: Path,
    facts: dict[str, Any],
    listing_options: GenerationOptions,
    flatfile_options: FlatFileOptions,
) -> tuple[list[str], list[str]]:
    template = AmazonTemplateSheet(xlsm_path=template_xlsm, sheet_name=flatfile_options.sheet_name)
    _, attribute_keys = template.read_headers()
    headers = [h for h in attribute_keys if h]
    if not headers:
        raise ValueError("No attribute keys found in template header row")

    listing = generate_listing(facts, options=listing_options)
    config = ScanConfig(allow_grade_terms_from_product_name=_clean(facts.get("product_name")))
    findings = scan_listing_fields(listing, config=config)
    if any(f.severity == "hard" for f in findings) and not flatfile_options.allow_noncompliant:
        raise ValueError("Listing failed compliance scan; re-run with allow_noncompliant to export anyway.")

    row: dict[str, str] = {h: "" for h in headers}

    sku_key = _find_first_header(headers, "contribution_sku#")
    if sku_key:
        row[sku_key] = _clean(facts.get("sku"))
    if "::record_action" in row:
        row["::record_action"] = flatfile_options.record_action
    pt_key = _find_first_header(headers, "product_type#")
    if pt_key:
        row[pt_key] = flatfile_options.product_type

    item_name_key = _find_first_header(
        headers, f"item_name[marketplace_id={flatfile_options.marketplace_id}]"
    )
    if item_name_key:
        row[item_name_key] = _clean(listing.get("title"))

    brand_key = _find_first_header(
        headers, f"brand[marketplace_id={flatfile_options.marketplace_id}]"
    )
    if brand_key:
        row[brand_key] = _clean(facts.get("brand")) or "Alliance Chemical"

    desc_key = _find_first_header(
        headers, f"product_description[marketplace_id={flatfile_options.marketplace_id}]"
    )
    if desc_key:
        row[desc_key] = _clean(listing.get("description"))

    bullet_keys = _find_all_headers(
        headers, f"bullet_point[marketplace_id={flatfile_options.marketplace_id}]"
    )
    bullets = listing.get("bullets") or []
    for k, bullet in zip(bullet_keys, bullets):
        row[k] = _clean(bullet)

    gk_keys = _find_all_headers(
        headers, f"generic_keyword[marketplace_id={flatfile_options.marketplace_id}]"
    )[: flatfile_options.generic_keyword_fields]
    backend = _clean(listing.get("backend_search_terms"))
    if gk_keys and backend:
        chunks = _chunk_terms_to_n_fields(
            backend,
            n=len(gk_keys),
            max_bytes_each=flatfile_options.generic_keyword_max_bytes_each,
        )
        for k, chunk in zip(gk_keys, chunks):
            row[k] = chunk

    size_key = _find_first_header(headers, f"size[marketplace_id={flatfile_options.marketplace_id}]")
    if size_key:
        row[size_key] = _clean(listing.get("metadata", {}).get("size")) or ""

    signal_key = _find_first_header(
        headers, f"hazard_classification_safety_signal_word[marketplace_id={flatfile_options.marketplace_id}]"
    )
    if signal_key:
        safety = facts.get("safety_summary") if isinstance(facts.get("safety_summary"), dict) else {}
        row[signal_key] = _clean(safety.get("signal_word") if isinstance(safety, dict) else "")

    data_row = [row.get(h, "") for h in headers]
    return headers, data_row


def write_flat_file(
    *,
    out_path: Path,
    headers: list[str],
    rows: Iterable[list[str]],
    output_format: str,
) -> None:
    delimiter = "\t" if output_format == "tsv" else ","
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        w.writerow(headers)
        for r in rows:
            w.writerow(r)
