from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.crypto import encrypt_secret
from app.models.connection import PrismConnection
from app.schemas.connection import ConnectionCreate, ConnectionUpdate


def list_connections(db: Session) -> list[PrismConnection]:
    return list(db.scalars(select(PrismConnection).order_by(PrismConnection.id)))


def get_connection(db: Session, connection_id: int) -> PrismConnection | None:
    return db.get(PrismConnection, connection_id)


def get_by_name(db: Session, name: str) -> PrismConnection | None:
    return db.scalar(select(PrismConnection).where(PrismConnection.name == name))


def create_connection(db: Session, payload: ConnectionCreate) -> PrismConnection:
    connection = PrismConnection(
        name=payload.name,
        host=payload.host,
        port=payload.port,
        username=payload.username,
        verify_ssl=payload.verify_ssl,
        encrypted_secret=encrypt_secret(payload.secret),
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


def update_connection(
    db: Session, connection: PrismConnection, payload: ConnectionUpdate
) -> PrismConnection:
    data = payload.model_dump(exclude_unset=True)
    secret = data.pop("secret", None)
    for field, value in data.items():
        setattr(connection, field, value)
    if secret:
        connection.encrypted_secret = encrypt_secret(secret)
    db.commit()
    db.refresh(connection)
    return connection


def delete_connection(db: Session, connection: PrismConnection) -> None:
    db.delete(connection)
    db.commit()
