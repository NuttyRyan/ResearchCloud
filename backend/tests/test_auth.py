from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["mode"] == "mock"


def test_login_success_and_me(auth_client: TestClient) -> None:
    resp = auth_client.get("/api/auth/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "admin"
    assert body["is_admin"] is True


def test_login_failure(client: TestClient) -> None:
    resp = client.post(
        "/api/auth/login", data={"username": "admin", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_connections_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/connections")
    assert resp.status_code == 401
