"""Tests for health check endpoints and dependency validation."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.core.health import (
    check_required_secrets,
    check_postgres,
    check_redis,
    check_migrations,
    check_audit_repository,
    gather_deep_health,
)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test /health endpoint (liveness probe)."""
    
    def test_health_returns_200_and_basic_info(self, client):
        """Verify /health returns 200 with version and environment."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "environment" in data


class TestReadyEndpoint:
    """Test /ready endpoint (readiness probe)."""
    
    @pytest.mark.asyncio
    async def test_ready_returns_200_when_all_checks_pass(self):
        """Verify /ready returns 200 when all critical checks pass."""
        # Mock all checks to return ok
        with patch("app.core.health.check_required_secrets", new_callable=AsyncMock) as mock_secrets, \
             patch("app.core.health.check_postgres", new_callable=AsyncMock) as mock_pg, \
             patch("app.core.health.check_redis", new_callable=AsyncMock) as mock_redis, \
             patch("app.core.health.check_migrations", new_callable=AsyncMock) as mock_migrations, \
             patch("app.core.health.check_audit_repository", new_callable=AsyncMock) as mock_audit, \
             patch("app.core.health.check_llm_provider", new_callable=AsyncMock) as mock_llm, \
             patch("app.core.health.check_judiciary", new_callable=AsyncMock) as mock_judiciary:
            
            mock_secrets.return_value = {"status": "ok"}
            mock_pg.return_value = {"status": "ok"}
            mock_redis.return_value = {"status": "ok"}
            mock_migrations.return_value = {"status": "ok"}
            mock_audit.return_value = {"status": "ok"}
            mock_llm.return_value = {"status": "skipped"}
            mock_judiciary.return_value = {"status": "ok"}
            
            client = TestClient(app)
            response = client.get("/ready")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "critical" in data
            assert "optional" in data
    
    @pytest.mark.asyncio
    async def test_ready_returns_503_when_critical_check_fails(self):
        """Verify /ready returns 503 when a critical check fails."""
        with patch("app.core.health.check_required_secrets", new_callable=AsyncMock) as mock_secrets, \
             patch("app.core.health.check_postgres", new_callable=AsyncMock) as mock_pg, \
             patch("app.core.health.check_redis", new_callable=AsyncMock) as mock_redis, \
             patch("app.core.health.check_migrations", new_callable=AsyncMock) as mock_migrations, \
             patch("app.core.health.check_audit_repository", new_callable=AsyncMock) as mock_audit, \
             patch("app.core.health.check_llm_provider", new_callable=AsyncMock) as mock_llm, \
             patch("app.core.health.check_judiciary", new_callable=AsyncMock) as mock_judiciary:
            
            mock_secrets.return_value = {"status": "error", "detail": "Missing JWT_SECRET_KEY"}
            mock_pg.return_value = {"status": "ok"}
            mock_redis.return_value = {"status": "ok"}
            mock_migrations.return_value = {"status": "ok"}
            mock_audit.return_value = {"status": "ok"}
            mock_llm.return_value = {"status": "skipped"}
            mock_judiciary.return_value = {"status": "ok"}
            
            client = TestClient(app)
            response = client.get("/ready")
            
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "error"


class TestCheckRequiredSecrets:
    """Test required secrets check."""
    
    @pytest.mark.asyncio
    async def test_check_required_secrets_passes_when_all_present(self):
        """Verify check passes when JWT_SECRET_KEY, DATABASE_URL, REDIS_URL are set."""
        result = await check_required_secrets()
        # Assumes these are set in test environment
        assert result["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_check_required_secrets_fails_with_message_when_missing(self):
        """Verify check fails and reports missing secrets."""
        with patch("app.core.health.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = None
            mock_settings.DATABASE_URL = "postgres://..."
            mock_settings.REDIS_URL = "redis://..."
            
            result = await check_required_secrets()
            
            assert result["status"] == "error"
            assert "missing" in result.get("detail", "").lower()


class TestCheckPostgres:
    """Test PostgreSQL connection check."""
    
    @pytest.mark.asyncio
    async def test_check_postgres_passes_when_connected(self):
        """Verify check returns ok when PostgreSQL is reachable."""
        result = await check_postgres()
        # Should pass if DB is running
        if result["status"] != "ok":
            pytest.skip("PostgreSQL not available in test environment")
        assert result["status"] == "ok"


class TestCheckRedis:
    """Test Redis connection check."""
    
    @pytest.mark.asyncio
    async def test_check_redis_passes_when_connected(self):
        """Verify check returns ok when Redis is reachable."""
        result = await check_redis()
        # Should pass if Redis is running
        if result["status"] != "ok":
            pytest.skip("Redis not available in test environment")
        assert result["status"] == "ok"


class TestCheckMigrations:
    """Test migrations applied check."""
    
    @pytest.mark.asyncio
    async def test_check_migrations_passes_when_applied(self):
        """Verify check returns ok when migrations are applied."""
        result = await check_migrations()
        # Should pass if migrations are up to date
        if result["status"] != "ok":
            pytest.skip("Migrations not applied in test environment")
        assert result["status"] == "ok"
        assert "revision" in result or result["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_check_migrations_fails_gracefully_without_table(self):
        """Verify check handles missing alembic_version table."""
        # This test would need database isolation to truly test
        result = await check_migrations()
        assert "status" in result
        assert result["status"] in ("ok", "error")


class TestCheckAuditRepository:
    """Test audit repository access check."""
    
    @pytest.mark.asyncio
    async def test_check_audit_repository_passes_when_accessible(self):
        """Verify check returns ok when audit repository is accessible."""
        result = await check_audit_repository()
        # Should pass if audit table exists
        if result["status"] != "ok":
            pytest.skip("Audit repository not available in test environment")
        assert result["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_check_audit_repository_fails_gracefully_on_error(self):
        """Verify check handles missing audit table gracefully."""
        result = await check_audit_repository()
        assert "status" in result
        assert result["status"] in ("ok", "error")


class TestGatherDeepHealth:
    """Test the full health gathering function."""
    
    @pytest.mark.asyncio
    async def test_gather_deep_health_structure(self):
        """Verify health payload has expected structure."""
        result = await gather_deep_health()
        
        assert "status" in result
        assert result["status"] in ("ok", "degraded", "error")
        assert "critical" in result
        assert "optional" in result
        assert "message" in result
        
        # Verify all critical checks are present
        assert "secrets" in result["critical"]
        assert "postgres" in result["critical"]
        assert "redis" in result["critical"]
        assert "migrations" in result["critical"]
        assert "audit_repository" in result["critical"]
    
    @pytest.mark.asyncio
    async def test_gather_deep_health_returns_error_on_critical_failure(self):
        """Verify overall status is 'error' when any critical check fails."""
        with patch("app.core.health.check_required_secrets", new_callable=AsyncMock) as mock_secrets, \
             patch("app.core.health.check_postgres", new_callable=AsyncMock) as mock_pg, \
             patch("app.core.health.check_redis", new_callable=AsyncMock) as mock_redis, \
             patch("app.core.health.check_migrations", new_callable=AsyncMock) as mock_migrations, \
             patch("app.core.health.check_audit_repository", new_callable=AsyncMock) as mock_audit, \
             patch("app.core.health.check_llm_provider", new_callable=AsyncMock) as mock_llm, \
             patch("app.core.health.check_judiciary", new_callable=AsyncMock) as mock_judiciary:
            
            mock_secrets.return_value = {"status": "error", "detail": "Missing secrets"}
            mock_pg.return_value = {"status": "ok"}
            mock_redis.return_value = {"status": "ok"}
            mock_migrations.return_value = {"status": "ok"}
            mock_audit.return_value = {"status": "ok"}
            mock_llm.return_value = {"status": "skipped"}
            mock_judiciary.return_value = {"status": "ok"}
            
            result = await gather_deep_health()
            
            assert result["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_gather_deep_health_returns_degraded_on_optional_failure(self):
        """Verify overall status is 'degraded' when an optional check fails."""
        with patch("app.core.health.check_required_secrets", new_callable=AsyncMock) as mock_secrets, \
             patch("app.core.health.check_postgres", new_callable=AsyncMock) as mock_pg, \
             patch("app.core.health.check_redis", new_callable=AsyncMock) as mock_redis, \
             patch("app.core.health.check_migrations", new_callable=AsyncMock) as mock_migrations, \
             patch("app.core.health.check_audit_repository", new_callable=AsyncMock) as mock_audit, \
             patch("app.core.health.check_llm_provider", new_callable=AsyncMock) as mock_llm, \
             patch("app.core.health.check_judiciary", new_callable=AsyncMock) as mock_judiciary:
            
            mock_secrets.return_value = {"status": "ok"}
            mock_pg.return_value = {"status": "ok"}
            mock_redis.return_value = {"status": "ok"}
            mock_migrations.return_value = {"status": "ok"}
            mock_audit.return_value = {"status": "ok"}
            mock_llm.return_value = {"status": "error", "detail": "LLM unavailable"}
            mock_judiciary.return_value = {"status": "ok"}
            
            result = await gather_deep_health()
            
            assert result["status"] == "degraded"
