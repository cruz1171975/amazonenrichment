from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from .config import AmazonConfig
from .lwa import LwaConfig, get_lwa_access_token
from .sigv4 import SigV4Credentials, sign_request


@dataclass
class SpApiClient:
    amazon: AmazonConfig
    lwa: LwaConfig
    aws: SigV4Credentials
    service: str = "execute-api"
    timeout_s: float = 60.0

    @staticmethod
    def from_env() -> "SpApiClient":
        amazon = AmazonConfig.from_env()
        lwa = LwaConfig.from_env()
        ak = os.environ.get("AWS_ACCESS_KEY_ID", "").strip()
        sk = os.environ.get("AWS_SECRET_ACCESS_KEY", "").strip()
        st = os.environ.get("AWS_SESSION_TOKEN", "").strip() or None
        if not ak or not sk:
            raise RuntimeError("Missing AWS env vars: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        return SpApiClient(amazon=amazon, lwa=lwa, aws=SigV4Credentials(ak, sk, st))

    def patch_listings_item(
        self,
        *,
        sku: str,
        marketplace_ids: list[str],
        patch_body: dict[str, Any],
        issue_locale: str = "en_US",
    ) -> dict[str, Any]:
        access_token = get_lwa_access_token(self.lwa)
        endpoint = self.amazon.endpoint.rstrip("/")
        path = f"/listings/2021-08-01/items/{self.amazon.seller_id}/{urllib.parse.quote(sku, safe='')}"
        url = endpoint + path

        query = {
            "marketplaceIds": ",".join(marketplace_ids),
            "issueLocale": issue_locale,
        }
        body = json.dumps(patch_body).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "x-amz-access-token": access_token,
        }
        signed = sign_request(
            method="PATCH",
            url=url,
            region=self.amazon.region,
            service=self.service,
            headers=headers,
            body=body,
            query_params=query,
            credentials=self.aws,
        )
        full_url = url + "?" + urllib.parse.urlencode(query)
        req = urllib.request.Request(full_url, data=body, headers=signed, method="PATCH")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
            raise RuntimeError(f"SP-API PATCH HTTP error: {e.code}: {detail}") from e

