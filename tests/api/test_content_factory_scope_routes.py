from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.core.security import get_current_user


pytestmark = pytest.mark.unit


def _client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def _admin_user() -> dict[str, str]:
    return {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"}


def _parent_user() -> dict[str, str]:
    return {"sub": str(uuid.uuid4()), "role": "parent", "type": "access"}


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    app.dependency_overrides.clear()
    app.openapi_schema = None
    yield
    app.dependency_overrides.clear()
    app.openapi_schema = None


def test_content_scope_list_requires_authentication() -> None:
    response = _client().get("/api/v2/admin/content-factory/scopes")

    assert response.status_code == 401


def test_content_scope_list_rejects_non_admin_user() -> None:
    app.dependency_overrides[get_current_user] = _parent_user

    response = _client().get("/api/v2/admin/content-factory/scopes")

    assert response.status_code == 403


def test_admin_can_list_content_scopes() -> None:
    app.dependency_overrides[get_current_user] = _admin_user

    response = _client().get("/api/v2/admin/content-factory/scopes")

    assert response.status_code == 200
    scopes = response.json()["data"]
    assert [scope["scope_id"] for scope in scopes] == ["grade4_mathematics_en"]


def test_admin_can_fetch_grade4_mathematics_scope() -> None:
    app.dependency_overrides[get_current_user] = _admin_user

    response = _client().get("/api/v2/admin/content-factory/scopes/grade4_mathematics_en")

    assert response.status_code == 200
    scope = response.json()["data"]
    assert scope["grade"] == 4
    assert scope["subject"] == "Mathematics"
    assert scope["caps_refs"] == ["4.M.1.1", "4.M.1.2", "4.M.1.3"]


def test_admin_can_fetch_content_scope_targets() -> None:
    app.dependency_overrides[get_current_user] = _admin_user

    response = _client().get("/api/v2/admin/content-factory/scopes/grade4_mathematics_en/targets")

    assert response.status_code == 200
    targets = response.json()["data"]
    assert len(targets) == 3
    assert targets[0]["caps_ref"] == "4.M.1.1"
    assert targets[0]["targets"]["diagnostic_items.approved"] == 40
    assert targets[0]["targets"]["lessons.approved"] == 8


def test_unknown_content_scope_returns_404() -> None:
    app.dependency_overrides[get_current_user] = _admin_user

    response = _client().get("/api/v2/admin/content-factory/scopes/unknown_scope")

    assert response.status_code == 404
