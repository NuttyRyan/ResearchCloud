from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.connection import PrismConnection
from app.models.user import User
from app.nutanix.base import NutanixClient
from app.nutanix.factory import get_client
from app.services import connection_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=True)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    username = decode_access_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_connection_or_404(connection_id: int, db: DbSession) -> PrismConnection:
    connection = connection_service.get_connection(db, connection_id)
    if connection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found"
        )
    return connection


def get_nutanix_client(
    connection: Annotated[PrismConnection, Depends(get_connection_or_404)],
) -> NutanixClient:
    return get_client(connection)


NutanixDep = Annotated[NutanixClient, Depends(get_nutanix_client)]
