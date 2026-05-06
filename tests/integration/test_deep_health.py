from fastapi.testclient import TestClient

from app.api_v2 import app


def test_deep_health_returns_ok_when_checks_pass(monkeypatch):
    async def fake_health():
        return {
            "status": "ok",
            "components": {
                "postgres": {"status": "ok"},
                "redis": {"status": "ok"},
                "llm_provider": {"status": "ok"},
                "judiciary": {"status": "ok"},
            },
        }

    monkeypatch.setattr("app.api_v2.gather_deep_health", fake_health)

    with TestClient(app) as client:
        response = client.get("/api/v2/health/deep")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_deep_health_returns_503_when_critical_component_fails(monkeypatch):
    async def fake_health():
        return {
            "status": "error",
            "components": {
                "postgres": {"status": "error", "detail": "down"},
                "redis": {"status": "ok"},
                "llm_provider": {"status": "ok"},
                "judiciary": {"status": "ok"},
            },
        }

    monkeypatch.setattr("app.api_v2.gather_deep_health", fake_health)

    with TestClient(app) as client:
        response = client.get("/api/v2/health/deep")

    assert response.status_code == 503
    assert response.json()["components"]["postgres"]["status"] == "error"
