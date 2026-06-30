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


def _valid_source() -> dict[str, object]:
    return {
        "source_document_id": "doc-1",
        "source_chunk_id": "chunk-1",
        "curriculum_mapping_id": "map-1",
        "caps_ref": "4.M.1.1",
        "document_status": "approved",
        "license_status": "government_open",
        "chunk_quality_score": 0.9,
    }


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    app.dependency_overrides.clear()
    app.openapi_schema = None
    yield
    app.dependency_overrides.clear()
    app.openapi_schema = None


def test_content_factory_admin_health_requires_authentication() -> None:
    response = _client().get("/api/v2/admin/content-factory/health")

    assert response.status_code == 401


def test_content_factory_admin_health_rejects_non_admin_user() -> None:
    app.dependency_overrides[get_current_user] = _parent_user

    response = _client().get("/api/v2/admin/content-factory/health")

    assert response.status_code == 403


def test_content_factory_admin_health_accepts_admin_user() -> None:
    app.dependency_overrides[get_current_user] = _admin_user

    response = _client().get("/api/v2/admin/content-factory/health")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "ok"
    assert body["data"]["route_scope"] == "admin"
    assert body["data"]["generation_enabled"] is False


def test_validate_artifact_rejects_missing_source_citations() -> None:
    app.dependency_overrides[get_current_user] = _admin_user

    response = _client().post(
        "/api/v2/admin/content-factory/validate-artifact",
        json={
            "artifact_type": "lesson",
            "caps_ref": "4.M.1.1",
            "artifact_json": {"title": "Place value"},
            "sources": [],
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["passed"] is False
    assert "At least one ETL source citation is required." in data["errors"]


def test_validate_artifact_rejects_diagnostic_item_without_answer_key() -> None:
    app.dependency_overrides[get_current_user] = _admin_user

    response = _client().post(
        "/api/v2/admin/content-factory/validate-artifact",
        json={
            "artifact_type": "diagnostic_item",
            "caps_ref": "4.M.1.1",
            "artifact_json": {"stem": "What is 2 + 2?"},
            "sources": [_valid_source()],
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["passed"] is False
    assert any("answer_key" in error for error in data["errors"])


def test_openapi_includes_admin_content_factory_contract() -> None:
    schema = app.openapi()

    tag_names = {tag["name"] for tag in schema["tags"]}
    assert "admin-content-factory" in tag_names
    assert "/api/v2/admin/content-factory/health" in schema["paths"]
    assert "/api/v2/admin/content-factory/scopes" in schema["paths"]
    assert "/api/v2/admin/content-factory/scopes/{scope_id}" in schema["paths"]
    assert "/api/v2/admin/content-factory/scopes/{scope_id}/targets" in schema["paths"]
    assert "/api/v2/admin/content-factory/validate-artifact" in schema["paths"]
    assert "/api/v2/content-factory/health" not in schema["paths"]
