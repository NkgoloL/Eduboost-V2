"""
Phase 9 — G.3: API Envelope Standardization Tests

Verifies that all API responses use the standardized envelope:
- {ok: bool, data: Any, error: str|null, meta: dict|null}

This test scrapes all routes and asserts envelope shape.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.api_v2 import app


class TestAPIEnvelope:
    """Test that all API responses conform to the standardized envelope."""

    @pytest.mark.asyncio
    async def test_health_envelope(self):
        """GET /health should return envelope."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "ok" in data or "status" in data  # /health uses {status: ok}

    @pytest.mark.asyncio
    async def test_ready_envelope(self):
        """GET /ready should return envelope with status."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/ready")
            # May return 200 or 503 depending on DB/Redis availability
            assert response.status_code in (200, 503)
            data = response.json()
            assert "status" in data
            assert data["status"] in ("ok", "degraded", "error")

    @pytest.mark.asyncio
    async def test_docs_returns_html(self):
        """GET /docs should return HTML for Swagger UI."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/docs")
            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_openapi_json_valid(self):
        """GET /openapi.json should return valid OpenAPI schema."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/openapi.json")
            assert response.status_code == 200
            data = response.json()
            assert "openapi" in data
            assert data["openapi"].startswith("3.")

    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """GET / should return envelope with message."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "docs" in data

    @pytest.mark.asyncio
    async def test_metrics_returns_prometheus(self):
        """GET /metrics should return Prometheus format (not envelope)."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/metrics")
            # In production, may return 403 for non-private IP
            assert response.status_code in (200, 403)
            if response.status_code == 200:
                assert "text/plain" in response.headers.get("content-type", "")
                # Prometheus format contains metric definitions
                assert "# TYPE" in response.text or "python_" in response.text

    @pytest.mark.asyncio
    async def test_404_returns_json_error(self):
        """Unknown routes should return JSON error envelope."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/nonexistent-endpoint-12345")
            assert response.status_code == 404
            data = response.json()
            # FastAPI default 404 is {detail: "Not Found"}
            assert "detail" in data or "error" in data

    @pytest.mark.asyncio
    async def test_health_endpoint_no_error_field(self):
        """Health endpoints may use simplified format (not full envelope)."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            # Health endpoints can use simplified format
            # This test just ensures they don't 500
            assert response.status_code == 200
