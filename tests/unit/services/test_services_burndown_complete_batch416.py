"""Comprehensive unit tests for Batch 416 targeting core services in app/services:
- backend_runtime_wiring_cases
- semantic_retrieval/evaluation
- curriculum/phase02r_verification
- curriculum/coverage
- lesson_service_v2
- job_runtime_integrity
- auth_db_lifecycle_proof
- auth_lifecycle_impl
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest
from fastapi import HTTPException, Response

from app.models import UserRole
from app.services.backend_runtime_wiring_cases import (
    WiringCaseResult,
    _load_cases,
    run_audit_wiring_cases,
    run_consent_wiring_cases,
    run_deep_readiness_wiring_cases,
    run_all_wiring_cases,
    all_wiring_cases_pass,
)
from app.services.semantic_retrieval.evaluation import evaluate_retrieval
from app.services.semantic_retrieval.types import (
    EvaluationCase,
    EvaluationMetrics,
    RetrievalFilters,
)
from app.services.curriculum.phase02r_verification import (
    REQUIRED_PATHS_BY_GATE,
    validate_required_paths,
)
from app.services.curriculum.coverage import (
    CurriculumGap,
    CurriculumCoverageAnalyzer,
)
from app.services.lesson_service_v2 import LessonServiceV2
from app.services.job_runtime_integrity import (
    JobRuntimeIntegrityError,
    assert_json_serializable_payload,
    assert_no_runtime_objects,
    validate_arq_job_payload,
)
from app.services.auth_db_lifecycle_proof import (
    AuthDBProofApplicationService,
    AuthDBProofTokens,
    SQLiteAuthLifecycleProofStore,
    _hash_password,
    _stable_token,
    extract_auth_payload,
    extract_refresh_token,
    token_response,
)
from app.services.auth_lifecycle_impl import (
    _normalise_role_value,
    _ensure_dev_session_consent,
    _set_refresh_cookie,
    _maybe_await,
    create_dev_session_impl,
    login_impl,
    refresh_impl,
    register_impl,
)
from app.domain.schemas import LoginRequest, RefreshRequest, RegisterRequest


# =====================================================================
# 1. Backend Runtime Wiring Cases
# =====================================================================

def test_backend_runtime_wiring_cases():
    res = WiringCaseResult(
        case_name="test_case",
        passed=True,
        message="ok",
        details={"info": 1},
    )
    assert res.passed is True
    assert res.case_name == "test_case"

    # _load_cases error when cases is not a list
    tmp_path = Path("/tmp/invalid_cases.json")
    tmp_path.write_text(json.dumps({"cases": "not-a-list"}))
    try:
        with pytest.raises(ValueError, match="must contain cases list"):
            _load_cases(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    # run_audit_wiring_cases
    audit_results = run_audit_wiring_cases()
    assert len(audit_results) > 0
    assert all(isinstance(r, WiringCaseResult) for r in audit_results)

    # run_consent_wiring_cases
    consent_results = run_consent_wiring_cases()
    assert len(consent_results) > 0

    # run_deep_readiness_wiring_cases
    readiness_results = run_deep_readiness_wiring_cases()
    assert len(readiness_results) > 0

    # Test catalogue mismatch in run_deep_readiness_wiring_cases
    with patch("app.services.backend_runtime_wiring_cases.DEFAULT_DEEP_READINESS_CHECKS", ()):
        mismatch_results = run_deep_readiness_wiring_cases()
        assert any(r.passed is False for r in mismatch_results)

    # run_all_wiring_cases and all_wiring_cases_pass
    all_res = run_all_wiring_cases()
    assert len(all_res) == len(audit_results) + len(consent_results) + len(readiness_results)
    assert isinstance(all_wiring_cases_pass(), bool)


# =====================================================================
# 2. Semantic Retrieval Evaluation
# =====================================================================

@pytest.mark.asyncio
async def test_semantic_retrieval_evaluation():
    mock_session = AsyncMock()
    mock_service = AsyncMock()

    # Empty cases raises ValueError
    with pytest.raises(ValueError, match="requires at least one case"):
        await evaluate_retrieval(mock_session, service=mock_service, cases=[])

    filters = RetrievalFilters(scope_id="caps", grade=10, subject_code="MATH")
    case1 = EvaluationCase(
        case_id="c1",
        query="fractions",
        expected_chunk_ids=frozenset(["chunk-1", "chunk-2"]),
        filters=filters,
        k=2,
    )
    case2 = EvaluationCase(
        case_id="c2",
        query="geometry",
        expected_chunk_ids=frozenset(["chunk-3"]),
        filters=filters,
        k=2,
    )

    hit1 = SimpleNamespace(chunk_id="chunk-1", document_status="approved", chunk_status="approved")
    hit2 = SimpleNamespace(chunk_id="chunk-other", document_status="approved", chunk_status="approved")
    res1 = SimpleNamespace(query="fractions", hits=[hit1, hit2], mode="semantic", fallback_reason=None)

    hit3 = SimpleNamespace(chunk_id="chunk-3", document_status="pending_review", chunk_status="unverified")
    res2 = SimpleNamespace(query="geometry", hits=[hit3], mode="keyword", fallback_reason="degraded")

    mock_service.search.side_effect = [res1, res2]

    metrics = await evaluate_retrieval(
        mock_session,
        service=mock_service,
        cases=[case1, case2],
        recall_threshold=0.5,
        mrr_threshold=0.5,
        unsafe_hit_threshold=0,
    )
    assert isinstance(metrics, EvaluationMetrics)
    assert metrics.case_count == 2
    assert metrics.unsafe_hit_count == 1
    # Because unsafe_hit_count > unsafe_hit_threshold (1 > 0), passed should be False
    assert metrics.passed is False


# =====================================================================
# 3. Curriculum Phase 2R Verification
# =====================================================================

def test_phase02r_verification():
    # Unknown gate returns empty
    assert validate_required_paths("UNKNOWN_GATE") == []

    # Known gate returns list
    errors = validate_required_paths("2R.2")
    assert isinstance(errors, list)

    # Missing file path branch test
    with patch("pathlib.Path.is_file", return_value=False):
        errs = validate_required_paths("2R.3")
        assert len(errs) == len(REQUIRED_PATHS_BY_GATE["2R.3"])
        assert "missing required 2R.3 implementation path" in errs[0]


# =====================================================================
# 4. Curriculum Coverage Analyzer
# =====================================================================

def test_curriculum_coverage_analyzer():
    @dataclass
    class MockTopic:
        reference: str
        grade: int
        subject: str
        topic: str

    mock_topic_map = MagicMock()
    mock_topic_map.topics = [
        MockTopic(reference="CAPS.MATH.1", grade=10, subject="MATH", topic="Algebra"),
        MockTopic(reference="CAPS.MATH.2", grade=10, subject="MATH", topic="Geometry"),
    ]

    analyzer = CurriculumCoverageAnalyzer(topic_map=mock_topic_map)

    # Case 1: Topic 1 has full coverage, Topic 2 has missing items & missing reviewed
    lessons = [
        {"caps_reference": "CAPS.MATH.1", "quality_reviewed": True},
        {"caps_reference": "CAPS.MATH.2", "quality_reviewed": False},
    ]
    diagnostic_items = [
        {"caps_reference": "CAPS.MATH.1"},
    ]

    gaps = analyzer.detect_gaps(lessons=lessons, diagnostic_items=diagnostic_items)
    assert len(gaps) == 1
    gap = gaps[0]
    assert gap.caps_reference == "CAPS.MATH.2"
    assert gap.missing_lessons is False
    assert gap.missing_diagnostics is True
    assert gap.missing_reviewed_content is True

    # Default constructor without arguments initializes CAPSTopicMap
    default_analyzer = CurriculumCoverageAnalyzer()
    assert default_analyzer.topic_map is not None


# =====================================================================
# 5. Lesson Service V2
# =====================================================================

@pytest.mark.asyncio
async def test_lesson_service_v2():
    mock_repo = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.incrby.return_value = 1000
    mock_redis.expire.return_value = True
    mock_redis.set.return_value = True

    service = LessonServiceV2(lesson_repository=mock_repo, redis_client=mock_redis)

    # 1. generate_lesson - cache hit
    mock_redis.get.return_value = json.dumps({"lesson_id": "cached-1", "title": "Cached Lesson"})
    cached_res = await service.generate_lesson(
        learner_id="lrn-1",
        subject_code="MATH",
        topic="Functions",
        grade_level=10,
    )
    assert cached_res["lesson_id"] == "cached-1"

    # 2. generate_lesson - cache miss
    mock_redis.get.return_value = None
    mock_lesson_row = SimpleNamespace(id="lesson-new")
    mock_repo.create.return_value = mock_lesson_row

    with patch("app.services.lesson_service_v2.AuditService.log_event", new_callable=AsyncMock) as mock_audit:
        new_res = await service.generate_lesson(
            learner_id="lrn-1",
            subject_code="MATH",
            topic="Functions",
            grade_level=10,
            archetype="VISUAL",
            tier="premium",
        )
        assert new_res["lesson_id"] == "lesson-new"
        assert new_res["learner_id"] == "lrn-1"
        assert mock_audit.called

    # 3. get_lesson - cached in redis
    mock_redis.get.return_value = json.dumps({"lesson_id": "l-cached", "title": "From Redis"})
    assert (await service.get_lesson("l-cached")) == {"lesson_id": "l-cached", "title": "From Redis"}

    # get_lesson - not in redis, found in DB
    mock_redis.get.return_value = None
    db_lesson = SimpleNamespace(
        lesson_id="db-1",
        title="DB Lesson",
        subject_code="MATH",
        grade_level=10,
        topic="Trig",
        content={"text": "hello"},
        generated_by="V2_LLM",
    )
    mock_repo.get_by_id.return_value = db_lesson
    got = await service.get_lesson("db-1")
    assert got is not None
    assert got["title"] == "DB Lesson"
    assert got["source"] == "database"

    # get_lesson - not in redis, None in DB
    mock_repo.get_by_id.return_value = None
    assert await service.get_lesson("missing") is None

    # 4. submit_feedback
    with patch("app.services.lesson_service_v2.AuditService.log_event", new_callable=AsyncMock) as mock_audit:
        fb = await service.submit_feedback("db-1", "lrn-1", rating=5, comment="Great!")
        assert fb["recorded"] is True
        assert mock_audit.called


# =====================================================================
# 6. Job Runtime Integrity
# =====================================================================

def test_job_runtime_integrity():
    # 1. assert_json_serializable_payload
    assert_json_serializable_payload({"key": "val", "num": 123})

    # Circular dict
    circular = {}
    circular["self"] = circular
    with pytest.raises(JobRuntimeIntegrityError, match="not JSON serializable"):
        assert_json_serializable_payload(circular)

    # 2. assert_no_runtime_objects
    assert_no_runtime_objects({"safe": [1, 2, "three", True, None, {"nested": (1, 2)}]})

    class CustomObject:
        def __init__(self):
            self.val = "ok"

    assert_no_runtime_objects(CustomObject())

    class UnsafeSessionDummy:
        pass

    with pytest.raises(JobRuntimeIntegrityError, match="must not include runtime object"):
        assert_no_runtime_objects({"session": UnsafeSessionDummy()})

    class UnsafeServiceDummy:
        pass

    with pytest.raises(JobRuntimeIntegrityError, match="must not include runtime object"):
        assert_no_runtime_objects([UnsafeServiceDummy()])

    # Circular reference handling in walk
    class CircularNode:
        def __init__(self):
            self.ref = None

    n1 = CircularNode()
    n2 = CircularNode()
    n1.ref = n2
    n2.ref = n1
    assert_no_runtime_objects(n1)

    # 3. validate_arq_job_payload
    validate_arq_job_payload("task_name", arg1=10, arg2="val")


# =====================================================================
# 7. Auth DB Lifecycle Proof
# =====================================================================

@pytest.mark.asyncio
async def test_auth_db_lifecycle_proof_store():
    store = SQLiteAuthLifecycleProofStore()

    # 1. Password hashing & stable token
    h1 = _hash_password("my_pass", "salt1")
    assert isinstance(h1, str)
    st = _stable_token("tok", "sub1")
    assert st.startswith("tok-")

    # 2. Register validations
    with pytest.raises(HTTPException) as exc1:
        store.register(email="", password="pass")
    assert exc1.value.status_code == 422

    with pytest.raises(HTTPException) as exc2:
        store.register(email="user@example.com", password="")
    assert exc2.value.status_code == 422

    tokens1 = store.register(email="user@example.com", password="Pass123!Safe", display_name="Guardian One")
    assert isinstance(tokens1, AuthDBProofTokens)
    assert tokens1.user_id.startswith("user-")
    assert len(tokens1.guardian_learner_ids) == 1

    # Duplicate registration
    with pytest.raises(HTTPException) as exc3:
        store.register(email="user@example.com", password="Pass123!Safe")
    assert exc3.value.status_code == 409

    # 3. Login validations
    with pytest.raises(HTTPException) as exc_login1:
        store.login(email="unknown@example.com", password="wrong")
    assert exc_login1.value.status_code == 401

    with pytest.raises(HTTPException) as exc_login2:
        store.login(email="user@example.com", password="wrong_pass")
    assert exc_login2.value.status_code == 401

    tokens2 = store.login(email="user@example.com", password="Pass123!Safe")
    assert tokens2.user_id == tokens1.user_id

    # 4. Refresh validations
    with pytest.raises(HTTPException) as exc_ref1:
        store.refresh(refresh_token="invalid-token")
    assert exc_ref1.value.status_code == 401

    tokens3 = store.refresh(refresh_token=tokens2.refresh_token)
    assert tokens3.user_id == tokens1.user_id

    # Refresh token reuse error
    with pytest.raises(HTTPException) as exc_ref2:
        store.refresh(refresh_token=tokens2.refresh_token)
    assert exc_ref2.value.status_code == 401

    # 5. Facade service
    service = AuthDBProofApplicationService(store)
    reg_resp = await service.register(email="user2@example.com", password="Pass123!Safe")
    assert "access_token" in reg_resp

    log_resp = await service.login(email="user2@example.com", password="Pass123!Safe")
    assert "access_token" in log_resp

    ref_resp = await service.refresh(refresh_token=log_resp["refresh_token"])
    assert "access_token" in ref_resp

    dev_resp = await service.create_dev_session()
    assert "access_token" in dev_resp

    # 6. extract_refresh_token
    assert extract_refresh_token({"refresh_token": "rt-1"}) == "rt-1"

    # From request cookies (use SimpleNamespace to avoid MagicMock infinite model_dump recursion)
    req_obj = SimpleNamespace(cookies={"refresh_token": "rt-cookie"})
    assert extract_refresh_token({"request": req_obj}) == "rt-cookie"

    with pytest.raises(HTTPException) as exc_rt_miss:
        extract_refresh_token({})
    assert exc_rt_miss.value.status_code == 401

    # 7. token_response
    resp_dict = token_response(tokens3)
    assert resp_dict["access_token"] == tokens3.access_token


# =====================================================================
# 8. Auth Lifecycle Impl
# =====================================================================

@pytest.mark.asyncio
async def test_auth_lifecycle_impl():
    # 1. Helpers
    assert _normalise_role_value(UserRole.PARENT) == "parent"
    assert _normalise_role_value("Role.Guardian") == "guardian"
    assert _normalise_role_value("STUDENT") == "student"

    mock_resp = Response()
    _set_refresh_cookie(mock_resp, "refresh-val")
    assert "eduboost_refresh=refresh-val" in mock_resp.headers.get("set-cookie", "")

    assert await _maybe_await("sync") == "sync"

    async def sample_coro():
        return "async"
    assert await _maybe_await(sample_coro()) == "async"

    # 2. _ensure_dev_session_consent
    mock_consent_repo = AsyncMock()

    # Active consent exists and is not revoked
    active_consent = SimpleNamespace(
        revoked_at=None,
        guardian_id="old_g",
        policy_version="0.9",
        status="pending",
        expires_at=None,
    )
    mock_consent_repo.get_active.return_value = active_consent
    updated_consent = await _ensure_dev_session_consent(
        mock_consent_repo,
        guardian_id="g1",
        learner_id="l1",
    )
    assert updated_consent.guardian_id == "g1"
    assert updated_consent.status == "granted"
    assert updated_consent.policy_version == "1.0.0"

    # Active is None, fallback to get_latest_for_learner
    mock_consent_repo.get_active.return_value = None
    mock_consent_repo.get_latest_for_learner = AsyncMock(return_value=active_consent)
    updated_latest = await _ensure_dev_session_consent(
        mock_consent_repo,
        guardian_id="g1",
        learner_id="l1",
    )
    assert updated_latest.guardian_id == "g1"

    # Neither exists -> calls create
    mock_consent_repo.get_active.return_value = None
    mock_consent_repo.get_latest_for_learner.return_value = None
    created_consent = SimpleNamespace(id="c-new")
    mock_consent_repo.create.return_value = created_consent
    assert await _ensure_dev_session_consent(mock_consent_repo, guardian_id="g1", learner_id="l1") == created_consent

    # 3. create_dev_session_impl
    mock_db = AsyncMock()
    mock_runtime = MagicMock()
    mock_runtime.guardian_repo = AsyncMock()
    mock_runtime.learner_repo = AsyncMock()
    mock_runtime.consent_repo = mock_consent_repo

    # Production check
    from app.core.config import Settings
    with patch.object(Settings, "is_production", return_value=True):
        with pytest.raises(HTTPException) as exc_prod:
            await create_dev_session_impl(mock_resp, mock_db, mock_runtime)
        assert exc_prod.value.status_code == 404

    # Non-production check
    with patch.object(Settings, "is_production", return_value=False), \
         patch("app.services.auth_lifecycle_impl.seed_dev_diagnostic_items", new_callable=AsyncMock), \
         patch("app.services.auth_lifecycle_impl.store_refresh_token", new_callable=AsyncMock), \
         patch("app.services.auth_lifecycle_impl.FourthEstateService.auth_event", new_callable=AsyncMock):

        # When guardian and learner do not exist
        mock_runtime.guardian_repo.get_by_email_hash.return_value = None
        new_g = SimpleNamespace(id="g-dev", role=UserRole.PARENT)
        mock_runtime.guardian_repo.create.return_value = new_g

        mock_runtime.learner_repo.get_by_guardian.return_value = []
        new_l = SimpleNamespace(id="l-dev", display_name="DevLearner", grade=3, language="en", streak_days=2)
        mock_runtime.learner_repo.create.return_value = new_l

        dev_session = await create_dev_session_impl(mock_resp, mock_db, mock_runtime)
        assert "access_token" in dev_session
        assert dev_session["guardian_id"] == "g-dev"
        assert dev_session["learner"]["id"] == "l-dev"

    # 4. login_impl
    login_req = LoginRequest(email="guardian@example.com", password="Password123!")
    mock_req = MagicMock()

    # Invalid password
    mock_runtime.guardian_repo.get_by_email_hash.return_value = SimpleNamespace(
        id="g-1",
        password_hash="different_hash",
        role=UserRole.PARENT,
    )
    with patch("app.services.auth_lifecycle_impl.FourthEstateService.auth_event", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_bad_pass:
            await login_impl(mock_req, login_req, mock_resp, mock_db, mock_runtime)
        assert exc_bad_pass.value.status_code == 401

    # Valid password
    with patch("app.services.auth_lifecycle_impl.verify_password", return_value=True), \
         patch("app.services.auth_lifecycle_impl.store_refresh_token", new_callable=AsyncMock), \
         patch("app.services.auth_lifecycle_impl.FourthEstateService.auth_event", new_callable=AsyncMock):
        tok_resp = await login_impl(mock_req, login_req, mock_resp, mock_db, mock_runtime)
        assert tok_resp.access_token is not None

    # 5. refresh_impl
    # No refresh token
    with pytest.raises(HTTPException) as exc_no_ref:
        await refresh_impl(mock_req, mock_resp, None, mock_db, cookie_refresh=None, auth_runtime=mock_runtime)
    assert exc_no_ref.value.status_code == 401

    # Inactive guardian
    ref_req = RefreshRequest(refresh_token="rt-valid")
    with patch("app.services.auth_lifecycle_impl.consume_refresh_token", AsyncMock(return_value={"sub": "g-1", "family": "fam-1"})):
        mock_runtime.guardian_repo.get_by_id.return_value = SimpleNamespace(id="g-1", is_active=False)
        with pytest.raises(HTTPException) as exc_inactive:
            await refresh_impl(mock_req, mock_resp, ref_req, mock_db, cookie_refresh=None, auth_runtime=mock_runtime)
        assert exc_inactive.value.status_code == 401

        # Active guardian
        mock_runtime.guardian_repo.get_by_id.return_value = SimpleNamespace(
            id="g-1",
            is_active=True,
            role=UserRole.PARENT,
            subscription_tier="free",
        )
        mock_runtime.guardian_learner_ids = AsyncMock(return_value=["l-1"])
        with patch("app.services.auth_lifecycle_impl.store_refresh_token", new_callable=AsyncMock), \
             patch("app.services.auth_lifecycle_impl.FourthEstateService.auth_event", new_callable=AsyncMock):
            ref_ok = await refresh_impl(mock_req, mock_resp, ref_req, mock_db, cookie_refresh=None, auth_runtime=mock_runtime)
            assert ref_ok.access_token is not None

    # 6. register_impl
    reg_req = RegisterRequest(
        email="new@example.com",
        password="K9#mX7$vL2!qR9",
        display_name="New Guardian",
        role="parent",
    )
    # Email already exists
    mock_runtime.guardian_repo.get_by_email_hash.return_value = SimpleNamespace(id="existing")
    with pytest.raises(HTTPException) as exc_reg_exist:
        await register_impl(mock_req, reg_req, mock_resp, mock_db, mock_runtime)
    assert exc_reg_exist.value.status_code == 409

    # New email
    mock_runtime.guardian_repo.get_by_email_hash.return_value = None
    mock_runtime.guardian_repo.create.return_value = SimpleNamespace(
        id="g-new",
        role=UserRole.PARENT,
        subscription_tier="free",
    )
    with patch("app.services.auth_lifecycle_impl.store_refresh_token", new_callable=AsyncMock), \
         patch("app.services.auth_lifecycle_impl.FourthEstateService.auth_event", new_callable=AsyncMock):
        reg_ok = await register_impl(mock_req, reg_req, mock_resp, mock_db, mock_runtime)
        assert reg_ok.access_token is not None
