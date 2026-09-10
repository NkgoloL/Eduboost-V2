from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi import HTTPException

from app.api_v2_deps.auth import AuthContext, TokenType, UserRole
from app.api_v2_routers import (
    commercial_launch,
    controlled_beta,
    content_quality,
    observability_sre,
    performance_scale_cost,
    production_release,
    security_assurance,
    privacy_operations,
    consent_renewal,
    audit,
    jobs,
    system,
    ether,
    study_plans,
    admin_etl,
    assessments,
    billing,
    onboarding,
    learner_content,
    vertical_journey,
)
from app.domain.api_v2_models import (
    StudyPlanGenerateRequest,
    AssessmentAttemptRequest,
    AssessmentAttemptResponseItem,
)
from app.domain.schemas import OnboardingSubmit, OnboardingAnswer


@pytest.fixture
def mock_auth_context() -> AuthContext:
    return AuthContext(
        user_id="user_test_123",
        roles=[UserRole.PARENT, UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={},
        jti="jti_123",
    )


@pytest.mark.asyncio
async def test_commercial_launch_router():
    r1 = await commercial_launch.get_commercial_launch_readiness()
    assert isinstance(r1, dict)
    assert "report_id" in r1 or "readiness" in r1 or "status" in r1 or len(r1) > 0

    r2 = await commercial_launch.get_commercial_runtime_audit_remediation()
    assert isinstance(r2, dict)
    assert len(r2) > 0


@pytest.mark.asyncio
async def test_controlled_beta_router():
    r1 = await controlled_beta.get_controlled_beta_preflight()
    assert isinstance(r1, dict)
    assert len(r1) > 0

    r2 = await controlled_beta.get_controlled_beta_final_authorisation()
    assert isinstance(r2, dict)
    assert len(r2) > 0


@pytest.mark.asyncio
async def test_content_quality_router():
    r1 = await content_quality.get_grade4_maths_content_quality_readiness()
    assert isinstance(r1, dict)
    assert len(r1) > 0

    r2 = await content_quality.get_grade4_maths_content_quality_final_acceptance()
    assert isinstance(r2, dict)
    assert len(r2) > 0


@pytest.mark.asyncio
async def test_observability_sre_router():
    r1 = await observability_sre.get_observability_sre_readiness()
    assert isinstance(r1, dict)
    assert len(r1) > 0

    r2 = await observability_sre.get_observability_sre_final_assurance()
    assert isinstance(r2, dict)
    assert len(r2) > 0


@pytest.mark.asyncio
async def test_performance_scale_cost_router():
    r1 = await performance_scale_cost.get_performance_scale_cost_readiness()
    assert isinstance(r1, dict)
    assert len(r1) > 0

    r2 = await performance_scale_cost.get_performance_scale_cost_final_assurance()
    assert isinstance(r2, dict)
    assert len(r2) > 0


@pytest.mark.asyncio
async def test_production_release_router():
    r1 = await production_release.get_production_release_preflight()
    assert isinstance(r1, dict)
    assert len(r1) > 0

    r2 = await production_release.get_true_state_runtime_baseline()
    assert isinstance(r2, dict)
    assert len(r2) > 0


@pytest.mark.asyncio
async def test_security_assurance_router():
    r1 = await security_assurance.get_security_assurance_readiness()
    assert isinstance(r1, dict)
    assert len(r1) > 0

    r2 = await security_assurance.get_security_final_assurance()
    assert isinstance(r2, dict)
    assert len(r2) > 0


@pytest.mark.asyncio
async def test_privacy_operations_router():
    r1 = await privacy_operations.get_popia_live_data_operations_readiness()
    assert isinstance(r1, dict)
    assert len(r1) > 0

    r2 = await privacy_operations.get_popia_live_data_operations_final_assurance()
    assert isinstance(r2, dict)
    assert len(r2) > 0


@pytest.mark.asyncio
async def test_consent_renewal_router(monkeypatch, mock_auth_context):
    mock_enqueue = AsyncMock(return_value="job_reminders_001")
    monkeypatch.setattr(consent_renewal, "enqueue_durable", mock_enqueue)

    res = await consent_renewal.trigger_renewal_reminders(mock_auth_context)
    assert res.job_id == "job_reminders_001"
    assert res.operation == "consent_renewal_reminders"
    assert res.status == "queued"


@pytest.mark.asyncio
async def test_audit_router(monkeypatch):
    mock_events = [{"event_id": "e1", "action": "login"}]
    monkeypatch.setattr(audit.AuditService, "get_recent_events", AsyncMock(return_value=mock_events))

    res1 = await audit.get_audit_feed(limit=10)
    assert res1 == mock_events

    res2 = await audit.get_audit_feed_alias(limit=5)
    assert res2 == mock_events


@pytest.mark.asyncio
async def test_jobs_router(monkeypatch, mock_auth_context):
    # 404 when not found
    monkeypatch.setattr(jobs, "get_job", AsyncMock(return_value=None))
    with pytest.raises(HTTPException) as exc_info:
        await jobs.get_job_status("nonexistent_job", mock_auth_context)
    assert exc_info.value.status_code == 404

    # Found job
    job_data = {
        "job_id": "job_123",
        "operation": "test_op",
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "payload": {},
        "result": {"status": "ok"},
        "error": None,
    }
    monkeypatch.setattr(jobs, "get_job", AsyncMock(return_value=job_data))
    res = await jobs.get_job_status("job_123", mock_auth_context)
    assert res.job_id == "job_123"
    assert res.status == "completed"


@pytest.mark.asyncio
async def test_system_router():
    h = await system.get_health()
    assert h["status"] == "ok"

    p = await system.get_pillars()
    assert "pillars" in p

    s = await system.get_schema_status()
    assert s["status"] == "ok"

    c = await system.get_capabilities()
    assert isinstance(c, dict)


@pytest.mark.asyncio
async def test_ether_router(mock_auth_context):
    q = await ether.get_questions(mock_auth_context)
    assert isinstance(q, list)
    assert len(q) > 0


@pytest.mark.asyncio
async def test_study_plans_router(monkeypatch, mock_auth_context):
    monkeypatch.setattr(study_plans, "require_learner_write_for_current_user", MagicMock())
    monkeypatch.setattr(study_plans, "require_active_consent_for_current_user", AsyncMock())
    monkeypatch.setattr(study_plans, "build_runtime_kg_study_plan_payload", AsyncMock(return_value={"kg": "ready"}))
    monkeypatch.setattr(study_plans, "enqueue_durable", AsyncMock(return_value="study_job_1"))

    req = StudyPlanGenerateRequest(gap_ratio=0.5)
    db = AsyncMock()
    res = await study_plans.generate_study_plan("learner_1", req, mock_auth_context, db)
    assert res.job_id == "study_job_1"
    assert res.operation == "study_plan_generation"


@pytest.mark.asyncio
async def test_admin_etl_router():
    st = await admin_etl.etl_admin_status()
    assert st.data is not None and st.data["status"] == "available"

    docs = await admin_etl.list_etl_documents()
    assert len(docs) > 0

    doc = await admin_etl.get_etl_document("caps-grade4-maths-topic-map")
    assert doc["document_id"] == "caps-grade4-maths-topic-map"

    doc_missing = await admin_etl.get_etl_document("unknown")
    assert doc_missing["status"] == "not_found"

    chunks = await admin_etl.get_etl_document_chunks("doc1")
    assert len(chunks) == 1

    audit_logs = await admin_etl.get_etl_document_audit("doc1")
    assert len(audit_logs) == 1

    q = await admin_etl.get_etl_review_queue()
    assert q == []

    qual = await admin_etl.get_etl_quality("doc1")
    assert qual["document_id"] == "doc1"

    s_empty = await admin_etl.search_etl("")
    assert s_empty["results"] == []

    s_res = await admin_etl.search_etl("caps")
    assert len(s_res["results"]) > 0

    ds = await admin_etl.list_etl_datasets()
    assert len(ds) == 1

    metrics = await admin_etl.get_etl_metrics()
    assert "documents_indexed" in metrics


@pytest.mark.asyncio
async def test_assessments_router(monkeypatch, mock_auth_context):
    mock_service = MagicMock()
    mock_service.with_db.return_value = mock_service
    mock_service.list_assessments = AsyncMock(return_value=[{"id": "a1"}])
    mock_service.submit_attempt = AsyncMock(return_value={"score": 100})
    monkeypatch.setattr(assessments, "AssessmentServiceV2", lambda: mock_service)
    monkeypatch.setattr(assessments, "require_learner_write_for_current_user", MagicMock())
    monkeypatch.setattr(assessments, "require_active_consent_for_current_user", AsyncMock())

    db = AsyncMock()
    # 1. list_assessments
    res_list = await assessments.list_assessments(limit=10, offset=0, _=mock_auth_context, db=db)
    assert res_list == [{"id": "a1"}]

    # 2. submit_attempt
    attempt_req = AssessmentAttemptRequest(
        learner_id="learner_1",
        responses=[AssessmentAttemptResponseItem(item_id="i1", answer="4")],
        time_taken_seconds=60,
    )
    res_sub = await assessments.submit_attempt("a1", attempt_req, mock_auth_context, db)
    assert res_sub == {"score": 100}


@pytest.mark.asyncio
async def test_billing_router(monkeypatch, mock_auth_context):
    monkeypatch.setattr(billing, "assert_billing_authorized", MagicMock())
    mock_stripe = MagicMock()
    mock_stripe.create_checkout_session = AsyncMock(return_value="https://checkout.stripe.com/test")
    mock_stripe.handle_webhook = AsyncMock(return_value={"status": "handled"})
    monkeypatch.setattr(billing, "StripeService", lambda db: mock_stripe)

    db = AsyncMock()
    # 1. create_checkout
    res_co = await billing.create_checkout(db=db, current_user=mock_auth_context, _auth_guard=None)
    assert res_co.checkout_url == "https://checkout.stripe.com/test"

    # 2. webhook
    mock_req = AsyncMock()
    mock_req.body = AsyncMock(return_value=b"payload_bytes")
    mock_audit = AsyncMock()
    res_wh = await billing.stripe_webhook(
        request=mock_req,
        db=db,
        stripe_signature="sig_test",
        audit=mock_audit,
        _auth_guard=None,
    )
    assert res_wh == {"status": "handled"}
    mock_audit.record.assert_awaited_once_with("STRIPE_WEBHOOK", payload={"status": "handled"})


@pytest.mark.asyncio
async def test_onboarding_router(monkeypatch, mock_auth_context):
    # 1. get_questions
    qs = await onboarding.get_onboarding_questions(mock_auth_context)
    assert len(qs) > 0

    # 2. submit_onboarding learner not found
    mock_learner_svc = MagicMock()
    mock_learner_svc.get_learner_summary = AsyncMock(return_value=None)
    monkeypatch.setattr(onboarding, "LearnerService", lambda db: mock_learner_svc)

    db = AsyncMock()
    submit_body = OnboardingSubmit(
        learner_id="learner_unknown",
        answers=[OnboardingAnswer(question_id=1, answer="visual")],
    )
    with pytest.raises(HTTPException) as exc:
        await onboarding.submit_onboarding(submit_body, db, mock_auth_context)
    assert exc.value.status_code == 404

    # 3. submit_onboarding success
    mock_learner_svc.get_learner_summary = AsyncMock(return_value={"id": "learner_1"})
    mock_learner_svc.process_onboarding = AsyncMock(
        return_value={
            "learner_id": "learner_1",
            "archetype": "Visual",
            "description": "Visual learner",
            "probabilities": {"visual": 0.9},
        }
    )
    monkeypatch.setattr(onboarding, "require_learner_write_for_current_user", MagicMock())
    monkeypatch.setattr(onboarding, "require_active_consent_for_current_user", AsyncMock())

    submit_ok = OnboardingSubmit(
        learner_id="learner_1",
        answers=[OnboardingAnswer(question_id=1, answer="visual")],
    )
    res = await onboarding.submit_onboarding(submit_ok, db, mock_auth_context)
    assert res.learner_id == "learner_1"
    assert res.archetype == "Visual"


@pytest.mark.asyncio
async def test_learner_content_router(mock_auth_context):
    assert learner_content.get_learner_read_service() is not None

    mock_svc = MagicMock()
    mock_svc.get_scope_content_summary = AsyncMock(return_value={"summary": "ok"})
    mock_svc.get_diagnostic_items = AsyncMock(return_value=[{"item_id": "item1"}])
    mock_svc.get_lessons = AsyncMock(return_value=[{"lesson_id": "lesson1"}])

    db = AsyncMock()

    r1 = await learner_content.get_scope_summary("scope1", mock_auth_context, db, mock_svc)
    assert r1 == {"summary": "ok"}

    r2 = await learner_content.get_diagnostic_items("scope1", mock_auth_context, db, mock_svc)
    assert r2 == [{"item_id": "item1"}]

    r3 = await learner_content.get_lessons("scope1", mock_auth_context, db, mock_svc)
    assert r3 == [{"lesson_id": "lesson1"}]

    r4 = await learner_content.get_diagnostic_items_by_caps_ref("scope1", "ref1", mock_auth_context, db, mock_svc)
    assert r4 == [{"item_id": "item1"}]

    r5 = await learner_content.get_lessons_by_caps_ref("scope1", "ref1", mock_auth_context, db, mock_svc)
    assert r5 == [{"lesson_id": "lesson1"}]


@pytest.mark.asyncio
async def test_vertical_journey_router(monkeypatch, mock_auth_context):
    # 1. 404 when learner not found
    mock_learner_svc = MagicMock()
    mock_learner_svc.repository.get_by_id = AsyncMock(return_value=None)
    monkeypatch.setattr(vertical_journey, "LearnerService", lambda db: mock_learner_svc)

    db = AsyncMock()
    with pytest.raises(HTTPException) as exc:
        await vertical_journey.get_learner_vertical_journey("learner_none", db, mock_auth_context)
    assert exc.value.status_code == 404

    # 2. Success with active consent
    learner_obj = MagicMock(id="learner_1", xp=100)
    mock_learner_svc.repository.get_by_id = AsyncMock(return_value=learner_obj)
    monkeypatch.setattr(vertical_journey, "require_learner_read_for_current_user", MagicMock())

    mock_consent_svc = MagicMock()
    mock_consent_svc.consent_decision = AsyncMock(return_value=MagicMock(active=True))
    monkeypatch.setattr(vertical_journey, "ConsentService", lambda db: mock_consent_svc)

    orig_count = vertical_journey._count
    monkeypatch.setattr(vertical_journey, "_count", AsyncMock(return_value=2))
    monkeypatch.setattr(
        vertical_journey,
        "build_runtime_kg_study_plan_payload",
        AsyncMock(return_value={"status": "ready"}),
    )

    res = await vertical_journey.get_learner_vertical_journey("learner_1", db, mock_auth_context)
    assert isinstance(res, dict)
    assert "learner_id" in res
    assert res["learner_id"] == "learner_1"

    # 3. _count helper
    mock_db_scalar = AsyncMock()
    mock_db_scalar.scalar = AsyncMock(return_value=5)
    c1 = await orig_count(mock_db_scalar, "stmt")
    assert c1 == 5

    mock_db_scalar.scalar = AsyncMock(return_value=None)
    c0 = await orig_count(mock_db_scalar, "stmt")
    assert c0 == 0
