from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AmazonConfig:
    seller_id: str
    marketplace_id: str = "ATVPDKIKX0DER"
    endpoint: str = "https://sellingpartnerapi-na.amazon.com"
    region: str = "us-east-1"

    @staticmethod
    def from_env() -> "AmazonConfig":
        seller_id = os.environ.get("AMAZON_SELLER_ID", "").strip()
        if not seller_id:
            raise RuntimeError("Missing AMAZON_SELLER_ID")
        marketplace_id = os.environ.get("AMAZON_MARKETPLACE_ID", "ATVPDKIKX0DER").strip()
        endpoint = os.environ.get("AMAZON_SP_API_ENDPOINT", "https://sellingpartnerapi-na.amazon.com").strip()
        region = os.environ.get("AMAZON_SP_API_REGION", "us-east-1").strip()
        return AmazonConfig(
            seller_id=seller_id,
            marketplace_id=marketplace_id,
            endpoint=endpoint,
            region=region,
        )

