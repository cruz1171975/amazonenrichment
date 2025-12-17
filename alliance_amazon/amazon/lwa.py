from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class LwaConfig:
    client_id: str
    client_secret: str
    refresh_token: str
    token_url: str = "https://api.amazon.com/auth/o2/token"
    timeout_s: float = 60.0

    @staticmethod
    def from_env() -> "LwaConfig":
        cid = os.environ.get("AMAZON_LWA_CLIENT_ID", "").strip()
        cs = os.environ.get("AMAZON_LWA_CLIENT_SECRET", "").strip()
        rt = os.environ.get("AMAZON_LWA_REFRESH_TOKEN", "").strip()
        if not cid or not cs or not rt:
            raise RuntimeError(
                "Missing LWA env vars: AMAZON_LWA_CLIENT_ID, AMAZON_LWA_CLIENT_SECRET, AMAZON_LWA_REFRESH_TOKEN"
            )
        return LwaConfig(client_id=cid, client_secret=cs, refresh_token=rt)


def get_lwa_access_token(cfg: LwaConfig) -> str:
    form = {
        "grant_type": "refresh_token",
        "refresh_token": cfg.refresh_token,
        "client_id": cfg.client_id,
        "client_secret": cfg.client_secret,
    }
    data = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(
        cfg.token_url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=cfg.timeout_s) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        raise RuntimeError(f"LWA token HTTP error: {e.code}: {detail}") from e
    except Exception as e:
        raise RuntimeError(f"LWA token request failed: {e}") from e
    token = raw.get("access_token") if isinstance(raw, dict) else None
    if not isinstance(token, str) or not token.strip():
        raise RuntimeError(f"Invalid LWA token response: {raw}")
    return token

