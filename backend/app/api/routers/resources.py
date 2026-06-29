from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import NutanixDep, get_current_user
from app.nutanix.base import NutanixError
from app.schemas.nutanix import (
    Cluster,
    FileServer,
    FileServerCreate,
    ObjectStore,
    ObjectStoreCreate,
    Project,
    ProjectCreate,
)

router = APIRouter(
    prefix="/api/connections/{connection_id}",
    tags=["resources"],
    dependencies=[Depends(get_current_user)],
)


def _handle(exc: NutanixError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))


@router.get("/clusters", response_model=list[Cluster])
def list_clusters(client: NutanixDep) -> list[Cluster]:
    try:
        return client.list_clusters()
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.get("/projects", response_model=list[Project])
def list_projects(client: NutanixDep) -> list[Project]:
    try:
        return client.list_projects()
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, client: NutanixDep) -> Project:
    try:
        return client.create_project(payload)
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.get("/files", response_model=list[FileServer])
def list_file_servers(client: NutanixDep) -> list[FileServer]:
    try:
        return client.list_file_servers()
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.post("/files", response_model=FileServer, status_code=status.HTTP_201_CREATED)
def create_file_server(payload: FileServerCreate, client: NutanixDep) -> FileServer:
    try:
        return client.create_file_server(payload)
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.get("/objects", response_model=list[ObjectStore])
def list_object_stores(client: NutanixDep) -> list[ObjectStore]:
    try:
        return client.list_object_stores()
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.post("/objects", response_model=ObjectStore, status_code=status.HTTP_201_CREATED)
def create_object_store(payload: ObjectStoreCreate, client: NutanixDep) -> ObjectStore:
    try:
        return client.create_object_store(payload)
    except NutanixError as exc:
        raise _handle(exc) from exc
