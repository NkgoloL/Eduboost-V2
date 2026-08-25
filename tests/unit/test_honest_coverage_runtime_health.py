from __future__ import annotations

import pytest

from app.core import health


@pytest.mark.asyncio
async def test_required_secrets_reports_missing_and_present_settings(monkeypatch) -> None:
    monkeypatch.setattr(health.settings, "JWT_SECRET", "")
    monkeypatch.setattr(health.settings, "DATABASE_URL", "", raising=False)
    monkeypatch.setattr(health.settings, "REDIS_URL", "", raising=False)

    missing = await health.check_required_secrets()

    assert missing["status"] == "error"
    assert "JWT_SECRET" in missing["detail"]
    assert "DATABASE_URL" in missing["detail"]
    assert "REDIS_URL" in missing["detail"]

    monkeypatch.setattr(health.settings, "JWT_SECRET", "secret")
    monkeypatch.setattr(health.settings, "DATABASE_URL", "postgresql://example")
    monkeypatch.setattr(health.settings, "REDIS_URL", "redis://example")

    assert await health.check_required_secrets() == {"status": "ok"}


@pytest.mark.asyncio
async def test_llm_provider_check_skips_without_credentials_and_sanitizes_failures(monkeypatch) -> None:
    monkeypatch.setattr(health.settings, "GOOGLE_API_KEY", "", raising=False)
    monkeypatch.setattr(health.settings, "GROQ_API_KEY", "", raising=False)
    monkeypatch.setattr(health.settings, "ANTHROPIC_API_KEY", "", raising=False)

    skipped = await health.check_llm_provider()

    assert skipped == {
        "status": "skipped",
        "detail": "No LLM provider credentials configured",
    }

    class FailingClient:
        def __init__(self, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, *_args, **_kwargs):
            raise RuntimeError("secret token must not leak")

    monkeypatch.setattr(health.settings, "GOOGLE_API_KEY", "google-key", raising=False)
    monkeypatch.setattr(health.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(health.httpx, "AsyncClient", FailingClient)

    result = await health.check_llm_provider()

    assert result == {
        "status": "error",
        "provider": "google",
        "detail": "RuntimeError",
    }


@pytest.mark.asyncio
async def test_gather_deep_health_separates_critical_failure_from_optional_degradation(monkeypatch) -> None:
    async def ok():
        return {"status": "ok"}

    async def skipped():
        return {"status": "skipped"}

    async def error():
        return {"status": "error", "detail": "RuntimeError"}

    calls: list[tuple[tuple[str, str], int]] = []

    class Gauge:
        def labels(self, **labels):
            self._labels = (labels["component"], labels["criticality"])
            return self

        def set(self, value: int) -> None:
            calls.append((self._labels, value))

    monkeypatch.setattr(health, "check_required_secrets", ok)
    monkeypatch.setattr(health, "check_postgres", ok)
    monkeypatch.setattr(health, "check_redis", ok)
    monkeypatch.setattr(health, "check_migrations", ok)
    monkeypatch.setattr(health, "check_schema_contract", ok)
    monkeypatch.setattr(health, "check_audit_repository", ok)
    monkeypatch.setattr(health, "check_llm_provider", error)
    monkeypatch.setattr(health, "check_judiciary", skipped)

    import app.core.metrics as metrics

    monkeypatch.setattr(metrics, "readiness_component_status", Gauge())

    degraded = await health.gather_deep_health()

    assert degraded["status"] == "degraded"
    assert degraded["message"] == "System is operational but in degraded mode"
    assert (("llm_provider", "optional"), 0) in calls
    assert (("judiciary", "optional"), 1) in calls

    monkeypatch.setattr(health, "check_postgres", error)
    unavailable = await health.gather_deep_health()

    assert unavailable["status"] == "error"
    assert unavailable["message"] == "System is unavailable"
