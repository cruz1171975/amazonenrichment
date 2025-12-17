from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote, urlparse


def _hash_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hmac(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _amz_date(now: datetime) -> tuple[str, str]:
    dt = now.astimezone(timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ"), dt.strftime("%Y%m%d")


def _canonical_query(params: dict[str, str]) -> str:
    items = []
    for k in sorted(params.keys()):
        v = params[k]
        items.append(f"{quote(k, safe='-_.~')}={quote(v, safe='-_.~')}")
    return "&".join(items)


def _canonical_headers(headers: dict[str, str]) -> tuple[str, str]:
    normalized = {k.lower().strip(): " ".join(v.strip().split()) for k, v in headers.items()}
    keys = sorted(normalized.keys())
    canon = "".join([f"{k}:{normalized[k]}\n" for k in keys])
    signed = ";".join(keys)
    return canon, signed


@dataclass(frozen=True)
class SigV4Credentials:
    access_key_id: str
    secret_access_key: str
    session_token: str | None = None


def sign_request(
    *,
    method: str,
    url: str,
    region: str,
    service: str,
    headers: dict[str, str],
    body: bytes,
    query_params: dict[str, str] | None = None,
    credentials: SigV4Credentials,
    now: datetime | None = None,
) -> dict[str, str]:
    """
    Returns headers including Authorization (+ x-amz-date, x-amz-security-token if needed).
    """
    now = now or datetime.now(timezone.utc)
    amz_date, date_stamp = _amz_date(now)
    parsed = urlparse(url)
    host = parsed.netloc
    uri = parsed.path or "/"

    qp = query_params or {}
    canonical_querystring = _canonical_query(qp)

    headers_to_sign = dict(headers)
    headers_to_sign["Host"] = host
    headers_to_sign["x-amz-date"] = amz_date
    payload_hash = _hash_sha256(body)
    headers_to_sign["x-amz-content-sha256"] = payload_hash
    if credentials.session_token:
        headers_to_sign["x-amz-security-token"] = credentials.session_token

    canonical_headers, signed_headers = _canonical_headers(headers_to_sign)
    canonical_request = "\n".join(
        [
            method.upper(),
            uri,
            canonical_querystring,
            canonical_headers,
            signed_headers,
            payload_hash,
        ]
    )

    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = "\n".join(
        [
            algorithm,
            amz_date,
            credential_scope,
            _hash_sha256(canonical_request.encode("utf-8")),
        ]
    )

    k_date = _hmac(("AWS4" + credentials.secret_access_key).encode("utf-8"), date_stamp)
    k_region = hmac.new(k_date, region.encode("utf-8"), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service.encode("utf-8"), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()
    signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    authorization_header = (
        f"{algorithm} "
        f"Credential={credentials.access_key_id}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )

    out = dict(headers_to_sign)
    out["Authorization"] = authorization_header
    return out

