"""Comprehensive branch coverage expansion for POPIADataRightsService."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException

from app.api_v2_deps.auth import AuthContext
from app.models import ErasureRequest
from app.services.popia_service import (
    ERASURE_METHOD_PHYSICAL,
    ERASURE_METHOD_PURGE,
    ERASURE_METHOD_SOFT,
    ERASURE_STATE_CANCELLED,
    ERASURE_STATE_EXECUTED,
    ERASURE_STATE_REQUESTED,
    ERASURE_STATE_SCHEDULED,
    ERASURE_STATE_VERIFIED,
    POPIADataRightsService,
    _current_user_role,
    _maybe_await,
    _now,
)


@pytest.mark.asyncio
async def test_current_user_role_and_helpers():
    # AuthContext with roles list
    ctx1 = AuthContext(
        sub="user-1",
        roles=["admin"],
        permissions=["read"],
        tenant_id="tenant-1",
        user_id="user-1",
        email="test@test.com",
        token_type="access",
        jti="jti-1",
        raw_claims={"role": "ignored"},
    )
    assert _current_user_role(ctx1) == "admin"

    # AuthContext with empty roles list, checking raw_claims
    ctx2 = AuthContext(
        sub="user-2",
        roles=[],
        permissions=["read"],
        tenant_id="tenant-1",
        user_id="user-2",
        email="test@test.com",
        token_type="access",
        jti="jti-2",
        raw_claims={"role": "parent"},
    )
    assert _current_user_role(ctx2) == "parent"

    # Dict role
    assert _current_user_role({"role": "Educator"}) == "educator"

    # _maybe_await sync vs async
    assert await _maybe_await("sync_val") == "sync_val"


@pytest.mark.asyncio
async def test_load_learner_for_read_and_write_not_found():
    db = AsyncMock()
    svc = POPIADataRightsService(db)
    svc.learners = SimpleNamespace(get_by_id=AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc1:
        await svc.load_learner_for_read("learner-missing", {"sub": "admin-1", "role": "admin"})
    assert exc1.value.status_code == 404

    with pytest.raises(HTTPException) as exc2:
        await svc.load_learner_for_write("learner-missing", {"sub": "admin-1", "role": "admin"})
    assert exc2.value.status_code == 404


@pytest.mark.asyncio
async def test_erasure_status_branches():
    db = AsyncMock()
    svc = POPIADataRightsService(db)

    learner = SimpleNamespace(
        id="learner-1",
        guardian_id="guardian-1",
        pseudonym_id="pseudo-1",
        is_deleted=False,
    )
    svc.learners = SimpleNamespace(get_by_id=AsyncMock(return_value=learner))

    # 1. No erasure request found -> default status
    db.scalar = AsyncMock(return_value=None)
    status_none = await svc.erasure_status("learner-1", {"sub": "guardian-1", "role": "admin"})
    assert status_none["status"] == "pending_review"

    # 2. Erasure request found, unauthorized user -> 403
    req = ErasureRequest(
        id="req-1",
        learner_id="learner-1",
        requester_id="guardian-1",
        requester_role="parent",
        state=ERASURE_STATE_REQUESTED,
        reason="guardian_request",
        legal_hold=False,
        created_at=_now(),
        grace_period_end_at=_now() + timedelta(days=30),
    )
    db.scalar = AsyncMock(return_value=req)
    with pytest.raises(HTTPException) as exc:
        await svc.erasure_status("learner-1", {"sub": "unauthorized-user", "role": "student"})
    assert exc.value.status_code == 403

    # 3. Authorized user (admin or requester) -> returns details
    res = await svc.erasure_status("learner-1", {"sub": "admin-1", "role": "admin"})
    assert res["request_id"] == "req-1"
    assert res["state"] == ERASURE_STATE_REQUESTED
    assert res["requires_admin_review"] is True


@pytest.mark.asyncio
async def test_cancel_erasure_authorized_and_unauthorized():
    db = AsyncMock()
    svc = POPIADataRightsService(db)

    learner = SimpleNamespace(
        id="learner-1",
        guardian_id="guardian-1",
        pseudonym_id="pseudo-1",
        is_deleted=True,
        display_name="[erased]",
        deletion_requested_at=_now(),
    )
    svc.learners = MagicMock()
    svc.learners.get_by_id = AsyncMock(return_value=learner)
    svc.audit = AsyncMock()

    # Mock load_learner_for_write directly to test service authorization on cancel_erasure
    svc.load_learner_for_write = AsyncMock(return_value=learner)

    req = ErasureRequest(
        id="req-1",
        learner_id="learner-1",
        requester_id="guardian-1",
        requester_role="parent",
        state=ERASURE_STATE_REQUESTED,
        reason="guardian_request",
    )
    db.scalar = AsyncMock(return_value=req)

    # 1. Unauthorized cancel (different non-admin user) -> 403
    with pytest.raises(HTTPException) as exc:
        await svc.cancel_erasure("learner-1", {"sub": "guardian-other", "role": "parent"})
    assert exc.value.status_code == 403

    # 2. Authorized cancel by requester -> resets learner, state = cancelled
    cancel_res = await svc.cancel_erasure("learner-1", {"sub": "guardian-1", "role": "parent"})
    assert cancel_res["state"] == ERASURE_STATE_CANCELLED
    assert learner.is_deleted is False
    assert learner.display_name == "Restored"
    svc.audit.append.assert_called_once()


@pytest.mark.asyncio
async def test_preflight_erasure_checks_and_export_payload_deep():
    db = AsyncMock()
    svc = POPIADataRightsService(db)

    learner = SimpleNamespace(
        id="learner-1",
        guardian_id="guardian-1",
        pseudonym_id="pseudo-1",
        display_name="Learner One",
        grade=5,
        language="en",
        archetype="visual",
        theta=0.5,
        xp=100,
        streak_days=3,
        last_active=_now(),
        is_deleted=False,
        deletion_requested_at=None,
        created_at=_now(),
        updated_at=_now(),
    )

    # 1. _preflight_erasure_checks
    preflight = await svc._preflight_erasure_checks(learner, "guardian-1", "parent")
    assert isinstance(preflight, dict)
    assert "export_offered" in preflight

    # 2. _export_payload with full populated related models
    diag = SimpleNamespace(
        id="diag-1", theta_before=0.0, theta_after=0.5, se_estimate=0.2, session_state="completed",
        gap_topics=["Fractions"], misconception_tags=["tag1"], items_served=5, theta_history=[0.0, 0.5],
        items_correct=4, completed_at=_now(), created_at=_now()
    )
    lesson = SimpleNamespace(
        id="les-1", knowledge_gap_id="gap-1", grade=5, subject="Math", topic="Fractions", language="en",
        archetype="visual", content="Body", caps_ref="5.M.1", caps_reference="5.M.1", term=1, subtopic="Fractions",
        learning_objectives=["Obj"], explanation="Exp", worked_examples=[], practice_questions=[], answer_key=[],
        remediation_hints=[], difficulty_level=1, language_level="en", safety_classification="safe",
        pii_check_passed=True, answer_key_verified=True, alignment_confidence=0.9, quality_score=0.9,
        trust_label="verified", review_status="approved", reviewed_at=_now(), prompt_template_version="v1",
        provider="anthropic", model_version="sonnet", generation_latency_ms=100, token_usage={},
        variant_type="standard", llm_provider="anthropic", served_from_cache=False, feedback_score=5,
        completed_at=_now(), created_at=_now()
    )
    gap = SimpleNamespace(id="gap-1", grade=5, subject="Math", topic="Fractions", severity=0.5, resolved=False, created_at=_now())
    consent = SimpleNamespace(id="con-1", guardian_id="guardian-1", policy_version="v1", is_active=True, revoked_at=None, granted_at=_now(), expires_at=_now() + timedelta(days=365), created_at=_now(), updated_at=_now())
    subj_m = SimpleNamespace(id="sm-1", subject="Math", topic="Fractions", theta=0.5, standard_error=0.2, created_at=_now(), last_updated=_now())
    top_m = SimpleNamespace(id="tm-1", caps_ref="5.M.1", mastery_score=0.8, mastery_label="mastered", theta_estimate=0.5, theta_se=0.2, last_updated_at=_now())
    m_snap = SimpleNamespace(id="ms-1", caps_ref="5.M.1", mastery_score=0.8, mastery_label="mastered", theta_estimate=0.5, theta_se=0.2, practice_accuracy=0.8, trigger="practice", snapshot_at=_now())
    pq = SimpleNamespace(id="pq-1", caps_ref="5.M.1", item_id="item-1", scheduled_at=_now(), completed_at=_now(), response="A", correct=True)
    sr = SimpleNamespace(id="sr-1", caps_ref="5.M.1", next_review_at=_now(), interval_days=3, easiness_factor=2.5, updated_at=_now())
    guard = SimpleNamespace(id="guardian-1", display_name="Parent One", role="parent", subscription_tier="pro", is_active=True, email_verified=True, created_at=_now(), updated_at=_now())
    audit_e = SimpleNamespace(id="ae-1", event_type="login", resource_id="learner-1", payload={}, previous_event_hash="h1", event_hash="h2", hmac_signature="sig", created_at=_now())

    def make_scalars_result(items):
        mock_res = MagicMock()
        mock_res.all.return_value = items
        return mock_res

    db.scalars = AsyncMock(side_effect=[
        make_scalars_result([diag]),
        make_scalars_result([lesson]),
        make_scalars_result([gap]),
        make_scalars_result([consent]),
        make_scalars_result([subj_m]),
        make_scalars_result([top_m]),
        make_scalars_result([m_snap]),
        make_scalars_result([pq]),
        make_scalars_result([sr]),
        make_scalars_result([audit_e]),
    ])
    db.get = AsyncMock(return_value=guard)

    payload = await svc._export_payload(learner)
    assert payload["learner"]["display_name"] == "Learner One"
    assert len(payload["diagnostic_sessions"]) == 1
    assert len(payload["lessons"]) == 1
    assert len(payload["knowledge_gaps"]) == 1
    assert len(payload["parental_consents"]) == 1
    assert payload["guardian"]["display_name"] == "Parent One"




@pytest.mark.asyncio
async def test_execute_erasure_validation_and_failures():
    db = AsyncMock()
    svc = POPIADataRightsService(db)
    svc.learners = SimpleNamespace(
        get_by_id=AsyncMock(),
        soft_delete=AsyncMock(),
        delete_by_id=AsyncMock(),
        purge_personal_data=AsyncMock(),
    )
    svc.audit = AsyncMock()

    # 1. Request not found -> 404
    db.scalar = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc:
        await svc.execute_erasure("req-missing", {"sub": "admin-1", "role": "admin"})
    assert exc.value.status_code == 404

    # 2. Unauthorized requester -> 403
    req = ErasureRequest(
        id="req-1",
        learner_id="learner-1",
        requester_id="guardian-1",
        state=ERASURE_STATE_VERIFIED,
        admin_override=False,
        grace_period_end_at=_now() - timedelta(days=1),
        legal_hold=False,
        export_offered=True,
    )
    db.scalar = AsyncMock(return_value=req)
    with pytest.raises(HTTPException) as exc:
        await svc.execute_erasure("req-1", {"sub": "other-user", "role": "parent"})
    assert exc.value.status_code == 403

    # 3. Invalid state (not verified/scheduled) -> 409
    req.state = ERASURE_STATE_REQUESTED
    with pytest.raises(HTTPException) as exc:
        await svc.execute_erasure("req-1", {"sub": "admin-1", "role": "admin"})
    assert exc.value.status_code == 409

    # 4. Grace period has not elapsed (without admin override) -> 403
    req.state = ERASURE_STATE_VERIFIED
    req.grace_period_end_at = _now() + timedelta(days=10)
    with pytest.raises(HTTPException) as exc:
        await svc.execute_erasure("req-1", {"sub": "admin-1", "role": "admin"})
    assert exc.value.status_code == 403

    # 5. Legal hold active -> 403
    req.grace_period_end_at = _now() - timedelta(days=1)
    req.legal_hold = True
    with pytest.raises(HTTPException) as exc:
        await svc.execute_erasure("req-1", {"sub": "guardian-1", "role": "parent"})
    assert exc.value.status_code == 403

    # 6. Export neither offered nor waived -> 403
    req.legal_hold = False
    req.export_offered = False
    req.export_waived = False
    with pytest.raises(HTTPException) as exc:
        await svc.execute_erasure("req-1", {"sub": "guardian-1", "role": "parent"})
    assert exc.value.status_code == 403

    # 7. Learner not found -> 404
    req.export_offered = True
    svc.learners.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc:
        await svc.execute_erasure("req-1", {"sub": "guardian-1", "role": "parent"})
    assert exc.value.status_code == 404

    # 8. Invalid method -> 422
    learner = SimpleNamespace(id="learner-1", pseudonym_id="p-1", guardian_id="guardian-1")
    svc.learners.get_by_id = AsyncMock(return_value=learner)
    with pytest.raises(HTTPException) as exc:
        await svc.execute_erasure("req-1", {"sub": "guardian-1", "role": "parent"}, method="invalid_method")
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_execute_erasure_methods_success():
    db = AsyncMock()
    svc = POPIADataRightsService(db)

    learner = SimpleNamespace(
        id="learner-1",
        pseudonym_id="p-1",
        guardian_id="guardian-1",
        is_deleted=True,
        display_name="[erased]",
    )
    svc.learners = SimpleNamespace(
        get_by_id=AsyncMock(return_value=learner),
        soft_delete=AsyncMock(),
        delete_by_id=AsyncMock(),
        purge_personal_data=AsyncMock(),
    )
    svc.audit = AsyncMock()

    # 1. Soft delete method
    req_soft = ErasureRequest(
        id="req-soft",
        learner_id="learner-1",
        requester_id="guardian-1",
        state=ERASURE_STATE_VERIFIED,
        admin_override=False,
        grace_period_end_at=_now() - timedelta(days=1),
        legal_hold=False,
        export_offered=True,
    )
    db.scalar = AsyncMock(return_value=req_soft)

    res_soft = await svc.execute_erasure("req-soft", {"sub": "guardian-1", "role": "parent"}, method=ERASURE_METHOD_SOFT)
    assert res_soft["state"] == ERASURE_STATE_EXECUTED
    assert res_soft["execution_method"] == ERASURE_METHOD_SOFT
    svc.learners.soft_delete.assert_called_with("learner-1")

    # 2. Physical delete method (admin override bypasses grace period)
    req_phys = ErasureRequest(
        id="req-phys",
        learner_id="learner-1",
        requester_id="guardian-1",
        state=ERASURE_STATE_SCHEDULED,
        admin_override=True,
        grace_period_end_at=_now() + timedelta(days=20),
        legal_hold=True,
        export_waived=True,
    )
    db.scalar = AsyncMock(return_value=req_phys)

    # In postflight verification for physical deletion, learner is None
    svc.learners.get_by_id = AsyncMock(side_effect=[learner, None])

    res_phys = await svc.execute_erasure("req-phys", {"sub": "admin-1", "role": "admin"}, method=ERASURE_METHOD_PHYSICAL)
    assert res_phys["state"] == ERASURE_STATE_EXECUTED
    assert res_phys["execution_method"] == ERASURE_METHOD_PHYSICAL
    svc.learners.delete_by_id.assert_called_with("learner-1")

    # 3. Purge method
    req_purge = ErasureRequest(
        id="req-purge",
        learner_id="learner-1",
        requester_id="guardian-1",
        state=ERASURE_STATE_SCHEDULED,
        admin_override=False,
        grace_period_end_at=_now() - timedelta(days=1),
        legal_hold=False,
        export_offered=True,
    )
    db.scalar = AsyncMock(return_value=req_purge)
    svc.learners.get_by_id = AsyncMock(side_effect=[learner, None])

    res_purge = await svc.execute_erasure("req-purge", {"sub": "guardian-1", "role": "parent"}, method=ERASURE_METHOD_PURGE)
    assert res_purge["state"] == ERASURE_STATE_EXECUTED
    assert res_purge["execution_method"] == ERASURE_METHOD_PURGE
    svc.learners.purge_personal_data.assert_called_with("learner-1")


@pytest.mark.asyncio
async def test_requires_admin_review():
    db = AsyncMock()
    svc = POPIADataRightsService(db)
    learner = SimpleNamespace(id="learner-1")
    assert await svc.requires_admin_review(learner) is False
