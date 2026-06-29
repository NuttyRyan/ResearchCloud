from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DbSession, get_connection_or_404, get_current_user
from app.models.connection import PrismConnection
from app.nutanix.base import NutanixError
from app.nutanix.factory import get_client
from app.schemas.connection import (
    ConnectionCreate,
    ConnectionOut,
    ConnectionTestResult,
    ConnectionUpdate,
)
from app.services import connection_service

router = APIRouter(
    prefix="/api/connections",
    tags=["connections"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[ConnectionOut])
def list_connections(db: DbSession) -> list[PrismConnection]:
    return connection_service.list_connections(db)


@router.post("", response_model=ConnectionOut, status_code=status.HTTP_201_CREATED)
def create_connection(payload: ConnectionCreate, db: DbSession) -> PrismConnection:
    if connection_service.get_by_name(db, payload.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Connection '{payload.name}' already exists",
        )
    return connection_service.create_connection(db, payload)


@router.get("/{connection_id}", response_model=ConnectionOut)
def get_connection(
    connection: PrismConnection = Depends(get_connection_or_404),
) -> PrismConnection:
    return connection


@router.patch("/{connection_id}", response_model=ConnectionOut)
def update_connection(
    payload: ConnectionUpdate,
    db: DbSession,
    connection: PrismConnection = Depends(get_connection_or_404),
) -> PrismConnection:
    return connection_service.update_connection(db, connection, payload)


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(
    db: DbSession, connection: PrismConnection = Depends(get_connection_or_404)
) -> None:
    connection_service.delete_connection(db, connection)


@router.post("/{connection_id}/test", response_model=ConnectionTestResult)
def test_connection(
    connection: PrismConnection = Depends(get_connection_or_404),
) -> ConnectionTestResult:
    client = get_client(connection)
    try:
        version, cluster_count = client.test_connection()
    except NutanixError as exc:
        return ConnectionTestResult(
            ok=False, message=str(exc), mode=client.mode
        )
    return ConnectionTestResult(
        ok=True,
        message="Connection successful",
        prism_central_version=version,
        cluster_count=cluster_count,
        mode=client.mode,
    )
