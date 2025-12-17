from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

from .blocklist import BlockedTerm, iter_blocked_terms


_GRADE_TERMS = [
    "laboratory grade",
    "lab grade",
    "technical grade",
    "food grade",
    "acs grade",
    "reagent grade",
    "pharmaceutical grade",
    "industrial grade",
    "usp grade",
    "fcc grade",
    "nf grade",
]


def _term_to_regex(term: str) -> re.Pattern[str]:
    t = term.strip()
    if not t:
        return re.compile(r"$^")

    escaped = re.escape(t)
    # Treat spaces as space-or-hyphen runs to catch variants like "technical-grade".
    escaped = escaped.replace(r"\ ", r"[-\s]+")
    escaped = escaped.replace(r"\-", r"[-\s]*")

    starts_alnum = t[:1].isalnum()
    ends_alnum = t[-1:].isalnum()
    if starts_alnum:
        escaped = r"\b" + escaped
    if ends_alnum:
        escaped = escaped + r"\b"
    return re.compile(escaped, re.IGNORECASE)


@dataclass(frozen=True)
class ScanConfig:
    allow_grade_terms_from_product_name: str | None = None


@dataclass(frozen=True)
class Finding:
    severity: str  # "hard" | "soft"
    rule_id: str
    field: str
    message: str
    match: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "rule_id": self.rule_id,
            "field": self.field,
            "message": self.message,
            "match": self.match,
        }


_BLOCKLIST: list[tuple[BlockedTerm, re.Pattern[str]]] = [
    (t, _term_to_regex(t.term)) for t in iter_blocked_terms()
]

_PERCENT_ORGANISM = re.compile(
    r"(?i)\b\d{1,3}(?:\.\d+)?\s*%.*\b(germs?|bacteria|viruses?|mold|mildew|fungus|pathogens?)\b"
)

_MEDICAL_CLAIM = re.compile(
    r"(?i)\b(cures|treats|prevents|heals|healing|therapeutic|medicinal)\b"
    r"(?:\W+\w+){0,3}\W+"
    r"\b(disease|illness|infection|asthma|allerg(?:y|ies)|flu|cold|covid|pain|inflammation)\b"
)


def _allowed_grade_terms(product_name: str | None) -> set[str]:
    if not product_name:
        return set()
    lower = product_name.lower()
    return {g for g in _GRADE_TERMS if g in lower}


def scan_text(text: str, *, config: ScanConfig, field: str = "text") -> list[Finding]:
    findings: list[Finding] = []
    if not text:
        return findings

    for blocked, rx in _BLOCKLIST:
        m = rx.search(text)
        if not m:
            continue
        findings.append(
            Finding(
                severity=blocked.severity,
                rule_id=f"BLOCKLIST-{blocked.rule_id}",
                field=field,
                message=f"Blocked term in category '{blocked.category}'",
                match=m.group(0),
            )
        )

    m2 = _PERCENT_ORGANISM.search(text)
    if m2:
        findings.append(
            Finding(
                severity="hard",
                rule_id="PATTERN-PERCENT-ORGANISM",
                field=field,
                message="Percent/organism claim implies antimicrobial efficacy",
                match=m2.group(0),
            )
        )

    m3 = _MEDICAL_CLAIM.search(text)
    if m3:
        findings.append(
            Finding(
                severity="hard",
                rule_id="PATTERN-MEDICAL-CLAIM",
                field=field,
                message="Medical/drug claim language detected",
                match=m3.group(0),
            )
        )

    allowed_grades = _allowed_grade_terms(config.allow_grade_terms_from_product_name)
    if not allowed_grades:
        for g in _GRADE_TERMS:
            rxg = re.compile(r"\b" + re.escape(g) + r"\b", re.IGNORECASE)
            mg = rxg.search(text)
            if mg:
                findings.append(
                    Finding(
                        severity="hard",
                        rule_id="RULE-GRADE-UNVERIFIED",
                        field=field,
                        message="Grade term used but not allowed (no product_name provided or grade not present there)",
                        match=mg.group(0),
                    )
                )
                break
    else:
        for g in _GRADE_TERMS:
            rxg = re.compile(r"\b" + re.escape(g) + r"\b", re.IGNORECASE)
            mg = rxg.search(text)
            if mg and g not in allowed_grades:
                findings.append(
                    Finding(
                        severity="hard",
                        rule_id="RULE-GRADE-MISMATCH",
                        field=field,
                        message=f"Grade term not present in product_name (allowed: {sorted(allowed_grades)})",
                        match=mg.group(0),
                    )
                )
                break

    return findings


def scan_listing_fields(payload: Any, *, config: ScanConfig) -> list[Finding]:
    findings: list[Finding] = []
    if isinstance(payload, dict):
        for key in ("title", "description", "backend_search_terms", "a_plus_markdown"):
            if isinstance(payload.get(key), str):
                findings.extend(scan_text(payload[key], config=config, field=key))
        bullets = payload.get("bullets")
        if isinstance(bullets, list):
            for idx, b in enumerate(bullets, start=1):
                if isinstance(b, str):
                    findings.extend(scan_text(b, config=config, field=f"bullet_{idx}"))
        a_plus = payload.get("a_plus")
        if isinstance(a_plus, (dict, list)):
            findings.extend(_scan_payload_strings(a_plus, config=config, field_prefix="a_plus"))
    else:
        findings.extend(scan_text(str(payload), config=config, field="payload"))
    return findings


def _scan_payload_strings(payload: Any, *, config: ScanConfig, field_prefix: str) -> list[Finding]:
    findings: list[Finding] = []
    if isinstance(payload, str):
        return scan_text(payload, config=config, field=field_prefix)
    if isinstance(payload, list):
        for idx, item in enumerate(payload, start=1):
            findings.extend(_scan_payload_strings(item, config=config, field_prefix=f"{field_prefix}[{idx}]"))
        return findings
    if isinstance(payload, dict):
        for k, v in payload.items():
            findings.extend(_scan_payload_strings(v, config=config, field_prefix=f"{field_prefix}.{k}"))
    return findings
