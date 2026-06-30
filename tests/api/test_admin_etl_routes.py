import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.core.security import get_current_user

pytestmark = pytest.mark.unit


def _admin_user():
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear(); app.openapi_schema = None
    yield
    app.dependency_overrides.clear(); app.openapi_schema = None


def test_admin_etl_status_requires_admin() -> None:
    assert TestClient(app, raise_server_exceptions=False).get("/api/v2/admin/etl/status").status_code == 401


def test_admin_can_read_etl_status() -> None:
    app.dependency_overrides[get_current_user] = _admin_user
    response = TestClient(app, raise_server_exceptions=False).get("/api/v2/admin/etl/status")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "available"
