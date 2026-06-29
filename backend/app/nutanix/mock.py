from __future__ import annotations

import threading
import uuid

from app.nutanix.base import NutanixClient, NutanixError
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
    SharePermission,
    Vm,
    VmCreate,
    VmPowerActionType,
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
        # Shares keyed by file server ext_id; buckets keyed by object store ext_id.
        self.shares: dict[str, list[Share]] = {
            "fs-seed-1": [
                Share(
                    ext_id="sh-seed-1",
                    name="datasets",
                    file_server_ext_id="fs-seed-1",
                    file_server_name="research-files",
                    protocol="SMB",
                    size_gib=512,
                    state="AVAILABLE",
                    permissions=[SharePermission(principal="research-admins", access="READ_WRITE")],
                ),
            ],
        }
        self.buckets: dict[str, list[Bucket]] = {
            "os-seed-1": [
                Bucket(
                    ext_id="bk-seed-1",
                    name="raw-data",
                    object_store_ext_id="os-seed-1",
                    object_store_name="research-objects",
                    versioning=True,
                    size_gib=1024,
                    state="COMPLETE",
                ),
            ],
        }
        self.vms: list[Vm] = [
            Vm(
                ext_id="vm-seed-1",
                name="jupyter-01",
                project_ext_id="prj-default",
                project_name="default",
                cluster_ext_id="0005f1a2-cls-1",
                cluster_name="rtp-prod-01",
                num_vcpus=4,
                memory_gib=16,
                os="Ubuntu 22.04",
                power_state="ON",
                ip_address="10.20.0.21",
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

    def _file_server(self, ext_id: str) -> FileServer:
        for fs in self._state.file_servers:
            if fs.ext_id == ext_id:
                return fs
        raise NutanixError(f"Unknown file server: {ext_id}")

    def _object_store(self, ext_id: str) -> ObjectStore:
        for os_ in self._state.object_stores:
            if os_.ext_id == ext_id:
                return os_
        raise NutanixError(f"Unknown object store: {ext_id}")

    def _project(self, ext_id: str) -> Project:
        for project in self._state.projects:
            if project.ext_id == ext_id:
                return project
        raise NutanixError(f"Unknown project: {ext_id}")

    def list_shares(self, file_server_ext_id: str) -> list[Share]:
        self._file_server(file_server_ext_id)
        return list(self._state.shares.get(file_server_ext_id, []))

    def create_share(self, file_server_ext_id: str, payload: ShareCreate) -> Share:
        fs = self._file_server(file_server_ext_id)
        shares = self._state.shares.setdefault(file_server_ext_id, [])
        if any(s.name == payload.name for s in shares):
            raise NutanixError(f"Share '{payload.name}' already exists")
        share = Share(
            ext_id=f"sh-{uuid.uuid4().hex[:12]}",
            name=payload.name,
            file_server_ext_id=fs.ext_id,
            file_server_name=fs.name,
            protocol=payload.protocol,
            size_gib=payload.size_gib,
            state="AVAILABLE",
            permissions=payload.permissions,
        )
        shares.append(share)
        return share

    def list_buckets(self, object_store_ext_id: str) -> list[Bucket]:
        self._object_store(object_store_ext_id)
        return list(self._state.buckets.get(object_store_ext_id, []))

    def create_bucket(self, object_store_ext_id: str, payload: BucketCreate) -> Bucket:
        store = self._object_store(object_store_ext_id)
        buckets = self._state.buckets.setdefault(object_store_ext_id, [])
        if any(b.name == payload.name for b in buckets):
            raise NutanixError(f"Bucket '{payload.name}' already exists")
        bucket = Bucket(
            ext_id=f"bk-{uuid.uuid4().hex[:12]}",
            name=payload.name,
            object_store_ext_id=store.ext_id,
            object_store_name=store.name,
            versioning=payload.versioning,
            size_gib=payload.size_gib,
            state="COMPLETE",
        )
        buckets.append(bucket)
        return bucket

    def list_vms(self, project_ext_id: str | None = None) -> list[Vm]:
        vms = list(self._state.vms)
        if project_ext_id:
            vms = [vm for vm in vms if vm.project_ext_id == project_ext_id]
        return vms

    def create_vm(self, payload: VmCreate) -> Vm:
        cluster = self._cluster(payload.cluster_ext_id)
        project = self._project(payload.project_ext_id)
        if any(vm.name == payload.name for vm in self._state.vms):
            raise NutanixError(f"VM '{payload.name}' already exists")
        vm = Vm(
            ext_id=f"vm-{uuid.uuid4().hex[:12]}",
            name=payload.name,
            project_ext_id=project.ext_id,
            project_name=project.name,
            cluster_ext_id=cluster.ext_id,
            cluster_name=cluster.name,
            num_vcpus=payload.num_vcpus,
            memory_gib=payload.memory_gib,
            os=payload.os,
            power_state="ON",
            ip_address=f"10.20.0.{50 + len(self._state.vms)}",
        )
        self._state.vms.append(vm)
        return vm

    def _vm(self, ext_id: str) -> Vm:
        for vm in self._state.vms:
            if vm.ext_id == ext_id:
                return vm
        raise NutanixError(f"Unknown VM: {ext_id}")

    def set_vm_power(self, vm_ext_id: str, action: VmPowerActionType) -> Vm:
        vm = self._vm(vm_ext_id)
        if action == "ON":
            vm.power_state = "ON"
        elif action == "OFF":
            vm.power_state = "OFF"
            vm.ip_address = None
        elif action == "RESTART":
            vm.power_state = "ON"
        return vm

    def delete_vm(self, vm_ext_id: str) -> None:
        vm = self._vm(vm_ext_id)
        self._state.vms.remove(vm)
