from __future__ import annotations

from fastapi.testclient import TestClient


def _create_connection(client: TestClient, name: str = "pc-lab") -> dict:
    resp = client.post(
        "/api/connections",
        json={
            "name": name,
            "host": "10.0.0.10",
            "port": 9440,
            "username": "admin",
            "secret": "super-secret",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_connection_crud_and_secret_not_leaked(auth_client: TestClient) -> None:
    created = _create_connection(auth_client)
    assert "secret" not in created
    assert "encrypted_secret" not in created

    listed = auth_client.get("/api/connections").json()
    assert len(listed) == 1

    updated = auth_client.patch(
        f"/api/connections/{created['id']}", json={"host": "10.0.0.20"}
    ).json()
    assert updated["host"] == "10.0.0.20"

    resp = auth_client.delete(f"/api/connections/{created['id']}")
    assert resp.status_code == 204
    assert auth_client.get("/api/connections").json() == []


def test_duplicate_connection_rejected(auth_client: TestClient) -> None:
    _create_connection(auth_client)
    resp = auth_client.post(
        "/api/connections",
        json={
            "name": "pc-lab",
            "host": "1.1.1.1",
            "username": "admin",
            "secret": "x",
        },
    )
    assert resp.status_code == 409


def test_test_connection_mock(auth_client: TestClient) -> None:
    created = _create_connection(auth_client)
    resp = auth_client.post(f"/api/connections/{created['id']}/test")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["mode"] == "mock"
    assert body["cluster_count"] >= 1
