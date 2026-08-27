"""Unit tests for API Deprecation Middleware & Canonical Routing (TSR-10)."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.api_deprecation import APIDeprecationMiddleware, SUNSET_DATE


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(APIDeprecationMiddleware)

    @app.get("/api/v2/health")
    async def canonical_health():
        return {"status": "ok", "canonical": True}

    @app.get("/v2/health")
    async def legacy_health():
        return {"status": "ok", "canonical": False}

    return app


@pytest.mark.unit
def test_canonical_route_has_no_deprecation_headers(test_app: FastAPI):
    client = TestClient(test_app)
    response = client.get("/api/v2/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "canonical": True}
    assert "Deprecation" not in response.headers
    assert "Sunset" not in response.headers


@pytest.mark.unit
def test_legacy_route_receives_deprecation_and_canonical_link_headers(test_app: FastAPI):
    client = TestClient(test_app)
    response = client.get("/v2/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "canonical": False}
    assert response.headers.get("Deprecation") == "@1730419200"
    assert response.headers.get("Sunset") == SUNSET_DATE
    assert response.headers.get("X-API-Canonical-Prefix") == "/api/v2"
    assert response.headers.get("Link") == '</api/v2/health>; rel="canonical"'
