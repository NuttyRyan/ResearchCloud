from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def connection_id(auth_client: TestClient) -> int:
    resp = auth_client.post(
        "/api/connections",
        json={
            "name": "pc-res",
            "host": "10.0.0.10",
            "username": "admin",
            "secret": "secret",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_list_clusters(auth_client: TestClient, connection_id: int) -> None:
    resp = auth_client.get(f"/api/connections/{connection_id}/clusters")
    assert resp.status_code == 200
    clusters = resp.json()
    assert len(clusters) >= 1
    assert clusters[0]["ext_id"]


def test_create_and_list_project(auth_client: TestClient, connection_id: int) -> None:
    resp = auth_client.post(
        f"/api/connections/{connection_id}/projects",
        json={"name": "genomics", "description": "Genomics research"},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["name"] == "genomics"

    names = [p["name"] for p in auth_client.get(
        f"/api/connections/{connection_id}/projects"
    ).json()]
    assert "genomics" in names


def test_deploy_file_server(auth_client: TestClient, connection_id: int) -> None:
    clusters = auth_client.get(f"/api/connections/{connection_id}/clusters").json()
    cluster_ext_id = clusters[0]["ext_id"]
    resp = auth_client.post(
        f"/api/connections/{connection_id}/files",
        json={"name": "lab-files", "cluster_ext_id": cluster_ext_id, "size_gib": 2048},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["name"] == "lab-files"
    assert body["state"] == "DEPLOYING"


def test_deploy_object_store(auth_client: TestClient, connection_id: int) -> None:
    clusters = auth_client.get(f"/api/connections/{connection_id}/clusters").json()
    cluster_ext_id = clusters[0]["ext_id"]
    resp = auth_client.post(
        f"/api/connections/{connection_id}/objects",
        json={"name": "lab-bucket-store", "cluster_ext_id": cluster_ext_id},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["endpoint"].startswith("lab-bucket-store")


def test_create_and_list_share(auth_client: TestClient, connection_id: int) -> None:
    base = f"/api/connections/{connection_id}"
    fs_ext_id = auth_client.get(f"{base}/files").json()[0]["ext_id"]
    resp = auth_client.post(
        f"{base}/files/{fs_ext_id}/shares",
        json={
            "name": "team-share",
            "protocol": "NFS",
            "size_gib": 256,
            "permissions": [{"principal": "genomics", "access": "READ_WRITE"}],
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["name"] == "team-share"
    assert body["protocol"] == "NFS"
    assert body["permissions"][0]["principal"] == "genomics"

    names = [s["name"] for s in auth_client.get(f"{base}/files/{fs_ext_id}/shares").json()]
    assert "team-share" in names


def test_create_and_list_bucket(auth_client: TestClient, connection_id: int) -> None:
    base = f"/api/connections/{connection_id}"
    os_ext_id = auth_client.get(f"{base}/objects").json()[0]["ext_id"]
    resp = auth_client.post(
        f"{base}/objects/{os_ext_id}/buckets",
        json={"name": "results", "versioning": True, "size_gib": 512},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["versioning"] is True

    names = [b["name"] for b in auth_client.get(f"{base}/objects/{os_ext_id}/buckets").json()]
    assert "results" in names


def test_project_utilization(auth_client: TestClient, connection_id: int) -> None:
    base = f"/api/connections/{connection_id}"
    util = auth_client.get(f"{base}/projects/utilization")
    assert util.status_code == 200, util.text
    rows = util.json()
    assert len(rows) >= 1
    default = next(r for r in rows if r["project_name"] == "default")
    # The seed VM (4 vCPU / 16 GiB) is in the default project.
    assert default["vcpus"]["limit"] == 64
    assert default["vcpus"]["used"] >= 4
    assert default["memory_gib"]["used"] >= 16


def test_cost_summary_placeholder(auth_client: TestClient, connection_id: int) -> None:
    resp = auth_client.get(f"/api/connections/{connection_id}/cost/summary")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["available"] is False
    assert body["source"] == "NCM Cost Governance"
    assert "NCM Cost Governance" in body["note"]


def test_vm_lifecycle(auth_client: TestClient, connection_id: int) -> None:
    base = f"/api/connections/{connection_id}"
    cluster_ext_id = auth_client.get(f"{base}/clusters").json()[0]["ext_id"]
    project_ext_id = auth_client.get(f"{base}/projects").json()[0]["ext_id"]

    created = auth_client.post(
        f"{base}/vms",
        json={
            "name": "analysis-01",
            "project_ext_id": project_ext_id,
            "cluster_ext_id": cluster_ext_id,
            "num_vcpus": 8,
            "memory_gib": 32,
            "os": "Ubuntu 22.04",
        },
    )
    assert created.status_code == 201, created.text
    vm = created.json()
    assert vm["power_state"] == "ON"
    vm_ext_id = vm["ext_id"]

    powered_off = auth_client.post(
        f"{base}/vms/{vm_ext_id}/power", json={"action": "OFF"}
    ).json()
    assert powered_off["power_state"] == "OFF"
    assert powered_off["ip_address"] is None

    # Filter by project includes our VM.
    project_vms = auth_client.get(f"{base}/vms", params={"project": project_ext_id}).json()
    assert any(v["ext_id"] == vm_ext_id for v in project_vms)

    resp = auth_client.delete(f"{base}/vms/{vm_ext_id}")
    assert resp.status_code == 204
    remaining = [v["ext_id"] for v in auth_client.get(f"{base}/vms").json()]
    assert vm_ext_id not in remaining
