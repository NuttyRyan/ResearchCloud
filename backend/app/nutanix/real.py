from __future__ import annotations

from typing import Any

import httpx

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

    def _post(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        try:
            with self._client() as client:
                resp = client.post(path, json=json)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as exc:  # noqa: B904
            raise NutanixError(f"POST {path} failed: {exc}") from exc

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
