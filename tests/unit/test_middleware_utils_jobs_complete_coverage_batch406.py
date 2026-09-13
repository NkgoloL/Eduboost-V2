from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.jobs import (
    ai_operations_job,
    batch_generation_job,
    consent_renewal_job,
    curriculum_expansion_job,
    irt_quality_job,
    practice_session_cleanup_job,
)
from app.middleware.api_deprecation import APIDeprecationMiddleware, SUNSET_DATE
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.utils.versioning import (
    SemanticVersion,
    VersionChangeType,
    detect_version_change,
    is_same_major_minor,
    requires_manual_renewal,
)


# ── MIDDLEWARE: SECURITY HEADERS ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_security_headers_middleware_development(monkeypatch):
    monkeypatch.setattr(type(settings), "is_production", lambda self: False)

    middleware = SecurityHeadersMiddleware(app=MagicMock())
    req = MagicMock(spec=Request)
    req.state = SimpleNamespace()

    async def call_next(request: Request) -> Response:
        return Response(content="ok", media_type="text/plain")

    res = await middleware.dispatch(req, call_next)

    # Standard headers
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert res.headers["X-XSS-Protection"] == "1; mode=block"
    assert res.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "Permissions-Policy" in res.headers

    # Dev CSP
    assert "unsafe-inline" in res.headers["Content-Security-Policy"]
    assert "Strict-Transport-Security" not in res.headers
    assert hasattr(req.state, "csp_nonce")


@pytest.mark.asyncio
async def test_security_headers_middleware_production(monkeypatch):
    monkeypatch.setattr(type(settings), "is_production", lambda self: True)

    middleware = SecurityHeadersMiddleware(app=MagicMock())
    req = MagicMock(spec=Request)
    req.state = SimpleNamespace()

    async def call_next(request: Request) -> Response:
        return Response(content="ok", media_type="text/plain")

    res = await middleware.dispatch(req, call_next)

    # Production HSTS & CSP
    assert "Strict-Transport-Security" in res.headers
    assert "max-age=31536000" in res.headers["Strict-Transport-Security"]
    assert "report-uri /api/v2/csp-report" in res.headers["Content-Security-Policy"]
    assert f"nonce-{req.state.csp_nonce}" in res.headers["Content-Security-Policy"]
    assert "unsafe-inline" not in res.headers["Content-Security-Policy"]


# ── MIDDLEWARE: API DEPRECATION ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_api_deprecation_middleware():
    middleware = APIDeprecationMiddleware(app=MagicMock())

    async def call_next(request: Request) -> Response:
        return Response(content="ok", media_type="text/plain")

    # 1. Canonical route - no deprecation headers
    req_canonical = MagicMock(spec=Request)
    req_canonical.url = SimpleNamespace(path="/api/v2/items")
    res1 = await middleware.dispatch(req_canonical, call_next)
    assert "Deprecation" not in res1.headers
    assert "Sunset" not in res1.headers

    # 2. Legacy /v2/items route - deprecation headers added
    req_legacy = MagicMock(spec=Request)
    req_legacy.url = SimpleNamespace(path="/v2/items")
    res2 = await middleware.dispatch(req_legacy, call_next)
    assert res2.headers.get("Deprecation") == "@1793491200"
    assert res2.headers.get("Sunset") == SUNSET_DATE
    assert res2.headers.get("Link") == '</api/v2/items>; rel="canonical"'
    assert res2.headers.get("X-API-Canonical-Prefix") == "/api/v2"

    # 3. Exact /v2 route
    req_exact = MagicMock(spec=Request)
    req_exact.url = SimpleNamespace(path="/v2")
    res3 = await middleware.dispatch(req_exact, call_next)
    assert res3.headers.get("Deprecation") == "@1793491200"
    assert res3.headers.get("Link") == '</api/v2>; rel="canonical"'


# ── UTILS: VERSIONING ─────────────────────────────────────────────────────────


def test_versioning_complete():
    # 1. Parse valid versions
    v_123 = SemanticVersion.parse("1.2.3")
    assert v_123.major == 1
    assert v_123.minor == 2
    assert v_123.patch == 3
    assert str(v_123) == "1.2.3"

    # 2. Parse invalid versions
    with pytest.raises(ValueError, match="Invalid version format"):
        SemanticVersion.parse("1.2")
    with pytest.raises(ValueError, match="Invalid version format"):
        SemanticVersion.parse("1.2.3.4")
    with pytest.raises(ValueError, match="Invalid version numbers"):
        SemanticVersion.parse("1.x.3")

    # 3. Comparison branches: major, minor, patch diffs and equality
    v_200 = SemanticVersion(2, 0, 0)
    assert v_123.compare(v_200) == -1
    assert v_200.compare(v_123) == 1

    v_113 = SemanticVersion(1, 1, 3)
    assert v_123.compare(v_113) == 1
    assert v_113.compare(v_123) == -1

    v_124 = SemanticVersion(1, 2, 4)
    assert v_124.compare(v_123) == 1
    assert v_123.compare(v_124) == -1
    assert v_123.compare(SemanticVersion(1, 2, 3)) == 0

    # 4. Equality and Inequality with non-SemanticVersion
    assert (v_123 == "1.2.3") is False
    assert (v_123 != "1.2.3") is True
    assert (v_123 == 42) is False
    assert (v_123 != 42) is True
    assert (v_123 == SemanticVersion(1, 2, 3)) is True
    assert (v_123 != SemanticVersion(1, 2, 4)) is True

    # 5. Operators: <, <=, >, >=
    assert (v_113 < v_123) is True
    assert (v_123 < v_113) is False
    assert (v_123 <= SemanticVersion(1, 2, 3)) is True
    assert (v_113 <= v_123) is True
    assert (v_123 > v_113) is True
    assert (v_113 > v_123) is False
    assert (v_123 >= SemanticVersion(1, 2, 3)) is True
    assert (v_124 >= v_123) is True

    # 6. Change type detection
    assert v_123.detect_change_type(SemanticVersion(2, 0, 0)) == VersionChangeType.MAJOR
    assert v_123.detect_change_type(SemanticVersion(1, 3, 0)) == VersionChangeType.MINOR
    assert v_123.detect_change_type(SemanticVersion(1, 2, 4)) == VersionChangeType.PATCH

    assert detect_version_change("1.0.0", "2.0.0") == VersionChangeType.MAJOR
    assert detect_version_change("1.0.0", "1.1.0") == VersionChangeType.MINOR
    assert detect_version_change("1.0.0", "1.0.1") == VersionChangeType.PATCH

    # 7. Renewal requirements
    assert requires_manual_renewal("1.0.0", "2.0.0") is True
    assert requires_manual_renewal("1.0.0", "1.1.0") is True
    assert requires_manual_renewal("1.0.0", "1.0.1") is False

    # 8. Major/Minor equivalence
    assert is_same_major_minor("1.2.0", "1.2.5") is True
    assert is_same_major_minor("1.2.0", "1.3.0") is False
    assert is_same_major_minor("1.2.0", "2.2.0") is False


# ── JOBS: AI_OPERATIONS ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_jobs_ai_operations(monkeypatch):
    mock_db = AsyncMock()
    mock_db.__aenter__.return_value = mock_db
    mock_db.__aexit__.return_value = None

    monkeypatch.setattr(ai_operations_job, "AsyncSessionLocal", lambda: mock_db)

    mock_svc = MagicMock()
    mock_svc.expire_stale = AsyncMock(return_value=5)
    monkeypatch.setattr(ai_operations_job, "AIOperationsService", lambda db: mock_svc)

    res = await ai_operations_job.expire_ai_usage_reservations()
    assert res == {"expired_reservations": 5}


# ── JOBS: CURRICULUM_EXPANSION ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_jobs_curriculum_expansion(monkeypatch):
    mock_db = AsyncMock()
    mock_db.__aenter__.return_value = mock_db
    mock_db.__aexit__.return_value = None

    monkeypatch.setattr(curriculum_expansion_job, "AsyncSessionLocal", lambda: mock_db)

    mock_registry = MagicMock()
    mock_scope = SimpleNamespace(scope_id="scope_math")
    mock_registry.list_active_scopes.return_value = [mock_scope]
    monkeypatch.setattr(curriculum_expansion_job, "ContentScopeRegistry", lambda: mock_registry)

    mock_svc = MagicMock()
    mock_svc.capture_snapshot = AsyncMock()
    monkeypatch.setattr(curriculum_expansion_job, "CurriculumExpansionService", lambda db, registry: mock_svc)

    res = await curriculum_expansion_job.capture_weekly_curriculum_coverage()
    assert res == {"snapshots_created": 1}
    mock_svc.capture_snapshot.assert_awaited_once_with("scope_math", None)


# ── JOBS: IRT_QUALITY ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_jobs_irt_quality(monkeypatch):
    mock_db = AsyncMock()
    mock_db.__aenter__.return_value = mock_db
    mock_db.__aexit__.return_value = None

    monkeypatch.setattr(irt_quality_job, "AsyncSessionLocal", lambda: mock_db)

    item_id = str(uuid4())
    mock_svc = MagicMock()
    mock_svc.run = AsyncMock(return_value={"status": "calibrated", "items_processed": 1})
    monkeypatch.setattr(irt_quality_job, "IRTQualityService", lambda: mock_svc)

    async def run_durable(job_id, fn):
        return await fn()

    with patch("app.modules.jobs._execute_durable_job", side_effect=run_durable):
        res = await irt_quality_job.run_irt_quality_watchdog(
            job_id="job_irt_01",
            item_ids=[item_id],
            idempotency_key="idemp_irt_01",
        )
        assert res["status"] == "calibrated"


# ── JOBS: BATCH_GENERATION ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_jobs_batch_generation(monkeypatch):
    mock_db = AsyncMock()
    mock_db.__aenter__.return_value = mock_db
    mock_db.__aexit__.return_value = None

    monkeypatch.setattr(batch_generation_job, "AsyncSessionFactory", lambda: mock_db)
    monkeypatch.setattr(batch_generation_job, "build_provider_router", lambda s: MagicMock())

    run_id = str(uuid4())
    mock_engine = MagicMock()
    mock_result = SimpleNamespace(
        succeeded=5,
        failed=0,
        safety_blocked=0,
        skipped=0,
        total_tasks=5,
    )
    mock_engine.process_run = AsyncMock(return_value=mock_result)
    monkeypatch.setattr(batch_generation_job, "BatchGenerationEngine", lambda provider_router: mock_engine)

    ctx = {"job_id": "arq_001"}
    res = await batch_generation_job.generate_content_batch(ctx, run_id, job_id="job_batch_01")
    assert res["run_id"] == run_id
    assert res["succeeded"] == 5
    assert res["total_tasks"] == 5


# ── JOBS: CONSENT_RENEWAL ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_jobs_consent_renewal(monkeypatch):
    mock_db = AsyncMock()
    mock_db.__aenter__.return_value = mock_db
    mock_db.__aexit__.return_value = None

    mock_svc = MagicMock()
    mock_svc.run = AsyncMock(return_value={"reminders_sent": 3})

    mock_update_job = AsyncMock()
    monkeypatch.setattr(consent_renewal_job, "update_job", mock_update_job)

    with (
        patch("app.services.consent_renewal_service.ConsentRenewalService", return_value=mock_svc),
        patch("app.services.consent_renewal_service.SendGridEmailGateway", return_value=MagicMock()),
    ):
        ctx = {"db_session_factory": lambda: mock_db}

        # 1. Success with job_id
        res = await consent_renewal_job.run_consent_renewal_reminders(ctx=ctx, job_id="job_consent_01")
        assert res == {"reminders_sent": 3}
        mock_update_job.assert_any_await("job_consent_01", status="running")
        mock_update_job.assert_any_await("job_consent_01", status="completed", result={"reminders_sent": 3})

        # 2. Failure with job_id
        mock_svc.run = AsyncMock(side_effect=RuntimeError("Email failure"))
        with pytest.raises(RuntimeError):
            await consent_renewal_job.run_consent_renewal_reminders(ctx=ctx, job_id="job_consent_02")
        mock_update_job.assert_any_await(
            "job_consent_02",
            status="failed",
            error={"type": "RuntimeError", "message": "Email failure"},
        )

        # 3. Success without job_id and ctx=None
        monkeypatch.setattr(consent_renewal_job, "AsyncSessionLocal", lambda: mock_db)
        mock_svc.run = AsyncMock(return_value={"reminders_sent": 1})
        res_no_job = await consent_renewal_job.run_consent_renewal_reminders(ctx=None, job_id=None)
        assert res_no_job == {"reminders_sent": 1}

        # 4. Failure without job_id
        mock_svc.run = AsyncMock(side_effect=ValueError("No job failure"))
        with pytest.raises(ValueError):
            await consent_renewal_job.run_consent_renewal_reminders(ctx=None, job_id=None)


# ── JOBS: PRACTICE_SESSION_CLEANUP ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_jobs_practice_session_cleanup(monkeypatch):
    mock_db = AsyncMock()
    mock_db.__aenter__.return_value = mock_db
    mock_db.__aexit__.return_value = None

    mock_repo = MagicMock()
    mock_repo.delete_expired = AsyncMock(return_value=12)

    mock_update_job = AsyncMock()
    monkeypatch.setattr(practice_session_cleanup_job, "update_job", mock_update_job)

    with patch("app.repositories.practice_session_repository.PracticeSessionRepository", return_value=mock_repo):
        ctx = {"db_session_factory": lambda: mock_db}

        # 1. Success with job_id
        res = await practice_session_cleanup_job.run_practice_session_cleanup(ctx=ctx, job_id="job_practice_01")
        assert res == {"deleted_count": 12}
        mock_update_job.assert_any_await("job_practice_01", status="running")
        mock_update_job.assert_any_await("job_practice_01", status="completed", result={"deleted_count": 12})

        # 2. Failure with job_id
        mock_repo.delete_expired = AsyncMock(side_effect=RuntimeError("DB lock timeout"))
        with pytest.raises(RuntimeError):
            await practice_session_cleanup_job.run_practice_session_cleanup(ctx=ctx, job_id="job_practice_02")
        mock_update_job.assert_any_await(
            "job_practice_02",
            status="failed",
            error={"type": "RuntimeError", "message": "DB lock timeout"},
        )

        # 3. Success without job_id and ctx=None
        monkeypatch.setattr(practice_session_cleanup_job, "AsyncSessionLocal", lambda: mock_db)
        mock_repo.delete_expired = AsyncMock(return_value=4)
        res_no_job = await practice_session_cleanup_job.run_practice_session_cleanup(ctx=None, job_id=None)
        assert res_no_job == {"deleted_count": 4}

        # 4. Failure without job_id
        mock_repo.delete_expired = AsyncMock(side_effect=ValueError("No job failure"))
        with pytest.raises(ValueError):
            await practice_session_cleanup_job.run_practice_session_cleanup(ctx=None, job_id=None)
