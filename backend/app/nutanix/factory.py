from __future__ import annotations

from app.core.config import get_settings
from app.core.crypto import decrypt_secret
from app.models.connection import PrismConnection
from app.nutanix.base import NutanixClient
from app.nutanix.mock import MockNutanixClient
from app.nutanix.real import RealNutanixClient


def get_client(connection: PrismConnection) -> NutanixClient:
    """Return a Nutanix client for the given connection.

    Uses the deterministic mock provider when ``RC_FORCE_MOCK_NUTANIX`` is set
    (default in development), otherwise a live v4 REST client.
    """

    settings = get_settings()
    if settings.force_mock_nutanix:
        return MockNutanixClient(connection.id)

    return RealNutanixClient(
        host=connection.host,
        port=connection.port,
        username=connection.username,
        secret=decrypt_secret(connection.encrypted_secret),
        verify_ssl=connection.verify_ssl,
    )
