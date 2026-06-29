from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, overridable via environment variables.

    All variables are prefixed with ``RC_`` (e.g. ``RC_DATABASE_URL``).
    """

    model_config = SettingsConfigDict(env_prefix="RC_", env_file=".env", extra="ignore")

    app_name: str = "ResearchCloud"
    environment: str = "development"

    # SQLite for local dev; swap to a Postgres URL in deploy via RC_DATABASE_URL.
    database_url: str = "sqlite:///./researchcloud.db"

    # JWT signing secret. MUST be overridden in production via RC_SECRET_KEY.
    secret_key: str = "dev-insecure-secret-change-me"
    access_token_expire_minutes: int = 480

    # Fernet key used to encrypt stored Prism Central credentials. When unset, a
    # deterministic dev key is derived from secret_key so local dev works out of the box.
    encryption_key: str | None = None

    # Default seeded admin account for first login (dev convenience).
    admin_username: str = "admin"
    admin_password: str = "admin"

    # When true, the NutanixClient always uses the deterministic mock provider,
    # regardless of stored credentials. Useful for demos and CI.
    force_mock_nutanix: bool = True

    # CORS origins allowed to call the API (frontend dev server).
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
