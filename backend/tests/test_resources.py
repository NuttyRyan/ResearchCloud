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
