import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_deps.auth import get_auth_context, AuthContext
from app.core.security import get_current_user
from app.models import UserRole

pytestmark = pytest.mark.unit


def _admin_auth_context():
    return AuthContext(
        user_id=str(uuid.uuid4()),
        roles=[UserRole.ADMIN],
        token_type="access",
        raw_claims={"sub": str(uuid.uuid4()), "role": "admin", "type": "access"},
        jti=str(uuid.uuid4()),
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear(); app.openapi_schema = None  # noqa: E702
    yield
    app.dependency_overrides.clear(); app.openapi_schema = None  # noqa: E702


def test_admin_etl_status_requires_admin() -> None:
    assert TestClient(app, raise_server_exceptions=False).get("/api/v2/admin/etl/status").status_code == 401


def test_admin_can_read_etl_status() -> None:
    app.dependency_overrides[get_auth_context] = _admin_auth_context
    response = TestClient(app, raise_server_exceptions=False).get("/api/v2/admin/etl/status")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "available"
