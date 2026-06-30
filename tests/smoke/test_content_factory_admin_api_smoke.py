"""
Admin API smoke tests for Content Factory.
Tests authentication and authorization boundaries for all admin routes.
"""
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.smoke

class TestContentFactoryAdminAPISmoke:
    """Smoke tests for admin Content Factory API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client with app."""
        from app.api_v2 import app
        return TestClient(app)

    @pytest.fixture
    def admin_headers(self):
        """Admin authentication headers."""
        return {"Authorization": "Bear2 test-admin-token"}

    def test_unauthenticated_health_rejected(self, client):
        """Unauthenticated requests to admin health should be rejected."""
        response = client.get("/api/v2/admin/content-factory/health")
        assert response.status_code in (401, 403)

    def test_admin_health_endpoint_exists(self, client):
        """Admin health endpoint should be registered."""
        response = client.get("/api/v2/admin/content-factory/health")
        assert response.status_code != 404

    def test_admin_scopes_endpoint_exists(self, client):
        """Admin scopes endpoint should be registered."""
        response = client.get("/api/v2/admin/content-factory/scopes")
        assert response.status_code != 404

    def test_admin_runs_endpoint_exists(self, client):
        """Admin runs endpoint should be registered."""
        response = client.get("/api/v2/admin/content-factory/runs")
        assert response.status_code != 404

    def test_admin_etl_status_endpoint_exists(self, client):
        """Admin ETL status endpoint should be registered."""
        response = client.get("/api/v2/admin/etl/status")
        assert response.status_code != 404

    def test_openapi_includes_admin_content_factory(self, client):
        """OpenAPI schema should include admin-content-factory tag."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi = response.json()
        paths = openapi.get("paths", {})
        admin_cf_paths = [p for p in paths if "/admin/content-factory" in p]
        assert len(admin_cf_paths) > 0

    def test_no_public_content_factory_in_openapi(self, client):
        """OpenAPI should not expose public content-factory routes."""
        response = client.get("/openapi.json")
        openapi = response.json()
        paths = openapi.get("paths",{})
        public_cf_paths = [
            p for p in paths
            if "/api/v2/content-factory" in p and "/admin" not in p
        ]
        assert len(public_cf_paths) == 0
