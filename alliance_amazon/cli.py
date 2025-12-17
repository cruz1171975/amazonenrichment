from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .compliance.scanner import ScanConfig, scan_listing_fields, scan_text
from .facts import (
    FactsValidationError,
    facts_from_shopify_product_dump,
    load_facts_card,
    validate_facts_card,
)
from .llm.providers import make_llm_client
from .llm.runner import generate_listing_with_llm
from .keywords import filter_keywords, suggest_keywords
from .flatfile.generate import FlatFileOptions, generate_flat_file_rows, write_flat_file
from .flatfile.template import AmazonTemplateSheet
from .listing.generator import GenerationOptions, generate_listing
from .utils import json_dumps, load_json, write_text_atomic


def _add_common_io_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write output to a file (default: stdout).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting an existing --out file.",
    )


def _write_output(out_path: Path | None, force: bool, text: str) -> None:
    if out_path is None:
        try:
            sys.stdout.write(text)
            if not text.endswith("\n"):
                sys.stdout.write("\n")
        except BrokenPipeError:
            try:
                sys.stdout.close()
            finally:
                return
        return
    if out_path.exists() and not force:
        raise SystemExit(
            f"Refusing to overwrite existing file: {out_path} (use --force)"
        )
    write_text_atomic(out_path, text)


def _cmd_facts_init(args: argparse.Namespace) -> int:
    template: dict[str, Any] = {
        "sku": "AC-12345",
        "asin": None,
        "product_name": "Official Shopify Product Title",
        "brand": "Alliance Chemical",
        "chemical_identity": {
            "chemical_name": None,
            "iupac_name": None,
            "cas_number": None,
            "other_names": [],
        },
        "specifications": {
            "purity": None,
            "concentration": None,
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
            "shipping_weight": None,
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
            "secondary": [],
            "application": [],
            "long_tail": [],
        },
        "sds_link": None,
        "tds_link": None,
        "last_updated": None,
        "updated_by": None,
    }
    _write_output(args.out, args.force, json_dumps(template))
    return 0


def _cmd_facts_validate(args: argparse.Namespace) -> int:
    data = load_json(args.facts)
    issues = validate_facts_card(data)
    errors = [i for i in issues if i.severity == "error"]
    if args.format == "json":
        _write_output(args.out, args.force, json_dumps([i.to_dict() for i in issues]))
    else:
        for issue in issues:
            sys.stdout.write(f"{issue.severity.upper()}: {issue.path}: {issue.message}\n")
    return 2 if errors else 0


def _cmd_facts_from_shopify(args: argparse.Namespace) -> int:
    product_payload = load_json(args.product)
    metafields_payload = load_json(args.metafields) if args.metafields else None
    facts = facts_from_shopify_product_dump(
        product_payload=product_payload,
        metafields_payload=metafields_payload,
        sku=args.sku,
        brand=args.brand,
    )
    _write_output(args.out, args.force, json_dumps(facts))
    return 0


def _cmd_compliance_scan(args: argparse.Namespace) -> int:
    allow_name = args.allow_grade_terms_from_product_name
    if not allow_name and args.facts:
        try:
            allow_name = str(load_json(args.facts).get("product_name") or "").strip() or None
        except Exception:
            allow_name = None
    config = ScanConfig(
        allow_grade_terms_from_product_name=allow_name,
    )
    path = args.input
    if path.suffix.lower() == ".json":
        payload = load_json(path)
        findings = scan_listing_fields(payload, config=config)
    else:
        findings = scan_text(path.read_text(encoding="utf-8", errors="replace"), config=config)
    errors = [f for f in findings if f.severity == "hard"]
    if args.format == "json":
        _write_output(args.out, args.force, json_dumps([f.to_dict() for f in findings]))
    else:
        for f in findings:
            sys.stdout.write(
                f"{f.severity.upper()} [{f.rule_id}] {f.field}: {f.message} (match: {f.match!r})\n"
            )
    return 2 if errors else 0


def _cmd_listing_generate(args: argparse.Namespace) -> int:
    try:
        facts = load_facts_card(args.facts)
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"Failed to load facts card: {e}") from e
    except FactsValidationError as e:
        raise SystemExit(str(e)) from e

    options = GenerationOptions(
        size=args.size,
        html_description=args.html_description,
        include_debug=args.include_debug,
    )
    listing = generate_listing(facts, options=options)
    if args.llm_provider:
        client = make_llm_client(args.llm_provider)
        llm_result = generate_listing_with_llm(
            facts=facts,
            base_listing={
                "title": listing.get("title", ""),
                "bullets": listing.get("bullets", []),
                "description": listing.get("description", ""),
                "backend_search_terms": listing.get("backend_search_terms", ""),
                "a_plus_markdown": listing.get("a_plus_markdown", ""),
                "a_plus": listing.get("a_plus", {}),
            },
            client=client,
            model=args.llm_model,
            max_attempts=args.llm_max_attempts,
        )
        # Replace core fields with LLM output; keep metadata/debug shape consistent.
        listing["title"] = llm_result.listing.get("title", listing.get("title", ""))
        listing["bullets"] = llm_result.listing.get("bullets", listing.get("bullets", []))
        listing["description"] = llm_result.listing.get("description", listing.get("description", ""))
        listing["backend_search_terms"] = llm_result.listing.get(
            "backend_search_terms", listing.get("backend_search_terms", "")
        )
        if "a_plus_markdown" in llm_result.listing:
            listing["a_plus_markdown"] = llm_result.listing["a_plus_markdown"]
        if "a_plus" in llm_result.listing:
            listing["a_plus"] = llm_result.listing["a_plus"]
        listing["compliance_findings"] = llm_result.compliance_findings
        listing["compliance_status"] = llm_result.compliance_status
        listing.setdefault("metadata", {})
        listing["metadata"]["llm_provider"] = args.llm_provider
        listing["metadata"]["llm_model"] = args.llm_model
        listing["metadata"]["llm_used_fallback"] = llm_result.used_fallback
    _write_output(args.out, args.force, json_dumps(listing))
    return 0


def _cmd_listing_render(args: argparse.Namespace) -> int:
    listing = load_json(args.listing)
    title = str(listing.get("title") or "").strip()
    bullets = listing.get("bullets") or []
    description = str(listing.get("description") or "").strip()
    backend = str(listing.get("backend_search_terms") or "").strip()
    a_plus_md = str(listing.get("a_plus_markdown") or "").strip()
    lines: list[str] = []
    if title:
        lines.append("# Title")
        lines.append(title)
        lines.append("")
    if bullets:
        lines.append("# Bullets")
        for b in bullets:
            lines.append(f"- {str(b).strip()}")
        lines.append("")
    if description:
        lines.append("# Description")
        lines.append(description)
        lines.append("")
    if backend:
        lines.append("# Backend Search Terms")
        lines.append(backend)
        lines.append("")
    if a_plus_md:
        lines.append(a_plus_md)
        lines.append("")
    _write_output(args.out, args.force, "\n".join(lines).rstrip() + "\n")
    return 0


def _cmd_keywords_suggest(args: argparse.Namespace) -> int:
    facts = load_json(args.facts)
    product_name = str(facts.get("product_name") or "").strip() or None
    suggested = suggest_keywords(facts)
    # Filter hard-blocked keywords by default for safety.
    flat = [*suggested.get("primary", []), *suggested.get("secondary", []), *suggested.get("application", []), *suggested.get("long_tail", [])]
    safe, blocked = filter_keywords(flat, allow_grade_terms_from_product_name=product_name)
    out = {"suggested": suggested, "safe_flat": safe, "blocked_flat": blocked}
    _write_output(args.out, args.force, json_dumps(out))
    return 0


def _cmd_keywords_filter(args: argparse.Namespace) -> int:
    allow_name = args.allow_grade_terms_from_product_name
    if not allow_name and args.facts:
        allow_name = str(load_json(args.facts).get("product_name") or "").strip() or None

    raw: list[str]
    if args.keywords.suffix.lower() == ".json":
        payload = load_json(args.keywords)
        raw = payload if isinstance(payload, list) else []
        raw = [str(x) for x in raw]
    else:
        raw = [
            line.strip()
            for line in args.keywords.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip()
        ]

    safe, blocked = filter_keywords(raw, allow_grade_terms_from_product_name=allow_name)
    out = {"safe": safe, "blocked": blocked}
    _write_output(args.out, args.force, json_dumps(out) if args.format == "json" else "\n".join(safe) + "\n")
    return 0 if not blocked else 2


def _cmd_flatfile_describe(args: argparse.Namespace) -> int:
    template = AmazonTemplateSheet(xlsm_path=args.xlsm, sheet_name=args.sheet)
    local_labels, keys = template.read_headers()
    cols = [(i + 1, local_labels[i], keys[i]) for i in range(len(keys)) if keys[i]]
    out = {
        "xlsm": str(args.xlsm),
        "sheet": args.sheet,
        "columns_with_keys": len(cols),
        "examples": [
            {"col": c, "label": lbl, "key": key}
            for (c, lbl, key) in cols[: min(25, len(cols))]
        ],
    }
    _write_output(args.out, args.force, json_dumps(out) if args.format == "json" else "\n".join(
        [f"{c}\t{lbl}\t{key}" for (c, lbl, key) in cols]
    ))
    return 0


def _cmd_flatfile_generate(args: argparse.Namespace) -> int:
    facts = load_facts_card(args.facts)
    listing_options = GenerationOptions(size=args.size, html_description=False, include_debug=False)
    flat_opts = FlatFileOptions(
        product_type=args.product_type,
        marketplace_id=args.marketplace_id,
        record_action=args.record_action,
        sheet_name=args.sheet,
        output_format=args.format,
        allow_noncompliant=args.allow_noncompliant,
        generic_keyword_max_bytes_each=args.generic_keyword_max_bytes_each,
    )
    headers, row = generate_flat_file_rows(
        template_xlsm=args.xlsm,
        facts=facts,
        listing_options=listing_options,
        flatfile_options=flat_opts,
    )
    if args.out is None:
        # Stream to stdout
        import io, csv

        delimiter = "\t" if args.format == "tsv" else ","
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        w.writerow(headers)
        w.writerow(row)
        _write_output(None, False, buf.getvalue().rstrip("\n"))
        return 0

    if args.out.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing file: {args.out} (use --force)")
    write_flat_file(out_path=args.out, headers=headers, rows=[row], output_format=args.format)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alliance-amazon",
        description="Alliance Chemical Amazon listing generator + compliance scanner (read-only by default).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    facts = sub.add_parser("facts", help="Facts card helpers")
    facts_sub = facts.add_subparsers(dest="facts_cmd", required=True)

    facts_init = facts_sub.add_parser("init", help="Print a facts card JSON template")
    _add_common_io_args(facts_init)
    facts_init.set_defaults(func=_cmd_facts_init)

    facts_validate = facts_sub.add_parser("validate", help="Validate a facts card JSON file")
    facts_validate.add_argument("facts", type=Path, help="Path to facts card JSON")
    facts_validate.add_argument("--format", choices=["text", "json"], default="text")
    _add_common_io_args(facts_validate)
    facts_validate.set_defaults(func=_cmd_facts_validate)

    facts_from_shopify = facts_sub.add_parser(
        "from-shopify", help="Create a facts card from a Shopify product JSON dump"
    )
    facts_from_shopify.add_argument(
        "--product",
        type=Path,
        required=True,
        help="Shopify product JSON file (GET /products/{id}.json output)",
    )
    facts_from_shopify.add_argument(
        "--metafields",
        type=Path,
        default=None,
        help="Optional Shopify metafields JSON file (GET /products/{id}/metafields.json output)",
    )
    facts_from_shopify.add_argument("--sku", type=str, required=True, help="Variant SKU to extract")
    facts_from_shopify.add_argument("--brand", type=str, default="Alliance Chemical")
    _add_common_io_args(facts_from_shopify)
    facts_from_shopify.set_defaults(func=_cmd_facts_from_shopify)

    compliance = sub.add_parser("compliance", help="Compliance scans")
    comp_sub = compliance.add_subparsers(dest="comp_cmd", required=True)

    comp_scan = comp_sub.add_parser("scan", help="Scan text or listing JSON for compliance risks")
    comp_scan.add_argument("input", type=Path, help="Text file or listing JSON to scan")
    comp_scan.add_argument("--format", choices=["text", "json"], default="text")
    comp_scan.add_argument(
        "--facts",
        type=Path,
        default=None,
        help="Optional facts card JSON to allow grade terms from its product_name.",
    )
    comp_scan.add_argument(
        "--allow-grade-terms-from-product-name",
        type=str,
        default=None,
        help="Optional product name used to allow grade terms found in that name.",
    )
    _add_common_io_args(comp_scan)
    comp_scan.set_defaults(func=_cmd_compliance_scan)

    listing = sub.add_parser("listing", help="Generate and render listing drafts")
    list_sub = listing.add_subparsers(dest="listing_cmd", required=True)

    list_gen = list_sub.add_parser("generate", help="Generate a listing JSON draft from a facts card")
    list_gen.add_argument("--facts", type=Path, required=True, help="Facts card JSON path")
    list_gen.add_argument("--size", type=str, default=None, help="Preferred size (e.g., '1 Gallon')")
    list_gen.add_argument(
        "--html-description",
        action="store_true",
        help="Generate an HTML description (otherwise plain text).",
    )
    list_gen.add_argument(
        "--include-debug",
        action="store_true",
        help="Include debug payload (facts + validation issues) in listing JSON.",
    )
    list_gen.add_argument(
        "--llm-provider",
        type=str,
        default=None,
        help="Optional LLM provider for copy rewrite (e.g., 'gemini').",
    )
    list_gen.add_argument(
        "--llm-model",
        type=str,
        default="gemini-3-flash-preview",
        help="LLM model name (default: gemini-3-flash-preview).",
    )
    list_gen.add_argument(
        "--llm-max-attempts",
        type=int,
        default=2,
        help="Max rewrite attempts before falling back to base copy.",
    )
    _add_common_io_args(list_gen)
    list_gen.set_defaults(func=_cmd_listing_generate)

    list_render = list_sub.add_parser("render", help="Render a listing JSON to Markdown-ish text")
    list_render.add_argument("--listing", type=Path, required=True, help="Listing JSON path")
    _add_common_io_args(list_render)
    list_render.set_defaults(func=_cmd_listing_render)

    keywords = sub.add_parser("keywords", help="Keyword helpers (suggest/filter)")
    kw_sub = keywords.add_subparsers(dest="kw_cmd", required=True)

    kw_suggest = kw_sub.add_parser("suggest", help="Suggest keywords from a facts card")
    kw_suggest.add_argument("--facts", type=Path, required=True, help="Facts card JSON path")
    _add_common_io_args(kw_suggest)
    kw_suggest.set_defaults(func=_cmd_keywords_suggest)

    kw_filter = kw_sub.add_parser("filter", help="Filter keywords through the compliance scanner")
    kw_filter.add_argument("keywords", type=Path, help="Text file (1 keyword/line) or JSON array")
    kw_filter.add_argument("--format", choices=["text", "json"], default="text")
    kw_filter.add_argument(
        "--facts",
        type=Path,
        default=None,
        help="Optional facts card JSON to allow grade terms from its product_name.",
    )
    kw_filter.add_argument(
        "--allow-grade-terms-from-product-name",
        type=str,
        default=None,
        help="Optional product name used to allow grade terms found in that name.",
    )
    _add_common_io_args(kw_filter)
    kw_filter.set_defaults(func=_cmd_keywords_filter)

    flatfile = sub.add_parser("flatfile", help="Amazon flat-file exports from a template .xlsm")
    ff_sub = flatfile.add_subparsers(dest="ff_cmd", required=True)

    ff_desc = ff_sub.add_parser("describe", help="Describe template header columns")
    ff_desc.add_argument("--xlsm", type=Path, required=True, help="Amazon category template .xlsm/.xlsx")
    ff_desc.add_argument("--sheet", type=str, default="Template", help="Sheet name (default: Template)")
    ff_desc.add_argument("--format", choices=["text", "json"], default="text")
    _add_common_io_args(ff_desc)
    ff_desc.set_defaults(func=_cmd_flatfile_describe)

    ff_gen = ff_sub.add_parser("generate", help="Generate a TSV/CSV row aligned to the template headers")
    ff_gen.add_argument("--xlsm", type=Path, required=True, help="Amazon category template .xlsm/.xlsx")
    ff_gen.add_argument("--sheet", type=str, default="Template", help="Sheet name (default: Template)")
    ff_gen.add_argument("--facts", type=Path, required=True, help="Facts card JSON path")
    ff_gen.add_argument("--size", type=str, default=None, help="Preferred size to use in listing/title fields")
    ff_gen.add_argument("--product-type", type=str, default="LAB_CHEMICAL")
    ff_gen.add_argument("--marketplace-id", type=str, default="ATVPDKIKX0DER")
    ff_gen.add_argument("--record-action", type=str, default="full_update")
    ff_gen.add_argument("--format", choices=["tsv", "csv"], default="tsv")
    ff_gen.add_argument("--allow-noncompliant", action="store_true", help="Export even if compliance scan fails")
    ff_gen.add_argument("--generic-keyword-max-bytes-each", type=int, default=50)
    _add_common_io_args(ff_gen)
    ff_gen.set_defaults(func=_cmd_flatfile_generate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
