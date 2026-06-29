from __future__ import annotations

from fastapi.testclient import TestClient


def _create_blueprint(client: TestClient, name: str = "data-science", os: str = "Ubuntu 22.04"):
    return client.post(
        "/api/blueprints",
        json={
            "name": name,
            "description": "DS workstation",
            "os": os,
            "num_vcpus": 4,
            "memory_gib": 16,
            "apps": [
                {"name": "docker", "method": "URL", "url": "https://get.docker.com"},
                {"name": "jupyter", "method": "INLINE", "script": "pip install jupyterlab"},
            ],
        },
    )


def test_create_blueprint_generates_bash_and_dsl(auth_client: TestClient) -> None:
    resp = _create_blueprint(auth_client)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["platform"] == "linux"
    assert body["install_script"].startswith("#!/usr/bin/env bash")
    assert "https://get.docker.com" in body["install_script"]
    assert "pip install jupyterlab" in body["install_script"]
    assert "class DataScienceBlueprint(Blueprint)" in body["calm_dsl"]
    assert "CalmTask.Exec.ssh" in body["calm_dsl"]


def test_windows_blueprint_generates_powershell(auth_client: TestClient) -> None:
    resp = _create_blueprint(auth_client, name="win-app", os="Windows Server 2022")
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["platform"] == "windows"
    assert "PowerShell" in body["install_script"]
    assert "Invoke-WebRequest" in body["install_script"]
    assert "CalmTask.Exec.powershell" in body["calm_dsl"]


def test_blueprint_duplicate_rejected(auth_client: TestClient) -> None:
    _create_blueprint(auth_client)
    resp = _create_blueprint(auth_client)
    assert resp.status_code == 409


def test_runbook_from_blueprint_and_list(auth_client: TestClient) -> None:
    bp_id = _create_blueprint(auth_client).json()["id"]
    resp = auth_client.post(
        f"/api/blueprints/{bp_id}/runbook",
        json={"name": "ds-setup", "description": "repeatable DS setup"},
    )
    assert resp.status_code == 201, resp.text
    runbook = resp.json()
    assert runbook["source_blueprint_id"] == bp_id
    assert "get.docker.com" in runbook["script"]

    names = [r["name"] for r in auth_client.get("/api/runbooks").json()]
    assert "ds-setup" in names


def test_standalone_runbook_crud(auth_client: TestClient) -> None:
    created = auth_client.post(
        "/api/runbooks",
        json={"name": "patch", "os": "Ubuntu 22.04", "script": "apt-get update -y"},
    )
    assert created.status_code == 201, created.text
    rb_id = created.json()["id"]
    assert auth_client.get(f"/api/runbooks/{rb_id}").json()["script"] == "apt-get update -y"
    assert auth_client.delete(f"/api/runbooks/{rb_id}").status_code == 204


def test_blueprints_require_auth(client: TestClient) -> None:
    assert client.get("/api/blueprints").status_code == 401
