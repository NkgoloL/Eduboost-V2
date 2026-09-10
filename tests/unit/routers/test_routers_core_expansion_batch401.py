from datetime import datetime, timezone, timedelta
import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest
from fastapi import HTTPException, Response
from starlette.requests import Request

from app.api_v2_deps.auth import AuthContext, TokenType, UserRole
from app.api_v2_routers import (
    lessons,
    learners,
    popia,
    auth,
    consent,
    api_v2,
)
from app.domain.schemas import (
    LessonRequest,
    LessonSyncRequest,
    LessonSyncEvent,
    LearnerCreate,
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
)
from app.domain.consent import ConsentRecord


@pytest.fixture
def mock_auth_context() -> AuthContext:
    uid = str(uuid4())
    return AuthContext(
        user_id=uid,
        roles=[UserRole.PARENT, UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": uid, "user_id": uid},
        jti="jti_123",
    )


# ── LESSONS ROUTER ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_lessons_router_generate_and_stream(monkeypatch, mock_auth_context):
    monkeypatch.setattr(lessons, "require_learner_write_for_current_user", MagicMock())
    monkeypatch.setattr(lessons, "require_active_consent_for_current_user", AsyncMock())
    monkeypatch.setattr(lessons, "enqueue_durable", AsyncMock(return_value="job_lesson_01"))

    db = AsyncMock()
    req = LessonRequest(learner_id=str(uuid4()), subject="Mathematics", topic="Fractions", language="en")

    # 1. generate_lesson
    mock_request = MagicMock(spec=Request)
    res_gen = await lessons.generate_lesson(mock_request, req, mock_auth_context, db)
    assert res_gen.job_id == "job_lesson_01"

    # 2. generate_lesson_stream - success
    mock_svc = MagicMock()
    mock_lesson = MagicMock()
    mock_lesson.model_dump_json.return_value = json.dumps({"lesson_id": "l1"})
    mock_svc.generate_lesson_for_learner = AsyncMock(return_value=(mock_lesson, False, "openai"))

    stream_resp = await lessons.generate_lesson_stream(req, mock_auth_context, db, mock_svc)
    assert stream_resp.media_type == "text/event-stream"

    events = [chunk async for chunk in stream_resp.body_iterator]
    assert any("accepted" in e for e in events)
    assert any("completed" in e for e in events)

    # 3. generate_lesson_stream - HTTPException
    mock_svc.generate_lesson_for_learner = AsyncMock(side_effect=HTTPException(status_code=400, detail="LLM error"))
    stream_err = await lessons.generate_lesson_stream(req, mock_auth_context, db, mock_svc)
    events_err = [chunk async for chunk in stream_err.body_iterator]
    assert any("LLM error" in e for e in events_err)

    # 4. generate_lesson_stream - Exception
    mock_svc.generate_lesson_for_learner = AsyncMock(side_effect=RuntimeError("Fatal error"))
    stream_fatal = await lessons.generate_lesson_stream(req, mock_auth_context, db, mock_svc)
    events_fatal = [chunk async for chunk in stream_fatal.body_iterator]
    assert any("Fatal error" in e for e in events_fatal)


@pytest.mark.asyncio
async def test_lessons_router_crud_and_sync(monkeypatch, mock_auth_context):
    monkeypatch.setattr(lessons, "require_lesson_read_access_for_current_user", AsyncMock())
    monkeypatch.setattr(lessons, "require_lesson_write_access_for_current_user", AsyncMock())
    db = AsyncMock()
    mock_svc = MagicMock()

    # 1. get_lesson not found
    mock_svc.get_lesson_by_id = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_get:
        await lessons.get_lesson("l_missing", mock_auth_context, mock_svc, db)
    assert exc_get.value.status_code == 404

    # 2. get_lesson found
    mock_lesson_obj = {
        "id": "l_1",
        "grade": 4,
        "subject": "Maths",
        "topic": "Fractions",
        "language": "en",
        "content": "Lesson text content here",
        "archetype": "Visual",
        "served_from_cache": False,
        "cache_hit": False,
        "caps_aligned": True,
        "created_at": datetime.now(timezone.utc),
    }
    mock_svc.get_lesson_by_id = AsyncMock(return_value=mock_lesson_obj)
    res_l = await lessons.get_lesson("l_1", mock_auth_context, mock_svc, db)
    assert res_l.id == "l_1"

    # 3. complete_lesson not found & found
    mock_svc.get_lesson_by_id = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_c:
        await lessons.complete_lesson("l_missing", mock_auth_context, mock_svc, db)
    assert exc_c.value.status_code == 404

    mock_svc.get_lesson_by_id = AsyncMock(return_value=mock_lesson_obj)
    mock_svc.complete_lesson = AsyncMock()
    res_c = await lessons.complete_lesson("l_1", mock_auth_context, mock_svc, db)
    assert res_c["status"] == "success"

    # 4. sync_lessons
    monkeypatch.setattr(lessons, "iter_sync_lesson_ids", lambda body: ["l_1", "l_2"])
    mock_svc.record_feedback = AsyncMock()
    body_sync = LessonSyncRequest(
        responses=[
            LessonSyncEvent(lesson_id="l_1", event_type="complete"),
            LessonSyncEvent(lesson_id="l_2", event_type="feedback", score=5),
        ]
    )
    res_sync = await lessons.sync_lessons(body_sync, mock_auth_context, mock_svc, db)
    assert res_sync["status"] == "success"
    assert res_sync["processed"] == 2


# ── LEARNERS ROUTER ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_learners_router(monkeypatch, mock_auth_context):
    db = AsyncMock()
    mock_svc = MagicMock()
    monkeypatch.setattr(learners, "LearnerService", lambda d: mock_svc)
    monkeypatch.setattr(learners, "require_learner_read_for_current_user", MagicMock())
    monkeypatch.setattr(learners, "require_active_consent_for_current_user", AsyncMock())

    # 1. create_learner
    mock_learner = {
        "id": str(uuid4()),
        "pseudonym_id": "pseudo_123",
        "display_name": "Lebo",
        "grade": 4,
        "language": "en",
        "archetype": "Visual",
        "theta": 0.0,
        "xp": 100,
        "streak_days": 3,
        "created_at": datetime.now(timezone.utc),
    }
    mock_svc.create_learner = AsyncMock(return_value=mock_learner)
    body_create = LearnerCreate(display_name="Lebo", grade=4, language="en")
    created = await learners.create_learner(body_create, db, mock_auth_context)
    assert created.display_name == "Lebo"

    # 2. get_learner not found & found
    mock_svc.get_learner_summary = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc:
        await learners.get_learner("l_none", db, mock_auth_context)
    assert exc.value.status_code == 404

    mock_svc.get_learner_summary = AsyncMock(return_value=mock_learner)
    res_g = await learners.get_learner(mock_learner["id"], db, mock_auth_context)
    assert res_g.display_name == "Lebo"

    # 3. get_mastery not found & found
    mock_svc.get_learner_summary = AsyncMock(return_value=None)
    with pytest.raises(HTTPException):
        await learners.get_mastery("l_none", db, mock_auth_context)

    mock_svc.get_learner_summary = AsyncMock(return_value=mock_learner)
    mock_svc.get_mastery = AsyncMock(return_value={"overall_score": 0.8})
    m = await learners.get_mastery(mock_learner["id"], db, mock_auth_context)
    assert m["overall_score"] == 0.8

    # 4. get_mastery_summary not found & found
    mock_svc.get_learner_summary = AsyncMock(return_value=None)
    with pytest.raises(HTTPException):
        await learners.get_mastery_summary("l_none", db, mock_auth_context)

    mock_svc.get_learner_summary = AsyncMock(return_value=mock_learner)
    mock_svc.get_subject_mastery_summary = AsyncMock(return_value={"Mathematics": 0.85})
    ms = await learners.get_mastery_summary(mock_learner["id"], db, mock_auth_context)
    assert ms["Mathematics"] == 0.85

    # 5. get_topic_mastery not found & found
    mock_svc.get_learner_summary = AsyncMock(return_value=None)
    with pytest.raises(HTTPException):
        await learners.get_topic_mastery("l_none", "CAPS.MATH.G4.1", db, mock_auth_context)

    mock_svc.get_learner_summary = AsyncMock(return_value=mock_learner)
    mock_svc.get_topic_mastery = AsyncMock(return_value={"topic": "Numbers", "mastery": 0.9})
    tm = await learners.get_topic_mastery(mock_learner["id"], "CAPS.MATH.G4.1", db, mock_auth_context)
    assert tm["mastery"] == 0.9

    # 6. request_erasure
    mock_popia = MagicMock()
    mock_popia.request_erasure = AsyncMock(return_value={"status": "pending_approval"})
    monkeypatch.setattr(learners, "POPIADataRightsService", lambda d: mock_popia)
    res_erase = await learners.request_erasure("l_1", db, mock_auth_context)
    assert res_erase["status"] == "pending_approval"

    # 7. enqueue_data_purge
    await learners.enqueue_data_purge("l_1", "pseudo_1")


# ── POPIA ROUTER ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_popia_router(monkeypatch, mock_auth_context):
    monkeypatch.setattr(popia, "_enforce_popia_learner_write", AsyncMock())
    monkeypatch.setattr(popia, "_authenticated_actor_id", lambda u: "actor_123")

    lid = uuid4()
    gid = uuid4()

    mock_consent_svc = MagicMock()
    mock_consent_record = MagicMock()
    mock_consent_record.learner_id = lid
    mock_consent_record.guardian_id = gid
    mock_consent_record.state = "active"
    mock_consent_svc.grant = AsyncMock(return_value=mock_consent_record)
    mock_consent_svc.deny = AsyncMock(return_value=mock_consent_record)
    mock_consent_svc.withdraw = AsyncMock(return_value=mock_consent_record)
    mock_consent_svc.renew = AsyncMock(return_value=mock_consent_record)

    # 1. grant
    grant_req = popia.ConsentGrantRequest(learner_id=lid, guardian_id=gid, privacy_notice_version="1.0")
    g_res = await popia.grant_consent(grant_req, mock_consent_svc, mock_auth_context)
    assert g_res.state == "active"

    # 2. deny
    deny_req = popia.ConsentDenyRequest(learner_id=lid, guardian_id=gid, privacy_notice_version="1.0", reason="opt_out")
    d_res = await popia.deny_consent(deny_req, mock_consent_svc, mock_auth_context)
    assert d_res.state == "active"

    # 3. withdraw
    withdraw_req = popia.ConsentWithdrawRequest(learner_id=lid)
    w_res = await popia.withdraw_consent(withdraw_req, mock_consent_svc, mock_auth_context)
    assert w_res.state == "active"

    # 4. renew
    renew_req = popia.ConsentRenewRequest(learner_id=lid, privacy_notice_version="2.0")
    r_res = await popia.renew_consent(renew_req, mock_consent_svc, mock_auth_context)
    assert r_res.state == "active"

    # 5. DSR routes
    mock_dsr_svc = MagicMock()
    mock_dsr_svc.build_learner_export = AsyncMock(return_value={"export_url": "https://s3/export.zip"})
    mock_dsr_svc.request_erasure = AsyncMock(return_value={"erasure_id": "e1", "status": "pending"})
    mock_dsr_svc.cancel_erasure = AsyncMock(return_value={"status": "cancelled"})
    mock_dsr_svc.erasure_status = AsyncMock(return_value={"status": "processing"})
    mock_dsr_svc.request_correction = AsyncMock(return_value={"status": "corrected"})
    mock_dsr_svc.restrict_processing = AsyncMock(return_value={"status": "restricted"})

    exp_body = popia.ExportRequestBody(learner_id=lid)
    exp_res = await popia.create_export_request(exp_body, mock_dsr_svc, mock_auth_context)
    assert "export_url" in exp_res

    era_body = popia.ErasureRequestBody(learner_id=lid)
    era_res = await popia.create_erasure_request(era_body, mock_dsr_svc, mock_auth_context)
    assert era_res["status"] == "pending"

    era_can = await popia.cancel_erasure(lid, mock_dsr_svc, mock_auth_context)
    assert era_can["status"] == "cancelled"

    era_st = await popia.erasure_status(lid, mock_dsr_svc, mock_auth_context)
    assert era_st["status"] == "processing"

    corr_body = popia.CorrectionRequestLegacyBody(learner_id=lid, fields={"name": "Lebo"}, reason="spelling")
    corr_res = await popia.create_correction_request(corr_body, mock_dsr_svc, mock_auth_context)
    assert corr_res["status"] == "corrected"

    rest_body = popia.RestrictionRequestLegacyBody(learner_id=lid, reason="dispute")
    rest_res = await popia.create_restriction_request(rest_body, mock_dsr_svc, mock_auth_context)
    assert rest_res["status"] == "restricted"


# ── AUTH ROUTER ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_auth_router(monkeypatch, mock_auth_context):
    # 1. helpers
    claims = auth._canonical_access_claims({"user_id": "u1", "role": "Parent"})
    assert "sub" in claims or "user_id" in claims or isinstance(claims, dict)

    ref_claims = auth._canonical_refresh_claims({"sub": "u1"}, {"user_id": "u1"})
    assert isinstance(ref_claims, dict)

    resp_err = auth._legacy_refresh_error_response("Token expired", status_code=401)
    assert resp_err.status_code == 401

    mock_resp = Response()
    auth._set_refresh_cookie(mock_resp, "token_val")
    assert "eduboost_refresh" in mock_resp.headers.get("set-cookie", "")

    # 2. me
    me_res = await auth.me(mock_auth_context)
    assert me_res.user_id == mock_auth_context.user_id

    # 3. register & login delegates
    mock_app_svc = MagicMock()
    mock_app_svc.register = AsyncMock(return_value={"access_token": "a1", "token_type": "bearer"})
    mock_app_svc.login = AsyncMock(return_value={"access_token": "a2", "token_type": "bearer"})
    mock_app_svc.create_dev_session = AsyncMock(return_value={"access_token": "a_dev", "token_type": "bearer"})
    mock_app_svc.refresh = AsyncMock(return_value={"access_token": "a_ref", "token_type": "bearer"})
    mock_app_svc.logout = AsyncMock(return_value=None)
    mock_app_svc.revoke_all_tokens = AsyncMock(return_value=None)

    db = AsyncMock()
    mock_rt = MagicMock()
    mock_req = MagicMock(spec=Request)

    reg_req = RegisterRequest(email="test.parent@example.com", password="StrongPass#2026", display_name="Test Parent")
    res_reg = await auth.register(mock_req, reg_req, mock_resp, db, mock_rt, mock_app_svc)
    assert res_reg["access_token"] == "a1"

    login_req = LoginRequest(email="test.parent@example.com", password="StrongPass#2026")
    res_login = await auth.login(mock_req, login_req, mock_resp, db, mock_rt, mock_app_svc)
    assert res_login["access_token"] == "a2"

    # 4. dev-session
    monkeypatch.setattr(auth.settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(auth.settings, "APP_ENV", "production")
    with pytest.raises(HTTPException) as exc_dev:
        await auth.create_dev_session(mock_resp, db, mock_rt, mock_app_svc)
    assert exc_dev.value.status_code == 404

    monkeypatch.setattr(auth.settings, "ENVIRONMENT", "development")
    monkeypatch.setattr(auth.settings, "APP_ENV", "development")
    res_dev = await auth.create_dev_session(mock_resp, db, mock_rt, mock_app_svc)
    assert res_dev["access_token"] == "a_dev"

    # 5. refresh
    res_ref = await auth.refresh(mock_req, mock_resp, RefreshRequest(refresh_token="tok"), db, "cookie_val", mock_rt, mock_app_svc)
    assert res_ref["access_token"] == "a_ref"

    # 6. list_sessions
    monkeypatch.setattr(auth, "list_user_refresh_sessions", AsyncMock(return_value=[{"jti": "j1"}]))
    sess = await auth.list_sessions(mock_auth_context)
    assert len(sess["sessions"]) == 1

    # 7. logout & revoke_all_tokens
    await auth.logout(mock_resp, mock_auth_context, db, "cookie_val", mock_app_svc)
    await auth.revoke_all_tokens(mock_resp, mock_auth_context, db, "cookie_val", mock_app_svc)


# ── CONSENT ROUTER ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_consent_router(monkeypatch, mock_auth_context):
    db = AsyncMock()
    mock_learner_svc = MagicMock()
    monkeypatch.setattr(consent, "LearnerService", lambda d: mock_learner_svc)
    monkeypatch.setattr(consent, "require_learner_write_for_current_user", MagicMock())
    monkeypatch.setattr(consent, "require_learner_read_for_current_user", MagicMock())

    lid = uuid4()
    req = MagicMock(spec=Request)
    req.state = MagicMock()
    req.headers = {"X-Forwarded-For": "10.0.0.1, 10.0.0.2"}

    # 1. grant_consent learner not found
    mock_learner_svc.get_learner_summary = AsyncMock(return_value=None)
    grant_body = consent.ConsentGrantRequest(learner_id=lid, consent_version="1.0")
    with pytest.raises(HTTPException) as exc_g:
        await consent.grant_consent(grant_body, req, mock_auth_context, db)
    assert exc_g.value.status_code == 404

    # 2. grant_consent success
    mock_learner_svc.get_learner_summary = AsyncMock(return_value={"id": str(lid)})
    mock_consent_svc = MagicMock()
    mock_rec = MagicMock()
    mock_rec.id = uuid4()
    mock_rec.learner_id = lid
    mock_rec.granted_at = datetime.now(timezone.utc)
    mock_rec.expires_at = datetime.now(timezone.utc) + timedelta(days=365)
    mock_consent_svc.grant = AsyncMock(return_value=mock_rec)
    mock_consent_svc.revoke = AsyncMock()
    monkeypatch.setattr(consent, "ConsentService", lambda d: mock_consent_svc)

    res_grant = await consent.grant_consent(grant_body, req, mock_auth_context, db)
    assert res_grant["learner_id"] == str(lid)

    # 3. revoke_consent learner not found
    mock_learner_svc.get_learner_summary = AsyncMock(return_value=None)
    revoke_body = consent.ConsentRevokeRequest(learner_id=lid, request_export=True, request_erasure=True)
    with pytest.raises(HTTPException) as exc_r:
        await consent.revoke_consent(revoke_body, req, mock_auth_context, db)
    assert exc_r.value.status_code == 404

    # 4. revoke_consent success with export & erasure
    mock_learner_svc.get_learner_summary = AsyncMock(return_value={"id": str(lid)})
    mock_popia = MagicMock()
    mock_popia.request_export = AsyncMock(return_value={"request_id": "exp_01"})
    mock_popia.request_erasure = AsyncMock(return_value={"request_id": "era_01"})
    monkeypatch.setattr(consent, "POPIADataRightsService", lambda d: mock_popia)

    res_rev = await consent.revoke_consent(revoke_body, req, mock_auth_context, db)
    assert res_rev["revoked"] == 1
    assert res_rev["export_request_id"] == "exp_01"
    assert res_rev["erasure_request_id"] == "era_01"

    # 5. consent_status learner not found
    mock_learner_svc.get_learner_summary = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_st:
        await consent.consent_status(lid, mock_auth_context, db)
    assert exc_st.value.status_code == 404

    # 6. consent_status inactive (None)
    mock_learner_svc.get_learner_summary = AsyncMock(return_value={"id": str(lid)})
    mock_consent_svc.get_status = AsyncMock(return_value=None)
    st_inactive = await consent.consent_status(lid, mock_auth_context, db)
    assert st_inactive["active"] is False

    # 7. consent_status active
    mock_consent_svc.get_status = AsyncMock(return_value=mock_rec)
    st_active = await consent.consent_status(lid, mock_auth_context, db)
    assert st_active["active"] is True
    assert st_active["days_remaining"] >= 364

    # 8. _get_ip
    req_fwd = MagicMock()
    req_fwd.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
    assert consent._get_ip(req_fwd) == "192.168.1.1"

    req_client = MagicMock()
    req_client.headers = {}
    req_client.client = MagicMock(host="127.0.0.1")
    assert consent._get_ip(req_client) == "127.0.0.1"

    req_none = MagicMock()
    req_none.headers = {}
    req_none.client = None
    assert consent._get_ip(req_none) is None


# ── API_V2 APPLICATION ROUTER ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_api_v2_app_router():
    h = await api_v2.health()
    assert h["status"] == "ok"

    r = await api_v2.root()
    assert r.status_code == 200

    async with api_v2.lifespan(api_v2.app):
        pass
