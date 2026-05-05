import pytest
from fastapi.testclient import TestClient
from app.api_v2 import app

client = TestClient(app)

def test_ready_endpoint_success(monkeypatch):
    # Mock deep health to return ok status
    async def mock_gather_deep_health():
        return {
            "status": "ok",
            "critical": {"postgres": {"status": "ok"}, "redis": {"status": "ok"}},
            "optional": {"llm_provider": {"status": "ok"}, "judiciary": {"status": "ok"}},
            "message": "System is operational"
        }
    monkeypatch.setattr("app.core.health.gather_deep_health", mock_gather_deep_health)
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "critical" in data
    assert "optional" in data

def test_ready_endpoint_degraded(monkeypatch):
    # Mock deep health to return degraded status (optional component fails)
    async def mock_gather_deep_health():
        return {
            "status": "degraded",
            "critical": {"postgres": {"status": "ok"}, "redis": {"status": "ok"}},
            "optional": {"llm_provider": {"status": "error", "detail": "provider timeout"}, "judiciary": {"status": "ok"}},
            "message": "System is operational but in degraded mode"
        }
    monkeypatch.setattr("app.core.health.gather_deep_health", mock_gather_deep_health)
    response = client.get("/ready")
    assert response.status_code == 200 # Degraded still returns 200 for readiness
    data = response.json()
    assert data["status"] == "degraded"
    assert data["optional"]["llm_provider"]["status"] == "error"

def test_ready_endpoint_failure(monkeypatch):
    # Mock deep health to return error status (critical component fails)
    async def mock_gather_deep_health():
        return {
            "status": "error",
            "critical": {"postgres": {"status": "error", "detail": "db down"}, "redis": {"status": "ok"}},
            "optional": {"llm_provider": {"status": "ok"}, "judiciary": {"status": "ok"}},
            "message": "System is unavailable"
        }
    monkeypatch.setattr("app.core.health.gather_deep_health", mock_gather_deep_health)
    response = client.get("/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "error"
    assert data["critical"]["postgres"]["status"] == "error"
