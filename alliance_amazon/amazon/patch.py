from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _clean(s: Any) -> str:
    if not isinstance(s, str):
        return ""
    return " ".join(s.strip().split())


def _chunk_by_utf8_bytes(terms: str, *, max_chunks: int = 5, max_bytes_each: int = 50) -> list[str]:
    tokens = [t for t in terms.split() if t]
    chunks: list[str] = []
    i = 0
    for _ in range(max_chunks):
        cur: list[str] = []
        while i < len(tokens):
            candidate = " ".join(cur + [tokens[i]])
            if len(candidate.encode("utf-8")) <= max_bytes_each:
                cur.append(tokens[i])
                i += 1
            else:
                break
        chunks.append(" ".join(cur))
    # Trim empty tail
    while chunks and not chunks[-1]:
        chunks.pop()
    return chunks


@dataclass(frozen=True)
class PatchBuildOptions:
    marketplace_id: str = "ATVPDKIKX0DER"
    language_tag: str = "en_US"
    product_type: str | None = None


def build_listings_item_patch(
    *,
    listing: dict[str, Any],
    options: PatchBuildOptions,
) -> dict[str, Any]:
    """
    Build a SP-API Listings Items PATCH body (schema: Listings Item Patch).
    """
    title = _clean(listing.get("title"))
    bullets = listing.get("bullets") if isinstance(listing.get("bullets"), list) else []
    bullets = [_clean(b) for b in bullets if _clean(b)]
    description = _clean(listing.get("description"))
    backend = _clean(listing.get("backend_search_terms"))
    keywords = _chunk_by_utf8_bytes(backend, max_chunks=5, max_bytes_each=50) if backend else []

    mkt = options.marketplace_id
    lang = options.language_tag

    def v(value: str) -> list[dict[str, str]]:
        return [{"value": value, "marketplace_id": mkt, "language_tag": lang}]

    patches: list[dict[str, Any]] = []
    if title:
        patches.append({"op": "replace", "path": "/attributes/item_name", "value": v(title)})
    if bullets:
        patches.append({"op": "replace", "path": "/attributes/bullet_point", "value": v_list(bullets, mkt, lang)})
    if description:
        patches.append(
            {"op": "replace", "path": "/attributes/product_description", "value": v(description)}
        )
    if keywords:
        patches.append(
            {"op": "replace", "path": "/attributes/generic_keyword", "value": v_list(keywords, mkt, lang)}
        )

    body: dict[str, Any] = {"patches": patches}
    if options.product_type:
        body["productType"] = options.product_type
    return body


def v_list(values: list[str], marketplace_id: str, language_tag: str) -> list[dict[str, str]]:
    return [{"value": s, "marketplace_id": marketplace_id, "language_tag": language_tag} for s in values]

