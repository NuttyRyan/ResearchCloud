from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Blueprint(Base):
    """A Self-Service blueprint authored in ResearchCloud.

    Blueprints are app-level templates (OS + sizing + applications) from which an
    install script and a Calm DSL blueprint are generated.
    """

    __tablename__ = "blueprints"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(1024), default="")
    os: Mapped[str] = mapped_column(String(100), default="Ubuntu 22.04")
    num_vcpus: Mapped[int] = mapped_column(Integer, default=2)
    memory_gib: Mapped[int] = mapped_column(Integer, default=8)
    # List of {name, method: "URL"|"INLINE", url, script}.
    apps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )


class Runbook(Base):
    """A repeatable, selectable script generated from a blueprint (or authored)."""

    __tablename__ = "runbooks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(1024), default="")
    os: Mapped[str] = mapped_column(String(100), default="Ubuntu 22.04")
    script: Mapped[str] = mapped_column(Text, default="")
    source_blueprint_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
