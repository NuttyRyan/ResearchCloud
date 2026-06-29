from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import NutanixDep, get_current_user
from app.nutanix.base import NutanixError
from app.schemas.nutanix import (
    Bucket,
    BucketCreate,
    Cluster,
    FileServer,
    FileServerCreate,
    ObjectStore,
    ObjectStoreCreate,
    Project,
    ProjectCreate,
    Share,
    ShareCreate,
    Vm,
    VmCreate,
    VmPowerAction,
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


# --- Phase 2: file shares ---


@router.get("/files/{file_server_ext_id}/shares", response_model=list[Share])
def list_shares(file_server_ext_id: str, client: NutanixDep) -> list[Share]:
    try:
        return client.list_shares(file_server_ext_id)
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.post(
    "/files/{file_server_ext_id}/shares",
    response_model=Share,
    status_code=status.HTTP_201_CREATED,
)
def create_share(
    file_server_ext_id: str, payload: ShareCreate, client: NutanixDep
) -> Share:
    try:
        return client.create_share(file_server_ext_id, payload)
    except NutanixError as exc:
        raise _handle(exc) from exc


# --- Phase 2: object buckets ---


@router.get("/objects/{object_store_ext_id}/buckets", response_model=list[Bucket])
def list_buckets(object_store_ext_id: str, client: NutanixDep) -> list[Bucket]:
    try:
        return client.list_buckets(object_store_ext_id)
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.post(
    "/objects/{object_store_ext_id}/buckets",
    response_model=Bucket,
    status_code=status.HTTP_201_CREATED,
)
def create_bucket(
    object_store_ext_id: str, payload: BucketCreate, client: NutanixDep
) -> Bucket:
    try:
        return client.create_bucket(object_store_ext_id, payload)
    except NutanixError as exc:
        raise _handle(exc) from exc


# --- Phase 6: virtual machines ---


@router.get("/vms", response_model=list[Vm])
def list_vms(
    client: NutanixDep, project: str | None = Query(default=None)
) -> list[Vm]:
    try:
        return client.list_vms(project)
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.post("/vms", response_model=Vm, status_code=status.HTTP_201_CREATED)
def create_vm(payload: VmCreate, client: NutanixDep) -> Vm:
    try:
        return client.create_vm(payload)
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.post("/vms/{vm_ext_id}/power", response_model=Vm)
def set_vm_power(vm_ext_id: str, payload: VmPowerAction, client: NutanixDep) -> Vm:
    try:
        return client.set_vm_power(vm_ext_id, payload.action)
    except NutanixError as exc:
        raise _handle(exc) from exc


@router.delete("/vms/{vm_ext_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vm(vm_ext_id: str, client: NutanixDep) -> None:
    try:
        client.delete_vm(vm_ext_id)
    except NutanixError as exc:
        raise _handle(exc) from exc
