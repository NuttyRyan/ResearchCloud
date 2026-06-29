from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator

import pytest

# Configure an isolated SQLite DB and force mock mode BEFORE app modules load.
_tmpdir = tempfile.mkdtemp(prefix="rc-test-")
os.environ["RC_DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"
os.environ["RC_FORCE_MOCK_NUTANIX"] = "true"
os.environ["RC_SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient  # noqa: E402

from app.bootstrap import init_db  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.nutanix.mock import reset_mock_store  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_state() -> Iterator[None]:
    Base.metadata.drop_all(bind=engine)
    init_db()
    reset_mock_store()
    yield


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_client(client: TestClient) -> TestClient:
    resp = client.post(
        "/api/auth/login", data={"username": "admin", "password": "admin"}
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
