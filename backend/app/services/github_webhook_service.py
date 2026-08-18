"""HMAC-SHA256 verification for GitHub webhook deliveries.

GitHub signs every webhook body with the App's webhook secret and sends it
as `X-Hub-Signature-256: sha256=<hexdigest>`. Constant-time comparison
avoids timing side-channels.
"""
from __future__ import annotations

import hashlib
import hmac
from typing import Optional


def verify_signature(payload: bytes, signature_header: Optional[str], secret: str) -> bool:
    if not secret or not signature_header:
        return False
    if not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
