"""Contract tests for content-factory admin router health and ETL status."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api_v2_deps.auth import AuthContext, TokenType, require_admin
from app.api_v2_routers import content_factory
from app.models import UserRole


ADMIN = {"sub": "admin-1", "role": "admin"}


def _admin_context() -> AuthContext:
    return AuthContext(
        user_id=ADMIN["sub"],
        roles=[UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims=ADMIN,
        jti="test-jti",
    )


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(content_factory.router, prefix="/api/v2")
    app.dependency_overrides[require_admin] = _admin_context
    return TestClient(app, raise_server_exceptions=True)


def _unwrap(payload: dict) -> dict:
    return payload.get("data", payload)


@pytest.mark.unit
def test_content_factory_health_returns_ok(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(content_factory, "_generation_enabled", lambda: True)
    client = _client()
    response = client.get("/api/v2/admin/content-factory/health")
    assert response.status_code == 200
    body = _unwrap(response.json())
    assert body["status"] == "ok"
    assert body["route_scope"] == "admin"
    assert body["generation_enabled"] is True


@pytest.mark.unit
def test_content_factory_etl_status_reports_pipeline(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(content_factory, "_mcp_runtime_imported", lambda: False)
    client = _client()
    response = client.get("/api/v2/admin/content-factory/etl/status")
    assert response.status_code == 200
    body = _unwrap(response.json())
    assert body["status"] == "available"
    assert body["pipeline_package"] == "app.services.etl"
    assert any("app.services.etl" in note for note in body["notes"])
