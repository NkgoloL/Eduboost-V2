from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from app.core import (
    base,
    consent_policy,
    dependencies as core_deps,
    envelope_route,
    exceptions,
    llm_gateway,
    middleware as core_mw,
    policy,
)
from app.core.database import Base
from app.models import UserRole
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID


# ── 1. LLM_GATEWAY SHIM ───────────────────────────────────────────────────────


def test_llm_gateway_shim():
    assert hasattr(llm_gateway, "ExecutiveService")
    assert hasattr(llm_gateway, "active_provider_label")


# ── 2. EXCEPTIONS & HANDLERS ──────────────────────────────────────────────────


def test_custom_exception_subclasses():
    e1 = exceptions.NotFoundError("Resource missing", {"id": "1"})
    assert e1.status_code == 404
    assert e1.error_code == "not_found"

    e2 = exceptions.ConsentRequiredError("Consent needed")
    assert e2.status_code == 403

    e3 = exceptions.ConsentExpiredError("Consent expired")
    assert e3.status_code == 403

    e4 = exceptions.AuthenticationError("Auth failed")
    assert e4.status_code == 401

    e5 = exceptions.AuthorisationError("Forbidden")
    assert e5.status_code == 403

    e6 = exceptions.DuplicateError("Conflict")
    assert e6.status_code == 409

    e7 = exceptions.LLMError("LLM down")
    assert e7.status_code == 503

    e8 = exceptions.POPIAViolationError("POPIA rule")
    assert e8.status_code == 451


def test_exception_helper_functions():
    req = MagicMock(spec=Request)
    req.state = SimpleNamespace(request_id="req_999")
    assert exceptions._request_id(req) == "req_999"

    assert exceptions._http_error_code(404) == "not_found"
    assert exceptions._http_error_code(418) == "http_error"

    msg1, det1 = exceptions._http_message_and_details("simple message")
    assert msg1 == "simple message"
    assert det1 == {}

    msg2, det2 = exceptions._http_message_and_details({"message": "dict msg", "extra": "val"})
    assert msg2 == "dict msg"
    assert det2 == {"extra": "val"}

    msg3, det3 = exceptions._http_message_and_details(12345)
    assert msg3 == "12345"
    assert det3 == {"detail": 12345}


def test_registered_exception_handlers():
    app = FastAPI()
    exceptions.register_exception_handlers(app)

    @app.get("/err/eduboost")
    async def throw_eduboost():
        raise exceptions.NotFoundError("Target missing", {"item": "alpha"})

    @app.get("/err/http")
    async def throw_http():
        raise HTTPException(status_code=400, detail={"detail": "Bad syntax"})

    @app.get("/err/validation")
    async def throw_validation():
        raise RequestValidationError([{"loc": ("body", "field_a"), "msg": "Required field", "type": "missing"}])

    @app.get("/err/jwt")
    async def throw_jwt():
        from app.core.jwt_compat import JWTError
        raise JWTError("Corrupted token signature")

    @app.get("/err/integrity")
    async def throw_integrity():
        raise IntegrityError("INSERT INTO", {}, Exception("Duplicate key"))

    class CustomRateLimitExceeded(RateLimitExceeded):
        status_code = 429
        def __init__(self):
            self.detail = "Limit 5/min exceeded"

    @app.get("/err/rate")
    async def throw_rate():
        raise CustomRateLimitExceeded()

    @app.get("/err/unhandled")
    async def throw_unhandled():
        raise RuntimeError("Crash unexpected")

    client = TestClient(app, raise_server_exceptions=False)

    r1 = client.get("/err/eduboost")
    assert r1.status_code == 404
    assert r1.json()["error"]["code"] == "not_found"

    r2 = client.get("/err/http")
    assert r2.status_code == 400
    assert r2.json()["error"]["code"] == "bad_request"

    r3 = client.get("/err/validation")
    assert r3.status_code == 422
    assert r3.json()["error"]["code"] == "validation_error"

    r4 = client.get("/err/jwt")
    assert r4.status_code == 401
    assert r4.json()["error"]["code"] == "unauthorized"

    r5 = client.get("/err/integrity")
    assert r5.status_code == 409
    assert r5.json()["error"]["code"] == "conflict"

    r6 = client.get("/err/rate")
    assert r6.status_code == 429
    assert r6.json()["error"]["code"] == "rate_limited"

    r7 = client.get("/err/unhandled")
    assert r7.status_code == 500
    assert r7.json()["error"]["code"] == "internal_error"


# ── 3. MIDDLEWARE ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_middleware_stack():
    # 1. _normalise_path
    uuid_str = str(uuid.uuid4())
    norm = core_mw._normalise_path(f"/api/v2/learners/{uuid_str}/lessons")
    assert norm == "/api/v2/learners/{id}/lessons"

    # 2. _get_client_ip
    req_fwd = MagicMock(spec=Request)
    req_fwd.headers = {"X-Forwarded-For": "203.0.113.195, 70.41.3.18"}
    assert core_mw._get_client_ip(req_fwd) == "203.0.113.195"

    req_client = MagicMock(spec=Request)
    req_client.headers = {}
    req_client.client = SimpleNamespace(host="10.0.0.1")
    assert core_mw._get_client_ip(req_client) == "10.0.0.1"

    req_unknown = MagicMock(spec=Request)
    req_unknown.headers = {}
    req_unknown.client = None
    assert core_mw._get_client_ip(req_unknown) == "unknown"

    # 3. RequestIDMiddleware
    req_id_mw = core_mw.RequestIDMiddleware(app=MagicMock())
    req1 = MagicMock(spec=Request)
    req1.headers = {"X-Request-ID": "custom_req_id_123"}
    req1.state = SimpleNamespace()

    async def call_next_ok(request: Request) -> Response:
        return Response(content="ok", status_code=200)

    res1 = await req_id_mw.dispatch(req1, call_next_ok)
    assert res1.headers["X-Request-ID"] == "custom_req_id_123"

    # 4. TimingMiddleware
    timing_mw = core_mw.TimingMiddleware(app=MagicMock())
    req_timing = MagicMock(spec=Request)
    req_timing.url = SimpleNamespace(path=f"/api/v2/items/{uuid_str}")
    req_timing.method = "GET"

    res_timing = await timing_mw.dispatch(req_timing, call_next_ok)
    assert "X-Response-Time" in res_timing.headers

    # 5. StructuredLoggingMiddleware
    log_mw = core_mw.StructuredLoggingMiddleware(app=MagicMock())
    req_log = MagicMock(spec=Request)
    req_log.url = SimpleNamespace(path="/api/v2/items")
    req_log.method = "POST"
    req_log.headers = {}
    req_log.client = SimpleNamespace(host="127.0.0.1")
    req_log.state = SimpleNamespace(request_id="log_req_1")

    res_log = await log_mw.dispatch(req_log, call_next_ok)
    assert res_log.status_code == 200


# ── 4. ENVELOPE_ROUTE ─────────────────────────────────────────────────────────


def test_envelope_route_helpers():
    assert envelope_route._is_already_enveloped({"data": 1, "error": None, "meta": {}}) is True
    assert envelope_route._is_already_enveloped({"result": "ok"}) is False
    assert envelope_route._is_already_enveloped("not a dict") is False

    w = envelope_route._wrap({"hello": "world"}, "req_env_1", 200)
    assert w["data"] == {"hello": "world"}
    assert w["meta"]["request_id"] == "req_env_1"


def test_enveloped_route_integration():
    from fastapi import APIRouter

    router = APIRouter(route_class=envelope_route.EnvelopedRoute)

    @router.get("/bare")
    async def get_bare():
        return JSONResponse(content={"foo": "bar"}, headers={"Content-Length": "14"})

    @router.get("/already_enveloped")
    async def get_enveloped():
        return JSONResponse(content={"data": "done", "error": None, "meta": {"request_id": "r1"}})

    @router.get("/plain")
    async def get_plain():
        return PlainTextResponse("raw text")

    @router.get("/invalid_json_body")
    async def get_invalid_json():
        res = JSONResponse(content={"ok": True})
        res.body = b"not valid json {{"
        return res

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    r_bare = client.get("/bare")
    assert r_bare.status_code == 200
    assert "meta" in r_bare.json()
    assert r_bare.json()["data"] == {"foo": "bar"}

    r_env = client.get("/already_enveloped")
    assert r_env.status_code == 200
    assert r_env.json()["data"] == "done"

    r_plain = client.get("/plain")
    assert r_plain.status_code == 200
    assert r_plain.text == "raw text"

    r_inv = client.get("/invalid_json_body")
    assert r_inv.status_code == 200


# ── 5. CONSENT_POLICY ─────────────────────────────────────────────────────────


def test_consent_policy_transitions():
    now = datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc)
    naive_dt = datetime(2026, 9, 10, 12, 0, 0)
    assert consent_policy._as_aware(naive_dt).tzinfo == timezone.utc
    assert consent_policy._as_aware(None) is None

    # 1. No record -> PENDING
    d1 = consent_policy.derive_consent_state(None, learner_id="l1", now=now)
    assert d1.state == consent_policy.ConsentState.PENDING
    assert d1.active is False

    # 2. Persisted state: DENIED
    consent_denied = SimpleNamespace(status="denied", granted_at=None, expires_at=None, revoked_at=None)
    d2 = consent_policy.derive_consent_state(consent_denied, learner_id="l1", now=now)
    assert d2.state == consent_policy.ConsentState.DENIED
    assert d2.active is False

    # 3. Invalid persisted state string fallback
    consent_inv = SimpleNamespace(status="invalid_status_str", granted_at=now, expires_at=None, revoked_at=None)
    d3 = consent_policy.derive_consent_state(consent_inv, learner_id="l1", now=now)
    assert d3.state == consent_policy.ConsentState.GRANTED
    assert d3.active is True

    # 4. Revoked / Withdrawn
    consent_withdrawn = SimpleNamespace(status=None, granted_at=now - timedelta(days=10), expires_at=now + timedelta(days=100), revoked_at=now - timedelta(days=1))
    d4 = consent_policy.derive_consent_state(consent_withdrawn, learner_id="l1", now=now)
    assert d4.state == consent_policy.ConsentState.WITHDRAWN
    assert d4.active is False

    # 5. Expired
    consent_expired = SimpleNamespace(status=None, granted_at=now - timedelta(days=400), expires_at=now - timedelta(days=10), revoked_at=None)
    d5 = consent_policy.derive_consent_state(consent_expired, learner_id="l1", now=now)
    assert d5.state == consent_policy.ConsentState.EXPIRED
    assert d5.active is False

    # 6. Renewal required (within renewal window)
    consent_renewal = SimpleNamespace(status=None, granted_at=now - timedelta(days=350), expires_at=now + timedelta(days=15), revoked_at=None)
    d6 = consent_policy.derive_consent_state(consent_renewal, learner_id="l1", renewal_window_days=30, now=now)
    assert d6.state == consent_policy.ConsentState.RENEWAL_REQUIRED
    assert d6.active is True

    # 7. Normal active granted
    consent_active = SimpleNamespace(status=None, granted_at=now - timedelta(days=10), expires_at=now + timedelta(days=200), revoked_at=None)
    d7 = consent_policy.derive_consent_state(consent_active, learner_id="l1", renewal_window_days=30, now=now)
    assert d7.state == consent_policy.ConsentState.GRANTED
    assert d7.active is True


# ── 6. POLICY (JUDICIARY) ─────────────────────────────────────────────────────


def test_judiciary_service():
    svc = policy.JudiciaryService()

    # Empty text
    with pytest.raises(policy.ConstitutionalViolation, match="empty response"):
        svc.stamp_study_plan("")

    # Blocked content
    with pytest.raises(policy.ConstitutionalViolation, match="policy violation"):
        svc.stamp_study_plan("pornographic adult content")

    # Valid study plan
    raw_plan = """```json
    {
        "week_label": "Week 1",
        "daily_topics": ["Algebra"],
        "priority_gaps": ["Fractions"]
    }
    ```"""
    plan = svc.stamp_study_plan(raw_plan)
    assert plan.week_label == "Week 1"

    # Invalid study plan schema
    raw_invalid_plan = """{"daily_topics": ["Algebra"]}"""
    with pytest.raises(policy.ConstitutionalViolation, match="StudyPlan schema violation"):
        svc.stamp_study_plan(raw_invalid_plan)

    # Valid diagnostic feedback
    raw_feedback = """```json
    {
        "summary": "Developing well",
        "encouragement": "Keep it up!",
        "next_steps": ["Practice fractions"]
    }
    ```"""
    fb = svc.stamp_diagnostic_feedback(raw_feedback)
    assert fb.summary == "Developing well"

    # Invalid diagnostic schema
    with pytest.raises(policy.ConstitutionalViolation, match="Diagnostic feedback schema violation"):
        svc.stamp_diagnostic_feedback("""{"summary": 123}""")

    # Valid lesson
    raw_lesson = """```json
    {
        "title": "Introduction to Algebra",
        "introduction": "Welcome to variables and expressions.",
        "main_content": "A variable represents an unknown number.",
        "worked_example": "Solve x + 2 = 5 -> x = 3.",
        "practice_question": "Solve x + 3 = 7.",
        "answer": "x = 4",
        "cultural_hook": "Counting goods in South African markets."
    }
    ```"""
    lesson = svc.stamp_lesson(raw_lesson)
    assert lesson.title == "Introduction to Algebra"

    # Invalid lesson schema
    with pytest.raises(policy.ConstitutionalViolation, match="Lesson schema violation"):
        svc.stamp_lesson("""{"title": "x"}""")

    # Answer quality assertions
    mock_lesson = MagicMock()
    mock_lesson.answer = "x"
    with pytest.raises(policy.ConstitutionalViolation, match="valid answer key"):
        svc._assert_answer_quality(mock_lesson)

    mock_lesson.answer = "n/a"
    with pytest.raises(policy.ConstitutionalViolation, match="placeholder answer"):
        svc._assert_answer_quality(mock_lesson)

    mock_lesson.answer = "Answer without numbers"
    mock_lesson.practice_question = "Please calculate 5 + 5"
    # logs warning but does not raise
    svc._assert_answer_quality(mock_lesson)


# ── 7. DEPENDENCIES ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_core_dependencies_learner_gate_and_request_id():
    # 1. get_request_id with contextvar set
    with patch("app.core.context.get_request_id", return_value="cid_123"):
        req = MagicMock(spec=Request)
        assert await core_deps.get_request_id(req) == "cid_123"

    # get_request_id fallback to header
    with patch("app.core.context.get_request_id", return_value=None):
        req_hdr = MagicMock(spec=Request)
        req_hdr.headers = {"X-Request-ID": "hdr_456"}
        assert await core_deps.get_request_id(req_hdr) == "hdr_456"

    # 2. require_active_consent_for_current_learner: learner not found
    mock_db = AsyncMock()
    mock_repo = MagicMock()
    mock_learner_repo = MagicMock()
    mock_learner_repo.get_by_id = AsyncMock(return_value=None)

    lid = uuid.uuid4()
    with patch("app.core.dependencies.LearnerRepository", return_value=mock_learner_repo):
        with pytest.raises(HTTPException) as exc1:
            await core_deps.require_active_consent_for_current_learner(
                lid,
                db=mock_db,
                repo=mock_repo,
                current_user={"sub": "u1", "role": "admin"},
            )
        assert exc1.value.status_code == 404

    # 3. require_active_consent_for_current_learner: learner found & verified
    mock_learner = SimpleNamespace(id=lid)
    mock_learner_repo.get_by_id = AsyncMock(return_value=mock_learner)

    with (
        patch("app.core.dependencies.LearnerRepository", return_value=mock_learner_repo),
        patch("app.core.dependencies.assert_can_access_learner") as mock_access,
        patch("app.core.dependencies.require_active_consent", new_callable=AsyncMock) as mock_req_consent,
    ):
        res_lid = await core_deps.require_active_consent_for_current_learner(
            lid,
            db=mock_db,
            repo=mock_repo,
            current_user={"sub": "u1", "role": "admin"},
        )
        assert res_lid == lid
        mock_access.assert_called_once()
        mock_req_consent.assert_awaited_once_with(lid, mock_db, mock_repo)


# ── 8. BASE_REPOSITORY ────────────────────────────────────────────────────────


class SampleEntity(Base):
    __tablename__ = "sample_entities"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)


@pytest.mark.asyncio
async def test_base_repository():
    class SampleRepo(base.BaseRepository[SampleEntity]):
        model = SampleEntity

    repo = SampleRepo()
    mock_db = AsyncMock()
    mock_db.add = MagicMock()

    # 1. get & get_or_404
    sample_id = uuid.uuid4()
    mock_result = MagicMock()
    mock_item = SampleEntity(id=sample_id, name="test_entity")
    mock_result.scalar_one_or_none.return_value = mock_item
    mock_db.execute.return_value = mock_result

    item = await repo.get(sample_id, mock_db)
    assert item is mock_item

    item_404 = await repo.get_or_404(sample_id, mock_db)
    assert item_404 is mock_item

    # get_or_404 raises NotFoundError
    mock_result.scalar_one_or_none.return_value = None
    with pytest.raises(exceptions.NotFoundError):
        await repo.get_or_404(uuid.uuid4(), mock_db)

    # 2. list with and without filters
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_item]
    mock_result.scalars.return_value = mock_scalars

    items_unfiltered = await repo.list(mock_db, limit=10, offset=0)
    assert items_unfiltered == [mock_item]

    items_filtered = await repo.list(mock_db, filters={"name": "test_entity"}, limit=5)
    assert items_filtered == [mock_item]

    # 3. create, update, delete
    created = await repo.create(mock_db, name="new_entity")
    assert created.name == "new_entity"
    mock_db.add.assert_called()
    mock_db.flush.assert_awaited()

    updated = await repo.update(created, mock_db, name="updated_entity")
    assert updated.name == "updated_entity"

    await repo.delete(updated, mock_db)
    mock_db.delete.assert_called_with(updated)
