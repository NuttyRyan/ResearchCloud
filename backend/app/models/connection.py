from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class PrismConnection(Base):
    """A stored Nutanix Prism Central connection.

    The credential (password or API key) is stored encrypted at rest via Fernet.
    """

    __tablename__ = "prism_connections"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    host: Mapped[str] = mapped_column(String(255))
    port: Mapped[int] = mapped_column(Integer, default=9440)
    username: Mapped[str] = mapped_column(String(150))
    encrypted_secret: Mapped[str] = mapped_column(String(2048))
    verify_ssl: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )
