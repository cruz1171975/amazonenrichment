from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class ShopifyClient:
    shop_domain: str
    access_token: str
    api_version: str = "2024-07"
    timeout_s: float = 60.0

    @staticmethod
    def from_env() -> "ShopifyClient":
        shop = os.environ.get("SHOPIFY_SHOP_DOMAIN", "").strip()
        token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip()
        version = os.environ.get("SHOPIFY_API_VERSION", "2024-07").strip()
        if not shop:
            raise RuntimeError("Missing SHOPIFY_SHOP_DOMAIN (e.g. alliance-chemical-store.myshopify.com)")
        if not token:
            raise RuntimeError("Missing SHOPIFY_ACCESS_TOKEN (Admin API access token)")
        return ShopifyClient(shop_domain=shop, access_token=token, api_version=version)

    def graphql(self, *, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"https://{self.shop_domain}/admin/api/{self.api_version}/graphql.json"
        payload = {"query": query, "variables": variables or {}}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": self.access_token,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
            raise RuntimeError(f"Shopify GraphQL HTTP error: {e.code}: {detail}") from e
        except Exception as e:
            raise RuntimeError(f"Shopify GraphQL request failed: {e}") from e

        if not isinstance(raw, dict):
            raise RuntimeError("Unexpected Shopify GraphQL response")
        if "errors" in raw and raw["errors"]:
            raise RuntimeError(f"Shopify GraphQL errors: {raw['errors']}")
        return raw

