from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .client import ShopifyClient


_PRODUCT_METAFIELD_IDENTIFIERS = [
    ("chem", "keywords"),
    ("chem", "title_optimized"),
    ("custom", "safety_data_sheet"),
    ("custom", "specific_gravity"),
    ("custom", "seo_title"),
    ("filters", "industry"),
    ("filters", "form"),
    ("filters", "grade"),
    ("filters", "percentage"),
    ("global", "WIDTH"),
    ("global", "HEIGHT"),
    ("global", "LENGTH"),
    ("product_details", "molecular_weight"),
    ("product_details", "formula"),
    ("product_details", "cas_number"),
    ("product_details", "grade"),
    ("product_details", "flash_point"),
    ("product_details", "form"),
    ("product_details", "solubility"),
    ("product_details", "appearance"),
    ("product_details", "melting_point"),
    ("product_details", "boiling_point"),
    ("product_details", "seo_title"),
    ("product_details", "seo_description"),
    ("product_details", "product_description"),
    ("product_details", "product_description_html"),
    ("shipperhq", "shipperhq_shipping_group"),
    ("shipperhq", "shipperhq_dim_group"),
    ("shopify--discovery--product_search_boost", "queries"),
]


def _alias(ns: str, key: str) -> str:
    raw = f"mf__{ns}__{key}"
    return re.sub(r"[^A-Za-z0-9_]", "_", raw)


def _metafield_selections(identifiers: list[tuple[str, str]]) -> str:
    # Shopify GraphQL Admin API: metafield(namespace:, key:) returns a single Metafield.
    # We use aliases to fetch many specific metafields without pulling all.
    parts: list[str] = []
    for ns, k in identifiers:
        a = _alias(ns, k)
        parts.append(
            f'{a}: metafield(namespace: "{ns}", key: "{k}") {{ namespace key type value }}'
        )
    return "\n        ".join(parts)


@dataclass(frozen=True)
class ShopifySkuFetchResult:
    sku: str
    product: dict[str, Any]
    variant: dict[str, Any]
    product_metafields: dict[str, Any]
    variant_metafields: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sku": self.sku,
            "product": self.product,
            "variant": self.variant,
            "product_metafields": self.product_metafields,
            "variant_metafields": self.variant_metafields,
        }


def fetch_by_sku(*, client: ShopifyClient, sku: str) -> ShopifySkuFetchResult:
    sku = sku.strip()
    if not sku:
        raise ValueError("sku is required")

    query = f"""
query($q: String!) {{
  productVariants(first: 1, query: $q) {{
    edges {{
      node {{
        id
        sku
        selectedOptions {{ name value }}
        {_metafield_selections(_PRODUCT_METAFIELD_IDENTIFIERS)}
        product {{
          id
          title
          handle
          vendor
          tags
          description
          descriptionHtml
          {_metafield_selections(_PRODUCT_METAFIELD_IDENTIFIERS)}
          variants(first: 100) {{
            edges {{
              node {{
                sku
                selectedOptions {{ name value }}
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""
    raw = client.graphql(query=query, variables={"q": f"sku:{sku}"})
    data = raw.get("data", {})
    pv = (data.get("productVariants") or {}).get("edges") or []
    if not pv:
        raise ValueError(f"SKU not found in Shopify: {sku}")
    node = pv[0].get("node") or {}
    product = node.get("product") or {}

    def mf_to_map(aliased_container: Any) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if not isinstance(aliased_container, dict):
            return out
        for ns, k in _PRODUCT_METAFIELD_IDENTIFIERS:
            a = _alias(ns, k)
            m = aliased_container.get(a)
            if not isinstance(m, dict):
                continue
            v = m.get("value")
            out[f"{ns}.{k}"] = v
        return out

    return ShopifySkuFetchResult(
        sku=sku,
        product={
            k: product.get(k)
            for k in [
                "id",
                "title",
                "handle",
                "vendor",
                "tags",
                "description",
                "descriptionHtml",
                "variants",
            ]
        },
        variant={k: node.get(k) for k in ["id", "sku", "selectedOptions"]},
        product_metafields=mf_to_map(product),
        variant_metafields=mf_to_map(node),
    )


def parse_metafield_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    s = value.strip()
    if not s:
        return ""
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        try:
            return json.loads(s)
        except Exception:
            return s
    return s
