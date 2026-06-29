from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import User


def init_db() -> None:
    """Create tables and seed the default admin user (idempotent)."""

    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        settings = get_settings()
        existing = (
            db.query(User).filter(User.username == settings.admin_username).first()
        )
        if existing is None:
            db.add(
                User(
                    username=settings.admin_username,
                    password_hash=hash_password(settings.admin_password),
                    is_admin=True,
                    ad_groups="research-admins",
                )
            )
            db.commit()
    finally:
        db.close()
