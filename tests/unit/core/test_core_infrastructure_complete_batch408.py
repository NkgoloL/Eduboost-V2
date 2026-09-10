from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from enum import Enum
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest
from fastapi import BackgroundTasks, HTTPException, Request, Response
from slowapi.errors import RateLimitExceeded

from app.core import (
    analytics,
    arq_worker,
    audit,
    context,
    degraded_mode,
    jobs,
    logging as core_logging,
    providers,
    rate_limit,
    rate_limiter,
    redis as core_redis,
    stripe_client,
)
from app.core.config import settings


# ── 1. RATE_LIMITER ───────────────────────────────────────────────────────────


def test_rate_limiter_calculations():
    now = datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc)
    seconds = rate_limiter.seconds_until_tomorrow(now)
    assert seconds == 12 * 3600

    decision = rate_limiter.QuotaDecision(key="k1", used=10, limit=5, retry_after=3600)
    exc = rate_limiter.AIQuotaExceeded(decision)
    assert exc.status_code == 429
    assert exc.headers["Retry-After"] == "3600"


@pytest.mark.asyncio
async def test_check_ai_quota():
    # Premium tier bypasses redis
    dec_prem = await rate_limiter.check_ai_quota("u_prem", tier="premium")
    assert dec_prem.key == ""
    assert dec_prem.limit == settings.PREMIUM_DAILY_REQUEST_QUOTA

    # Free tier under limit
    with patch("app.core.rate_limiter.increment_counter", new_callable=AsyncMock) as mock_incr:
        mock_incr.return_value = 5
        dec_free = await rate_limiter.check_ai_quota("u_free", tier="free")
        assert dec_free.used == 5
        assert dec_free.limit == settings.FREE_DAILY_REQUEST_QUOTA

    # Free tier exceeded limit
    with patch("app.core.rate_limiter.increment_counter", new_callable=AsyncMock) as mock_incr:
        mock_incr.return_value = settings.FREE_DAILY_REQUEST_QUOTA + 1
        with pytest.raises(rate_limiter.AIQuotaExceeded):
            await rate_limiter.check_ai_quota("u_free_exceeded", tier="free")


# ── 2. RATE_LIMIT ─────────────────────────────────────────────────────────────


def test_rate_limit_helpers():
    # _get_account_key with authenticated user
    req_auth = MagicMock(spec=Request)
    req_auth.state = SimpleNamespace(current_user=SimpleNamespace(user_id="user_123"))
    assert rate_limit._get_account_key(req_auth) == "account:user_123"

    # _get_account_key fallback to IP
    req_anon = MagicMock(spec=Request)
    req_anon.state = SimpleNamespace(current_user=None)
    req_anon.client = SimpleNamespace(host="192.168.1.1")
    assert rate_limit._get_account_key(req_anon) == "192.168.1.1"

    # risk_limit
    req_risky = MagicMock(spec=Request)
    req_risky.state = SimpleNamespace(failed_auth_count=3)
    assert rate_limit.risk_limit(req_risky) == "3/minute"

    req_safe = MagicMock(spec=Request)
    req_safe.state = SimpleNamespace(failed_auth_count=1)
    assert rate_limit.risk_limit(req_safe) == rate_limit.LOGIN_LIMIT

    # rate_limit_exceeded_handler
    exc = MagicMock(spec=RateLimitExceeded)
    exc.detail = "10/minute"
    resp = rate_limit.rate_limit_exceeded_handler(req_safe, exc)
    assert resp.status_code == 429


# ── 3. CONTEXT ────────────────────────────────────────────────────────────────


def test_context_request_id():
    context.clear_request_id()
    assert context.get_request_id() == "unknown"
    assert context.get_request_id("fallback_id") == "fallback_id"

    context.set_request_id("req_abc_123")
    assert context.get_request_id() == "req_abc_123"

    context.set_request_id(None)
    assert context.get_request_id() == "unknown"

    # Exception tolerance during set/clear
    mock_var = MagicMock()
    mock_var.set.side_effect = Exception("Context error")
    with patch("app.core.context._request_id_var", mock_var):
        context.set_request_id(None)
        context.clear_request_id()


# ── 4. REDIS ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_redis_wrapper():
    mock_redis = AsyncMock()
    core_redis._pool = mock_redis

    # get_redis uses cached pool
    assert core_redis.get_redis() is mock_redis

    # cache_set
    await core_redis.cache_set("key1", "val1", ttl=60)
    mock_redis.set.assert_awaited_once_with("key1", "val1", ex=60)

    # cache_get
    mock_redis.get.return_value = "val1"
    assert await core_redis.cache_get("key1") == "val1"

    # cache_delete
    await core_redis.cache_delete("key1")
    mock_redis.delete.assert_awaited_once_with("key1")

    # cache_delete_pattern: empty
    async def empty_scan(match):
        if False:
            yield None

    mock_redis.scan_iter = empty_scan
    assert await core_redis.cache_delete_pattern("prefix:*") == 0

    # cache_delete_pattern: with keys
    async def keys_scan(match):
        yield "prefix:1"
        yield "prefix:2"

    mock_redis.scan_iter = keys_scan
    mock_redis.delete.return_value = 2
    assert await core_redis.cache_delete_pattern("prefix:*") == 2

    # increment_counter
    pipe = MagicMock()
    pipe.execute = AsyncMock(return_value=[7, True])
    mock_redis.pipeline = MagicMock(return_value=pipe)
    res = await core_redis.increment_counter("counter_key", ttl_seconds=3600)
    assert res == 7
    pipe.incr.assert_called_once_with("counter_key")
    pipe.expire.assert_called_once_with("counter_key", 3600)


# ── 5. DEGRADED_MODE ──────────────────────────────────────────────────────────


def test_degraded_mode_capabilities(monkeypatch):
    cap = degraded_mode.RuntimeCapability(
        name="test_cap",
        status="available",
        criticality="optional",
        fallback="Do nothing",
        reason="",
    )
    assert cap.to_dict()["name"] == "test_cap"

    # All providers enabled
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "test_key")
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test")
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setattr(settings, "STRIPE_PRICE_ID_PREMIUM", "price_test")
    monkeypatch.setattr(settings, "SENDGRID_API_KEY", "sg_test")
    monkeypatch.setattr(settings, "SENDGRID_FROM_EMAIL", "test@eduboost.co.za")
    monkeypatch.setattr(settings, "POSTHOG_API_KEY", "ph_test")

    payload_ok = degraded_mode.capabilities_payload()
    assert payload_ok["status"] == "ok"
    assert payload_ok["degraded_capabilities"] == []

    # Providers disabled
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", None)
    monkeypatch.setattr(settings, "GROQ_API_KEY", None)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", None)
    monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", None)
    monkeypatch.setattr(settings, "SENDGRID_API_KEY", None)
    monkeypatch.setattr(settings, "POSTHOG_API_KEY", None)

    payload_deg = degraded_mode.capabilities_payload()
    assert payload_deg["status"] == "degraded"
    assert "llm_generation" in payload_deg["degraded_capabilities"]
    assert "billing" in payload_deg["degraded_capabilities"]

    # require_optional_capability raises 503 when degraded
    with pytest.raises(HTTPException) as exc:
        degraded_mode.require_optional_capability("llm_generation")
    assert exc.value.status_code == 503

    # require_optional_capability returns capability when available
    monkeypatch.setattr(settings, "LLM_PROVIDER", "mock")
    cap_llm = degraded_mode.require_optional_capability("llm_generation")
    assert cap_llm.status == "available"


# ── 6. ANALYTICS ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_analytics_middleware_and_helpers():
    assert analytics._event_for_path("/api/v2/auth/login") == "session_start"
    assert analytics._event_for_path("/unknown/path") is None

    p = analytics.build_analytics_payload("login_evt", "pseudo_1", "/api/v2/auth/login", {"key": "val"})
    assert p["analytics_event"] == "login_evt"
    assert p["distinct_id"] == "pseudo_1"
    assert p["properties"]["key"] == "val"

    async def dummy_call_next(req: Request) -> Response:
        return Response(content="ok", status_code=200)

    # 1. request.state.analytics present
    req1 = MagicMock(spec=Request)
    req1.url = SimpleNamespace(path="/api/v2/custom")
    req1.state = SimpleNamespace(analytics={"event": "custom_evt", "pseudonym_id": "p123", "properties": {"a": 1}})
    with patch("app.services.telemetry.TelemetryService.track_event_async", new_callable=AsyncMock):
        res1 = await analytics.analytics_middleware(req1, dummy_call_next)
        assert res1.status_code == 200

    # 2. Path in TRACKED_EVENTS with header
    req2 = MagicMock(spec=Request)
    req2.url = SimpleNamespace(path="/api/v2/auth/login")
    req2.state = SimpleNamespace()
    req2.headers = {"x-eduboost-pseudonym-id": "header_pseudo"}
    with patch("app.services.telemetry.TelemetryService.track_event_async", new_callable=AsyncMock):
        res2 = await analytics.analytics_middleware(req2, dummy_call_next)
        assert res2.status_code == 200

    # 3. Path in TRACKED_EVENTS anonymous
    req3 = MagicMock(spec=Request)
    req3.url = SimpleNamespace(path="/api/v2/diagnostics/submit")
    req3.state = SimpleNamespace()
    req3.headers = {}
    with patch("app.services.telemetry.TelemetryService.track_event_async", new_callable=AsyncMock):
        res3 = await analytics.analytics_middleware(req3, dummy_call_next)
        assert res3.status_code == 200

    # 4. Error response (status >= 400) not tracked
    async def error_call_next(req: Request) -> Response:
        return Response(content="err", status_code=400)

    res4 = await analytics.analytics_middleware(req2, error_call_next)
    assert res4.status_code == 400


# ── 7. JOBS ───────────────────────────────────────────────────────────────────


class SampleEnum(Enum):
    ALPHA = "alpha"


class SampleModel:
    def model_dump(self, mode=None):
        return {"field": "value"}


@pytest.mark.asyncio
async def test_jobs_complete_lifecycle():
    # _jsonable branches
    u = uuid.uuid4()
    dt = datetime.now(timezone.utc)
    assert jobs._jsonable(SampleEnum.ALPHA) == "alpha"
    assert jobs._jsonable(u) == str(u)
    assert jobs._jsonable(dt) == str(dt)
    assert jobs._jsonable([1, (2, {3})]) == [1, [2, [3]]]
    assert jobs._jsonable(SampleModel()) == {"field": "value"}
    assert jobs._jsonable(42) == 42

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.side_effect = Exception("Redis write err")

    with patch("app.core.jobs.get_redis", return_value=mock_redis):
        # Create job
        job = await jobs.create_job("test_op", {"meta": "data"})
        job_id = job["job_id"]
        assert job["operation"] == "test_op"
        assert job["status"] == "queued"

        # Read job fallback from memory
        loaded = await jobs.get_job(job_id)
        assert loaded["job_id"] == job_id

        # Update job
        updated = await jobs.update_job(job_id, status="running", result={"done": True})
        assert updated["status"] == "running"
        assert updated["result"] == {"done": True}

        # Update non-existent job
        assert await jobs.update_job("non_existent_job_id", status="failed") is None

        # run_job success
        async def mock_handler():
            return {"count": 10}

        await jobs.run_job(job_id, mock_handler)
        final_job = await jobs.get_job(job_id)
        assert final_job["status"] == "completed"
        assert final_job["result"] == {"count": 10}

        # run_job failure
        async def failing_handler():
            raise ValueError("Something broke")

        await jobs.run_job(job_id, failing_handler)
        failed_job = await jobs.get_job(job_id)
        assert failed_job["status"] == "failed"
        assert failed_job["error"]["type"] == "ValueError"

        # enqueue_job with background_tasks
        bg = BackgroundTasks()
        enqueued = await jobs.enqueue_job(bg, operation="bg_op", handler=mock_handler)
        assert enqueued["operation"] == "bg_op"
        assert len(bg.tasks) == 1


# ── 8. ARQ_WORKER ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_arq_worker_settings_and_hooks():
    ctx = {}
    await arq_worker.on_startup(ctx)
    assert ctx["settings"] is settings
    assert "db_session_factory" in ctx

    await arq_worker.on_shutdown(ctx)

    assert len(arq_worker.WorkerSettings.functions) >= 1
    assert len(arq_worker.WorkerSettings.cron_jobs) >= 1
    assert arq_worker.WorkerSettings.on_startup == arq_worker.on_startup
    assert arq_worker.WorkerSettings.on_shutdown == arq_worker.on_shutdown


# ── 9. PROVIDERS ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_providers_injection():
    mock_db = AsyncMock()
    learner_svc = await providers.get_learner_service(mock_db)
    assert learner_svc.db is mock_db

    audit_svc = await providers.get_audit_service(mock_db)
    assert audit_svc.repository is mock_db

    lesson_svc = await providers.get_lesson_service(mock_db)
    assert lesson_svc.lesson_repository is mock_db


# ── 10. AUDIT ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fourth_estate_audit_service():
    mock_db = AsyncMock()
    mock_repo = MagicMock()
    mock_entry = SimpleNamespace(id=uuid.uuid4())
    mock_repo.log = AsyncMock(return_value=mock_entry)

    with patch("app.core.audit.AuditRepository", return_value=mock_repo):
        svc = audit.FourthEstateService(mock_db)

        # Helpers
        await svc.consent_granted("g1", "l1", "1.0.0")
        await svc.consent_revoked("g1", "l1")
        await svc.erasure_requested("g1", "pseudo_l1")
        await svc.erasure_executed("pseudo_l1")
        await svc.lesson_generated("pseudo_l1", "Math", "Algebra", "mock_llm")
        await svc.constitutional_violation("pseudo_l1", "Unsafe topic")
        await svc.auth_event("LOGIN_SUCCESS", "g1", {"ip": "127.0.0.1"})
        await svc.access_rejected("g1", "l1", "Missing consent")
        await svc.subscription_changed("g1", "premium", "evt_stripe_1")

        assert mock_repo.log.await_count == 9

        # Logger AttributeError resilience
        with patch("app.core.audit.log.info", side_effect=AttributeError("Logger setup minimal")):
            await svc.record("TEST_EVENT", actor_id="a1")


# ── 11. STRIPE_CLIENT ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_stripe_service_complete():
    mock_db = AsyncMock()
    mock_guardian_repo = MagicMock()
    mock_event_repo = MagicMock()

    with (
        patch("app.core.stripe_client.GuardianRepository", return_value=mock_guardian_repo),
        patch("app.core.stripe_client.StripeEventRepository", return_value=mock_event_repo),
    ):
        svc = stripe_client.StripeService(mock_db)

        # 1. create_checkout_session: guardian not found
        mock_guardian_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc1:
            await svc.create_checkout_session("g_missing", "test@example.com")
        assert exc1.value.status_code == 404

        # 2. create_checkout_session: guardian without customer_id
        guardian_no_cust = SimpleNamespace(id="g1", stripe_customer_id=None)
        mock_guardian_repo.get_by_id = AsyncMock(return_value=guardian_no_cust)
        mock_guardian_repo.update_subscription = AsyncMock()

        mock_customer = SimpleNamespace(id="cus_new_123")
        mock_checkout = SimpleNamespace(url="https://checkout.stripe.com/pay/cs_123")

        with (
            patch("stripe.Customer.create", return_value=mock_customer),
            patch("stripe.checkout.Session.create", return_value=mock_checkout),
        ):
            url = await svc.create_checkout_session("g1", "test@example.com")
            assert url == "https://checkout.stripe.com/pay/cs_123"
            mock_db.execute.assert_awaited()
            mock_guardian_repo.update_subscription.assert_awaited_once_with("g1", "free", None)

        # 3. handle_webhook: signature error
        with patch("stripe.Webhook.construct_event", side_effect=stripe_client.stripe.error.SignatureVerificationError("bad sig", "sig")):
            with pytest.raises(HTTPException) as exc2:
                await svc.handle_webhook(b"payload", "bad_sig")
            assert exc2.value.status_code == 400

        # 4. handle_webhook: already processed
        mock_event_repo.is_processed = AsyncMock(return_value=True)
        with patch("stripe.Webhook.construct_event", return_value={"id": "evt_dup"}):
            res_dup = await svc.handle_webhook(b"payload", "valid_sig")
            assert res_dup == {"status": "already_processed"}

        # 5. handle_webhook: customer.subscription.created & deleted
        mock_event_repo.is_processed = AsyncMock(return_value=False)
        mock_event_repo.record = AsyncMock()

        evt_created = {
            "id": "evt_created_1",
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_123",
                    "status": "active",
                    "metadata": {"guardian_id": "g1"},
                }
            },
        }

        mock_subscription_svc = MagicMock()
        mock_subscription_svc.activate_premium = AsyncMock()
        mock_subscription_svc.downgrade_to_free = AsyncMock()

        with (
            patch("stripe.Webhook.construct_event", return_value=evt_created),
            patch("app.core.stripe_client.SubscriptionService", return_value=mock_subscription_svc),
        ):
            res_created = await svc.handle_webhook(b"payload", "valid_sig")
            assert res_created == {"status": "processed"}
            mock_subscription_svc.activate_premium.assert_awaited_once_with("g1", "sub_123")

        # Subscription change without guardian_id in metadata
        evt_no_guardian = {
            "id": "evt_no_g",
            "type": "customer.subscription.created",
            "data": {"object": {"id": "sub_nog", "status": "active", "metadata": {}}},
        }
        with (
            patch("stripe.Webhook.construct_event", return_value=evt_no_guardian),
            patch("app.core.stripe_client.SubscriptionService", return_value=mock_subscription_svc),
        ):
            await svc.handle_webhook(b"payload", "valid_sig")

        # 6. handle_webhook: invoice.payment_failed
        evt_failed = {
            "id": "evt_failed_1",
            "type": "invoice.payment_failed",
            "data": {"object": {"subscription": "sub_123", "customer": "cus_123"}},
        }
        mock_guardian_repo.get_by_stripe_customer_id = AsyncMock(return_value=SimpleNamespace(id="g1"))
        with (
            patch("stripe.Webhook.construct_event", return_value=evt_failed),
            patch("app.core.stripe_client.SubscriptionService", return_value=mock_subscription_svc),
        ):
            res_failed = await svc.handle_webhook(b"payload", "valid_sig")
            assert res_failed == {"status": "processed"}
            mock_subscription_svc.downgrade_to_free.assert_awaited_with("g1")


# ── 12. LOGGING ───────────────────────────────────────────────────────────────


def test_core_logging_configuration(monkeypatch):
    # Non-production configuration
    monkeypatch.setattr(type(settings), "is_production", lambda self: False)
    monkeypatch.setattr(settings, "DEBUG", True)
    core_logging.configure_logging()
    logger = core_logging.get_logger("test_dev")
    assert logger is not None

    # Production configuration with Sentry
    monkeypatch.setattr(type(settings), "is_production", lambda self: True)
    monkeypatch.setattr(settings, "DEBUG", False)
    monkeypatch.setattr(settings, "SENTRY_DSN", "https://public@sentry.example.com/1")

    with patch("sentry_sdk.init") as mock_sentry_init:
        core_logging.configure_logging()
        mock_sentry_init.assert_called_once()
