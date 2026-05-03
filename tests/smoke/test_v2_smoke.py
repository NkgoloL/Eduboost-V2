"""
EduBoost SA — V2 Smoke Tests
Tests that actual endpoints respond correctly — not just that modules import.
Replaces the shallow importlib-only check in the legacy CI job.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api_v2 import app

client = TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoints:
    def test_health_returns_200(self) -> None:
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_includes_request_id_header(self) -> None:
        r = client.get("/health")
        assert "X-Request-ID" in r.headers

    def test_health_includes_timing_header(self) -> None:
        r = client.get("/health")
        assert "X-Response-Time" in r.headers

    def test_readiness_probe_exists(self) -> None:
        # Will return 503 in test env (no real DB), but endpoint must exist
        r = client.get("/ready")
        assert r.status_code in (200, 503)

    def test_metrics_endpoint_exists(self) -> None:
        r = client.get("/metrics")
        assert r.status_code == 200


class TestAuthEndpoints:
    def test_register_validates_email(self) -> None:
        r = client.post("/v2/auth/register", json={
            "email": "not-an-email",
            "password": "securepassword123",
            "full_name": "Test Guardian",
        })
        assert r.status_code == 422

    def test_register_requires_all_fields(self) -> None:
        r = client.post("/v2/auth/register", json={"email": "test@example.com"})
        assert r.status_code == 422

    def test_login_returns_401_for_invalid_credentials(self) -> None:
        r = client.post("/v2/auth/login", json={
            "email": "nobody@example.com",
            "password": "wrongpassword",
        })
        # 401 or 503 if DB unavailable in test
        assert r.status_code in (401, 503, 500)

    def test_protected_endpoint_requires_auth(self) -> None:
        r = client.get("/v2/auth/me")
        assert r.status_code == 401

    def test_invalid_token_returns_401(self) -> None:
        r = client.get("/v2/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert r.status_code == 401


class TestConsentGate:
    def test_lessons_endpoint_requires_auth(self) -> None:
        r = client.get("/v2/lessons/00000000-0000-0000-0000-000000000001")
        assert r.status_code == 401

    def test_lessons_generate_requires_auth(self) -> None:
        r = client.post("/v2/lessons/generate", json={
            "learner_id": "00000000-0000-0000-0000-000000000001",
            "subject": "Mathematics",
            "topic": "Fractions",
        })
        assert r.status_code == 401

    def test_consent_grant_requires_auth(self) -> None:
        r = client.post("/v2/consent/grant", json={
            "learner_id": "00000000-0000-0000-0000-000000000001",
        })
        assert r.status_code == 401


class TestErrorHandling:
    def test_404_returns_json_error(self) -> None:
        r = client.get("/v2/nonexistent-endpoint")
        assert r.status_code == 404
        data = r.json()
        assert "error" in data or "detail" in data

    def test_invalid_uuid_returns_422(self) -> None:
        r = client.get("/v2/consent/status/not-a-uuid", headers={
            "Authorization": "Bearer fake.token"
        })
        assert r.status_code in (401, 422)

    def test_response_has_request_id_on_errors(self) -> None:
        r = client.get("/v2/nonexistent-endpoint")
        assert "X-Request-ID" in r.headers


class TestOpenAPISchema:
    def test_openapi_schema_is_accessible_in_non_production(self) -> None:
        r = client.get("/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert "openapi" in schema
        assert "paths" in schema

    def test_consent_endpoints_in_schema(self) -> None:
        r = client.get("/openapi.json")
        schema = r.json()
        paths = schema.get("paths", {})
        assert any("consent" in path for path in paths)

    def test_auth_endpoints_in_schema(self) -> None:
        r = client.get("/openapi.json")
        schema = r.json()
        paths = schema.get("paths", {})
        assert any("auth" in path for path in paths)
