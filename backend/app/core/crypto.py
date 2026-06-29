from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import get_settings


def _derive_fernet_key() -> bytes:
    """Return a urlsafe base64 Fernet key.

    Uses ``RC_ENCRYPTION_KEY`` when provided, otherwise derives a stable key from
    the application secret so local development works without extra setup. In
    production an explicit ``RC_ENCRYPTION_KEY`` should always be supplied.
    """

    settings = get_settings()
    if settings.encryption_key:
        key = settings.encryption_key.encode()
        # Accept either a ready-made Fernet key or arbitrary text.
        try:
            Fernet(key)
            return key
        except (ValueError, TypeError):
            digest = hashlib.sha256(key).digest()
            return base64.urlsafe_b64encode(digest)

    digest = hashlib.sha256(settings.secret_key.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def _fernet() -> Fernet:
    return Fernet(_derive_fernet_key())


def encrypt_secret(plaintext: str) -> str:
    """Encrypt a secret string, returning a urlsafe token."""

    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_secret(token: str) -> str:
    """Decrypt a token produced by :func:`encrypt_secret`."""

    return _fernet().decrypt(token.encode()).decode()
