from __future__ import annotations

from typing import Any

import httpx

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
    Vm,
    VmCreate,
    VmPowerActionType,
)


class RealNutanixClient(NutanixClient):
    """Live client targeting the Nutanix Prism Central v4 REST APIs.

    Projects are accessed via the v3 API because full Projects support in v4 is
    only expected mid-2026 (legacy v3 is supported until Q4 2026).
    """

    mode = "live"

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        secret: str,
        verify_ssl: bool = False,
        timeout: float = 30.0,
    ) -> None:
        self._base = f"https://{host}:{port}"
        self._auth = httpx.BasicAuth(username, secret)
        self._verify = verify_ssl
        self._timeout = timeout

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self._base,
            auth=self._auth,
            verify=self._verify,
            timeout=self._timeout,
            headers={"Accept": "application/json"},
        )

    def _get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        try:
            with self._client() as client:
                resp = client.get(path, **kwargs)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as exc:  # noqa: B904
            raise NutanixError(f"GET {path} failed: {exc}") from exc

    def _post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            with self._client() as client:
                resp = client.post(path, json=json or {})
                resp.raise_for_status()
                return resp.json() if resp.content else {}
        except httpx.HTTPError as exc:  # noqa: B904
            raise NutanixError(f"POST {path} failed: {exc}") from exc

    def _delete(self, path: str) -> None:
        try:
            with self._client() as client:
                resp = client.delete(path)
                resp.raise_for_status()
        except httpx.HTTPError as exc:  # noqa: B904
            raise NutanixError(f"DELETE {path} failed: {exc}") from exc

    def test_connection(self) -> tuple[str, int]:
        clusters = self.list_clusters()
        version = "unknown"
        try:
            data = self._get("/api/prism/v4.0/config/domain-managers")
            items = data.get("data") or []
            if items:
                version = items[0].get("version", "unknown")
        except NutanixError:
            pass
        return version, len(clusters)

    def list_clusters(self) -> list[Cluster]:
        data = self._get("/api/clustermgmt/v4.0/config/clusters")
        clusters: list[Cluster] = []
        for item in data.get("data", []) or []:
            config = item.get("config", {}) or {}
            nodes = item.get("nodes", {}) or {}
            clusters.append(
                Cluster(
                    ext_id=item.get("extId", ""),
                    name=config.get("name", item.get("name", "")),
                    hypervisor=(config.get("hypervisorTypes") or ["AHV"])[0],
                    node_count=nodes.get("numberOfNodes", 0),
                )
            )
        return clusters

    def list_projects(self) -> list[Project]:
        data = self._post(
            "/api/nutanix/v3/projects/list", {"kind": "project", "length": 250}
        )
        projects: list[Project] = []
        for item in data.get("entities", []) or []:
            meta = item.get("metadata", {}) or {}
            spec = item.get("spec", {}) or {}
            projects.append(
                Project(
                    ext_id=meta.get("uuid", ""),
                    name=spec.get("name", ""),
                    description=spec.get("description", ""),
                    state=item.get("status", {}).get("state", "ACTIVE"),
                )
            )
        return projects

    def create_project(self, payload: ProjectCreate) -> Project:
        body = {
            "spec": {
                "name": payload.name,
                "description": payload.description,
                "resources": {},
            },
            "metadata": {"kind": "project"},
            "api_version": "3.1.0",
        }
        data = self._post("/api/nutanix/v3/projects", body)
        meta = data.get("metadata", {}) or {}
        spec = data.get("spec", {}) or {}
        return Project(
            ext_id=meta.get("uuid", ""),
            name=spec.get("name", payload.name),
            description=spec.get("description", payload.description),
            state="PENDING",
        )

    def list_file_servers(self) -> list[FileServer]:
        data = self._get("/api/files/v4.0/config/file-servers")
        servers: list[FileServer] = []
        for item in data.get("data", []) or []:
            servers.append(
                FileServer(
                    ext_id=item.get("extId", ""),
                    name=item.get("name", ""),
                    cluster_ext_id=item.get("clusterExtId", ""),
                    cluster_name=item.get("clusterName", ""),
                    size_gib=int(item.get("sizeInGib", 0)),
                    state=item.get("state", "UNKNOWN"),
                    version=item.get("version", ""),
                )
            )
        return servers

    def create_file_server(self, payload: FileServerCreate) -> FileServer:
        body = {
            "name": payload.name,
            "clusterExtId": payload.cluster_ext_id,
            "sizeInGib": payload.size_gib,
        }
        data = self._post("/api/files/v4.0/config/file-servers", body)
        item = data.get("data", body)
        return FileServer(
            ext_id=item.get("extId", ""),
            name=item.get("name", payload.name),
            cluster_ext_id=payload.cluster_ext_id,
            cluster_name=item.get("clusterName", ""),
            size_gib=payload.size_gib,
            state=item.get("state", "DEPLOYING"),
            version=item.get("version", ""),
        )

    def list_object_stores(self) -> list[ObjectStore]:
        data = self._get("/api/objects/v4.0/config/object-stores")
        stores: list[ObjectStore] = []
        for item in data.get("data", []) or []:
            stores.append(
                ObjectStore(
                    ext_id=item.get("extId", ""),
                    name=item.get("name", ""),
                    cluster_ext_id=item.get("clusterExtId", ""),
                    cluster_name=item.get("clusterName", ""),
                    capacity_gib=int(item.get("totalCapacityGiB", 0)),
                    state=item.get("state", "UNKNOWN"),
                    endpoint=item.get("ipAddress", ""),
                )
            )
        return stores

    def create_object_store(self, payload: ObjectStoreCreate) -> ObjectStore:
        body = {
            "name": payload.name,
            "clusterExtId": payload.cluster_ext_id,
            "totalCapacityGiB": payload.capacity_gib,
        }
        data = self._post("/api/objects/v4.0/config/object-stores", body)
        item = data.get("data", body)
        return ObjectStore(
            ext_id=item.get("extId", ""),
            name=item.get("name", payload.name),
            cluster_ext_id=payload.cluster_ext_id,
            cluster_name=item.get("clusterName", ""),
            capacity_gib=payload.capacity_gib,
            state=item.get("state", "DEPLOYING"),
            endpoint=item.get("ipAddress", ""),
        )

    def list_shares(self, file_server_ext_id: str) -> list[Share]:
        data = self._get(
            f"/api/files/v4.0/config/file-servers/{file_server_ext_id}/shares"
        )
        shares: list[Share] = []
        for item in data.get("data", []) or []:
            shares.append(
                Share(
                    ext_id=item.get("extId", ""),
                    name=item.get("name", ""),
                    file_server_ext_id=file_server_ext_id,
                    file_server_name=item.get("fileServerName", ""),
                    protocol=item.get("protocol", "SMB"),
                    size_gib=int(item.get("maxSizeGib", 0)),
                    state=item.get("state", "UNKNOWN"),
                    permissions=[],
                )
            )
        return shares

    def create_share(self, file_server_ext_id: str, payload: ShareCreate) -> Share:
        body = {
            "name": payload.name,
            "protocol": payload.protocol,
            "maxSizeGib": payload.size_gib,
        }
        data = self._post(
            f"/api/files/v4.0/config/file-servers/{file_server_ext_id}/shares", body
        )
        item = data.get("data", body)
        return Share(
            ext_id=item.get("extId", ""),
            name=item.get("name", payload.name),
            file_server_ext_id=file_server_ext_id,
            file_server_name=item.get("fileServerName", ""),
            protocol=payload.protocol,
            size_gib=payload.size_gib,
            state=item.get("state", "AVAILABLE"),
            permissions=payload.permissions,
        )

    def list_buckets(self, object_store_ext_id: str) -> list[Bucket]:
        data = self._get(
            f"/api/objects/v4.0/config/object-stores/{object_store_ext_id}/buckets"
        )
        buckets: list[Bucket] = []
        for item in data.get("data", []) or []:
            buckets.append(
                Bucket(
                    ext_id=item.get("extId", ""),
                    name=item.get("name", ""),
                    object_store_ext_id=object_store_ext_id,
                    object_store_name=item.get("objectStoreName", ""),
                    versioning=bool(item.get("versioningEnabled", False)),
                    size_gib=int(item.get("maxSizeGib", 0)),
                    state=item.get("state", "UNKNOWN"),
                )
            )
        return buckets

    def create_bucket(self, object_store_ext_id: str, payload: BucketCreate) -> Bucket:
        body = {
            "name": payload.name,
            "versioningEnabled": payload.versioning,
            "maxSizeGib": payload.size_gib,
        }
        data = self._post(
            f"/api/objects/v4.0/config/object-stores/{object_store_ext_id}/buckets", body
        )
        item = data.get("data", body)
        return Bucket(
            ext_id=item.get("extId", ""),
            name=item.get("name", payload.name),
            object_store_ext_id=object_store_ext_id,
            object_store_name=item.get("objectStoreName", ""),
            versioning=payload.versioning,
            size_gib=payload.size_gib,
            state=item.get("state", "COMPLETE"),
        )

    def list_vms(self, project_ext_id: str | None = None) -> list[Vm]:
        params: dict[str, Any] = {}
        if project_ext_id:
            params["$filter"] = f"project/extId eq '{project_ext_id}'"
        data = self._get("/api/vmm/v4.0/ahv/config/vms", params=params)
        vms: list[Vm] = []
        for item in data.get("data", []) or []:
            cluster = item.get("cluster", {}) or {}
            project = item.get("project", {}) or {}
            nics = item.get("nics", []) or []
            ip = None
            if nics:
                ipinfo = (nics[0].get("networkInfo", {}) or {}).get("ipv4Config", {}) or {}
                ip = (ipinfo.get("ipAddress", {}) or {}).get("value")
            vms.append(
                Vm(
                    ext_id=item.get("extId", ""),
                    name=item.get("name", ""),
                    project_ext_id=project.get("extId", ""),
                    project_name=project.get("name", ""),
                    cluster_ext_id=cluster.get("extId", ""),
                    cluster_name=cluster.get("name", ""),
                    num_vcpus=int(item.get("numSockets", 1))
                    * int(item.get("numCoresPerSocket", 1)),
                    memory_gib=int(item.get("memorySizeBytes", 0)) // (1024**3),
                    os=item.get("guestOs", "unknown"),
                    power_state="ON" if item.get("powerState") == "ON" else "OFF",
                    ip_address=ip,
                )
            )
        return vms

    def create_vm(self, payload: VmCreate) -> Vm:
        body = {
            "name": payload.name,
            "numSockets": payload.num_vcpus,
            "numCoresPerSocket": 1,
            "memorySizeBytes": payload.memory_gib * (1024**3),
            "cluster": {"extId": payload.cluster_ext_id},
            "project": {"extId": payload.project_ext_id},
        }
        data = self._post("/api/vmm/v4.0/ahv/config/vms", body)
        item = data.get("data", body)
        return Vm(
            ext_id=item.get("extId", ""),
            name=payload.name,
            project_ext_id=payload.project_ext_id,
            project_name=item.get("project", {}).get("name", ""),
            cluster_ext_id=payload.cluster_ext_id,
            cluster_name=item.get("cluster", {}).get("name", ""),
            num_vcpus=payload.num_vcpus,
            memory_gib=payload.memory_gib,
            os=payload.os,
            power_state="OFF",
            ip_address=None,
        )

    def set_vm_power(self, vm_ext_id: str, action: VmPowerActionType) -> Vm:
        endpoint = {
            "ON": "power-on",
            "OFF": "power-off",
            "RESTART": "reset",
        }[action]
        self._post(f"/api/vmm/v4.0/ahv/config/vms/{vm_ext_id}/$actions/{endpoint}")
        data = self._get(f"/api/vmm/v4.0/ahv/config/vms/{vm_ext_id}")
        item = data.get("data", {}) or {}
        cluster = item.get("cluster", {}) or {}
        project = item.get("project", {}) or {}
        return Vm(
            ext_id=vm_ext_id,
            name=item.get("name", ""),
            project_ext_id=project.get("extId", ""),
            project_name=project.get("name", ""),
            cluster_ext_id=cluster.get("extId", ""),
            cluster_name=cluster.get("name", ""),
            num_vcpus=int(item.get("numSockets", 1))
            * int(item.get("numCoresPerSocket", 1)),
            memory_gib=int(item.get("memorySizeBytes", 0)) // (1024**3),
            os=item.get("guestOs", "unknown"),
            power_state="ON" if item.get("powerState") == "ON" else "OFF",
            ip_address=None,
        )

    def delete_vm(self, vm_ext_id: str) -> None:
        self._delete(f"/api/vmm/v4.0/ahv/config/vms/{vm_ext_id}")
