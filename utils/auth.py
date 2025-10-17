# utils/auth.py
from __future__ import annotations

import os
import time
import hmac
import json
import base64
import hashlib
from typing import Optional, Dict, Any

from passlib.hash import pbkdf2_sha256

# ---------------------------------------------------------------------------
# Config (load from environment; never hard-code secrets)
# ---------------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGO = "HS256"
JWT_TTL_SEC = int(os.getenv("JWT_TTL_SEC", "86400"))  # 24h default
PASSWORD_PEPPER = os.getenv("PASSWORD_PEPPER", "")    # short server-side secret

# ---------------------------------------------------------------------------
# Password hashing (PBKDF2-SHA256; no 72-byte limit)
# ---------------------------------------------------------------------------
def _prehash(password: str) -> str:
    return f"{password}{PASSWORD_PEPPER}"

def hash_password(password: str) -> str:
    # You can tune cost via .using(rounds=...) later if needed.
    return pbkdf2_sha256.hash(_prehash(password))

def verify_password(password: str, password_hash: str) -> bool:
    return pbkdf2_sha256.verify(_prehash(password), password_hash)

# ---------------------------------------------------------------------------
# Minimal JWT (HS256)
# ---------------------------------------------------------------------------
def _b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

def _b64url_decode(s: str) -> bytes:
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s.encode())

def create_jwt(payload: Dict[str, Any], ttl: int = JWT_TTL_SEC) -> str:
    header = {"alg": JWT_ALGO, "typ": "JWT"}
    now = int(time.time())
    body = {**payload, "iat": now, "exp": now + ttl}

    h = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url_encode(json.dumps(body, separators=(",", ":")).encode())
    sig = hmac.new(JWT_SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
    s = _b64url_encode(sig)
    return f"{h}.{p}.{s}"

def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
    try:
        h, p, s = token.split(".")
        expected = hmac.new(JWT_SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url_encode(expected), s):
            return None
        payload = json.loads(_b64url_decode(p))
        if int(time.time()) > int(payload.get("exp", 0)):
            return None
        return payload
    except Exception:
        return None
