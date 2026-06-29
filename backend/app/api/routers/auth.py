from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DbSession
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import Token, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(db: DbSession, form: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = db.query(User).filter(User.username == form.username).first()
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.username))


@router.get("/me", response_model=UserOut)
def me(current_user: CurrentUser) -> UserOut:
    groups = [g for g in (current_user.ad_groups or "").split(",") if g]
    return UserOut(
        username=current_user.username,
        is_admin=current_user.is_admin,
        ad_groups=groups,
    )
