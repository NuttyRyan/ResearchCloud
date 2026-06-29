from __future__ import annotations

import abc

from app.schemas.nutanix import (
    Cluster,
    FileServer,
    FileServerCreate,
    ObjectStore,
    ObjectStoreCreate,
    Project,
    ProjectCreate,
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
