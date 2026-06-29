from __future__ import annotations

import abc

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
    ProjectUtilization,
    Share,
    ShareCreate,
    Vm,
    VmCreate,
    VmPowerActionType,
)


class NutanixError(Exception):
    """Raised when a Nutanix operation fails."""


class NutanixClient(abc.ABC):
    """Abstraction over Nutanix Prism Central operations.

    Implemented by both a real v4 REST client and a deterministic mock used for
    local development, demos and tests.
    """

    mode: str = "base"

    @abc.abstractmethod
    def test_connection(self) -> tuple[str, int]:
        """Return ``(prism_central_version, cluster_count)`` or raise NutanixError."""

    @abc.abstractmethod
    def list_clusters(self) -> list[Cluster]:
        ...

    @abc.abstractmethod
    def list_projects(self) -> list[Project]:
        ...

    @abc.abstractmethod
    def create_project(self, payload: ProjectCreate) -> Project:
        ...

    @abc.abstractmethod
    def list_project_utilization(self) -> list[ProjectUtilization]:
        ...

    @abc.abstractmethod
    def list_file_servers(self) -> list[FileServer]:
        ...

    @abc.abstractmethod
    def create_file_server(self, payload: FileServerCreate) -> FileServer:
        ...

    @abc.abstractmethod
    def list_object_stores(self) -> list[ObjectStore]:
        ...

    @abc.abstractmethod
    def create_object_store(self, payload: ObjectStoreCreate) -> ObjectStore:
        ...

    # --- Phase 2: file shares ---

    @abc.abstractmethod
    def list_shares(self, file_server_ext_id: str) -> list[Share]:
        ...

    @abc.abstractmethod
    def create_share(self, file_server_ext_id: str, payload: ShareCreate) -> Share:
        ...

    # --- Phase 2: object buckets ---

    @abc.abstractmethod
    def list_buckets(self, object_store_ext_id: str) -> list[Bucket]:
        ...

    @abc.abstractmethod
    def create_bucket(self, object_store_ext_id: str, payload: BucketCreate) -> Bucket:
        ...

    # --- Phase 6: virtual machines ---

    @abc.abstractmethod
    def list_vms(self, project_ext_id: str | None = None) -> list[Vm]:
        ...

    @abc.abstractmethod
    def create_vm(self, payload: VmCreate) -> Vm:
        ...

    @abc.abstractmethod
    def set_vm_power(self, vm_ext_id: str, action: VmPowerActionType) -> Vm:
        ...

    @abc.abstractmethod
    def delete_vm(self, vm_ext_id: str) -> None:
        ...
