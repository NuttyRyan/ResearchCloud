from __future__ import annotations

import threading
import uuid

from app.nutanix.base import NutanixClient, NutanixError
from app.schemas.nutanix import (
    Cluster,
    FileServer,
    FileServerCreate,
    ObjectStore,
    ObjectStoreCreate,
    Project,
    ProjectCreate,
)

_PC_VERSION = "pc.2024.3.1"


class _ConnectionState:
    """In-memory per-connection state so create/list behaves realistically."""

    def __init__(self) -> None:
        self.clusters: list[Cluster] = [
            Cluster(
                ext_id="0005f1a2-cls-1",
                name="rtp-prod-01",
                hypervisor="AHV",
                node_count=4,
            ),
            Cluster(
                ext_id="0005f1a2-cls-2",
                name="lab-edge-02",
                hypervisor="AHV",
                node_count=3,
            ),
        ]
        self.projects: list[Project] = [
            Project(
                ext_id="prj-default",
                name="default",
                description="Default Prism Central project",
                vm_count=12,
            ),
        ]
        self.file_servers: list[FileServer] = [
            FileServer(
                ext_id="fs-seed-1",
                name="research-files",
                cluster_ext_id="0005f1a2-cls-1",
                cluster_name="rtp-prod-01",
                size_gib=4096,
                state="AVAILABLE",
                version="5.1",
            ),
        ]
        self.object_stores: list[ObjectStore] = [
            ObjectStore(
                ext_id="os-seed-1",
                name="research-objects",
                cluster_ext_id="0005f1a2-cls-1",
                cluster_name="rtp-prod-01",
                capacity_gib=8192,
                state="COMPLETE",
                endpoint="research-objects.objects.rtp-prod-01.local",
            ),
        ]


class _MockStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._states: dict[int, _ConnectionState] = {}

    def state(self, connection_id: int) -> _ConnectionState:
        with self._lock:
            if connection_id not in self._states:
                self._states[connection_id] = _ConnectionState()
            return self._states[connection_id]

    def reset(self) -> None:
        with self._lock:
            self._states.clear()


_store = _MockStore()


def reset_mock_store() -> None:
    """Clear all mock state (used by tests)."""

    _store.reset()


class MockNutanixClient(NutanixClient):
    mode = "mock"

    def __init__(self, connection_id: int) -> None:
        self._state = _store.state(connection_id)

    def test_connection(self) -> tuple[str, int]:
        return _PC_VERSION, len(self._state.clusters)

    def list_clusters(self) -> list[Cluster]:
        return list(self._state.clusters)

    def _cluster(self, cluster_ext_id: str) -> Cluster:
        for cluster in self._state.clusters:
            if cluster.ext_id == cluster_ext_id:
                return cluster
        raise NutanixError(f"Unknown cluster: {cluster_ext_id}")

    def list_projects(self) -> list[Project]:
        return list(self._state.projects)

    def create_project(self, payload: ProjectCreate) -> Project:
        if any(p.name == payload.name for p in self._state.projects):
            raise NutanixError(f"Project '{payload.name}' already exists")
        project = Project(
            ext_id=f"prj-{uuid.uuid4().hex[:12]}",
            name=payload.name,
            description=payload.description,
            state="ACTIVE",
            vm_count=0,
        )
        self._state.projects.append(project)
        return project

    def list_file_servers(self) -> list[FileServer]:
        return list(self._state.file_servers)

    def create_file_server(self, payload: FileServerCreate) -> FileServer:
        cluster = self._cluster(payload.cluster_ext_id)
        if any(f.name == payload.name for f in self._state.file_servers):
            raise NutanixError(f"File server '{payload.name}' already exists")
        fs = FileServer(
            ext_id=f"fs-{uuid.uuid4().hex[:12]}",
            name=payload.name,
            cluster_ext_id=cluster.ext_id,
            cluster_name=cluster.name,
            size_gib=payload.size_gib,
            state="DEPLOYING",
            version="5.1",
        )
        self._state.file_servers.append(fs)
        return fs

    def list_object_stores(self) -> list[ObjectStore]:
        return list(self._state.object_stores)

    def create_object_store(self, payload: ObjectStoreCreate) -> ObjectStore:
        cluster = self._cluster(payload.cluster_ext_id)
        if any(o.name == payload.name for o in self._state.object_stores):
            raise NutanixError(f"Object store '{payload.name}' already exists")
        store = ObjectStore(
            ext_id=f"os-{uuid.uuid4().hex[:12]}",
            name=payload.name,
            cluster_ext_id=cluster.ext_id,
            cluster_name=cluster.name,
            capacity_gib=payload.capacity_gib,
            state="DEPLOYING",
            endpoint=f"{payload.name}.objects.{cluster.name}.local",
        )
        self._state.object_stores.append(store)
        return store
