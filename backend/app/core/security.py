from __future__ import annotations

import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings

_PBKDF2_ROUNDS = 200_000
_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 (stdlib only)."""

    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${_PBKDF2_ROUNDS}${salt.hex()}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, rounds, salt_hex, hash_hex = stored.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds)
    )
    return hmac.compare_digest(derived.hex(), hash_hex)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")
