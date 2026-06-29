from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    # Comma-separated AD group names linked to this user (Phase 4 expands this).
    ad_groups: Mapped[str] = mapped_column(String(1024), default="")
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
