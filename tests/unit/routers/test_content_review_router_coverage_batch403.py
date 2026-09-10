from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest
from fastapi import HTTPException

from app.api_v2_deps.auth import AuthContext, TokenType, UserRole
from app.api_v2_routers import content_review
from app.domain.content_review_schemas import (
    AnswerKeyVerificationRequest,
    ArtifactPublishRequest,
    ArtifactRevisionRequest,
    QuarantineRequest,
    ReviewAssignmentAcceptRequest,
    ReviewAssignmentCreateRequest,
    ReviewAssignmentReassignRequest,
    ReviewDecisionRequest,
)
from app.models.content_factory import ContentReviewAction
from app.services.content_review_governance import ReviewConflictError


@pytest.fixture
def mock_lead_actor() -> content_review.ReviewActor:
    return content_review.ReviewActor(
        user_id="lead_01",
        permissions=frozenset({
            "assign",
            "assignment_accept",
            "review",
            "quarantine",
            "revise",
            "publish",
            "answer_key_verify",
            "history_read",
            "stale_read",
        }),
        competencies=("mathematics", "science"),
    )


@pytest.mark.asyncio
async def test_get_review_actor_branches():
    # 1. raw_permissions & raw_competencies as strings, curriculum_lead role
    auth_lead = AuthContext(
        user_id="lead_u",
        roles=[UserRole.TEACHER],
        token_type=TokenType.ACCESS,
        raw_claims={
            "review_permissions": "custom_perm",
            "reviewer_competencies": "algebra",
            "content_review_role": "curriculum_lead",
        },
        jti="jti_lead",
    )
    actor_lead = await content_review.get_review_actor(auth_lead)
    assert "publish" in actor_lead.permissions
    assert "custom_perm" in actor_lead.permissions
    assert "algebra" in actor_lead.competencies

    # 2. senior_reviewer role
    auth_senior = AuthContext(
        user_id="sen_u",
        roles=[],
        token_type=TokenType.ACCESS,
        raw_claims={"content_review_role": "senior_reviewer"},
        jti="jti_sen",
    )
    actor_sen = await content_review.get_review_actor(auth_senior)
    assert "assign" in actor_sen.permissions
    assert "publish" not in actor_sen.permissions

    # 3. admin role
    auth_admin = AuthContext(
        user_id="admin_u",
        roles=[UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={},
        jti="jti_adm",
    )
    actor_admin = await content_review.get_review_actor(auth_admin)
    assert "assign" in actor_admin.permissions
    assert "quarantine" in actor_admin.permissions

    # 4. no permissions -> 403
    auth_empty = AuthContext(
        user_id="empty_u",
        roles=[],
        token_type=TokenType.ACCESS,
        raw_claims={},
        jti="jti_emp",
    )
    with pytest.raises(HTTPException) as exc_emp:
        await content_review.get_review_actor(auth_empty)
    assert exc_emp.value.status_code == 403


def test_get_governance_service_and_helpers():
    svc = content_review.get_governance_service()
    assert svc is not None

    # test ReviewActor.require denial
    actor_empty = content_review.ReviewActor(
        user_id="actor_no_perm",
        permissions=frozenset(),
        competencies=(),
    )
    with pytest.raises(HTTPException) as exc_req:
        actor_empty.require("assign")
    assert exc_req.value.status_code == 403

    # test _value helper with and without .value
    enum_like = SimpleNamespace(value="active_val")
    assert content_review._value(enum_like) == "active_val"
    assert content_review._value("plain_val") == "plain_val"


@pytest.mark.asyncio
async def test_assign_reviewers(mock_lead_actor):
    session = AsyncMock()
    service = MagicMock()
    art_id = uuid4()
    asgn_id = uuid4()

    req = ReviewAssignmentCreateRequest(
        reviewer_ids=["rev_1", "rev_2"],
        priority="high",
    )

    # Success
    mock_res = SimpleNamespace(
        assignment_ids=[asgn_id],
        artifact_id=art_id,
        artifact_version=1,
        assigned_count=2,
    )
    service.assign_reviewers = AsyncMock(return_value=mock_res)
    res = await content_review.assign_reviewers(art_id, req, session, mock_lead_actor, service)
    assert res.assigned_count == 2

    # Error
    service.assign_reviewers = AsyncMock(side_effect=ValueError("Invalid reviewers"))
    with pytest.raises(HTTPException) as exc:
        await content_review.assign_reviewers(art_id, req, session, mock_lead_actor, service)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_accept_assignment(mock_lead_actor):
    session = AsyncMock()
    service = MagicMock()
    asgn_id = uuid4()
    art_id = uuid4()
    req = ReviewAssignmentAcceptRequest(conflict_of_interest=False)

    mock_asgn = SimpleNamespace(artifact_id=art_id)
    mock_art = SimpleNamespace(
        artifact_id=art_id,
        version_number=1,
        status="approved",
        approval_count=2,
        publication_eligible=True,
        approved_at=datetime.now(timezone.utc),
        published_at=None,
    )
    service.accept_assignment = AsyncMock(return_value=mock_asgn)
    session.get = AsyncMock(return_value=mock_art)

    # Success
    res = await content_review.accept_assignment(asgn_id, req, session, mock_lead_actor, service)
    assert res.artifact_id == art_id

    # Artifact is None -> AssertionError
    session.get = AsyncMock(return_value=None)
    with pytest.raises(AssertionError):
        await content_review.accept_assignment(asgn_id, req, session, mock_lead_actor, service)

    # Exceptions
    service.accept_assignment = AsyncMock(side_effect=LookupError("Not found"))
    with pytest.raises(HTTPException) as exc_404:
        await content_review.accept_assignment(asgn_id, req, session, mock_lead_actor, service)
    assert exc_404.value.status_code == 404

    service.accept_assignment = AsyncMock(side_effect=PermissionError("Forbidden"))
    with pytest.raises(HTTPException) as exc_403:
        await content_review.accept_assignment(asgn_id, req, session, mock_lead_actor, service)
    assert exc_403.value.status_code == 403

    service.accept_assignment = AsyncMock(side_effect=ValueError("Conflict"))
    with pytest.raises(HTTPException) as exc_409:
        await content_review.accept_assignment(asgn_id, req, session, mock_lead_actor, service)
    assert exc_409.value.status_code == 409


@pytest.mark.asyncio
async def test_reassign_review(mock_lead_actor):
    session = AsyncMock()
    service = MagicMock()
    asgn_id = uuid4()
    art_id = uuid4()
    req = ReviewAssignmentReassignRequest(
        new_reviewer_id="rev_new",
        reason="Unavailable",
    )

    mock_asgn = SimpleNamespace(
        id=asgn_id,
        artifact_id=art_id,
        artifact_version=1,
        assigned_to="rev_new",
        status="pending",
        assigned_at=datetime.now(timezone.utc),
        due_by=None,
        priority="normal",
        reminder_count=0,
        last_reminded_at=None,
        escalated_at=None,
        reassigned_from_id=None,
    )
    service.reassign_assignment = AsyncMock(return_value=mock_asgn)

    # Success
    res = await content_review.reassign_review(asgn_id, req, session, mock_lead_actor, service)
    assert res.assignment_id == asgn_id

    # LookupError -> 404
    service.reassign_assignment = AsyncMock(side_effect=LookupError("Not found"))
    with pytest.raises(HTTPException) as exc_404:
        await content_review.reassign_review(asgn_id, req, session, mock_lead_actor, service)
    assert exc_404.value.status_code == 404

    # ReviewConflictError -> 409
    service.reassign_assignment = AsyncMock(side_effect=ReviewConflictError("Conflict"))
    with pytest.raises(HTTPException) as exc_409:
        await content_review.reassign_review(asgn_id, req, session, mock_lead_actor, service)
    assert exc_409.value.status_code == 409


@pytest.mark.asyncio
async def test_submit_review_decision(mock_lead_actor):
    session = AsyncMock()
    service = MagicMock()
    art_id = uuid4()
    dec_id = uuid4()

    req = ReviewDecisionRequest(
        action=ContentReviewAction.APPROVE,
        expected_version=1,
        idempotency_key="idemp_dec_001",
    )

    mock_res = SimpleNamespace(
        decision_id=dec_id,
        artifact_id=art_id,
        artifact_version=1,
        action="approve",
        previous_status="pending_review",
        current_status="approved",
        approval_count=2,
        quorum_threshold=2,
        quorum_reached=True,
        idempotent_replay=False,
    )
    service.submit_decision = AsyncMock(return_value=mock_res)

    # Success
    res = await content_review.submit_review_decision(art_id, req, session, mock_lead_actor, service)
    assert res.decision_id == dec_id

    # LookupError -> 404
    service.submit_decision = AsyncMock(side_effect=LookupError("Not found"))
    with pytest.raises(HTTPException) as exc_404:
        await content_review.submit_review_decision(art_id, req, session, mock_lead_actor, service)
    assert exc_404.value.status_code == 404

    # PermissionError -> 403
    service.submit_decision = AsyncMock(side_effect=PermissionError("Forbidden"))
    with pytest.raises(HTTPException) as exc_403:
        await content_review.submit_review_decision(art_id, req, session, mock_lead_actor, service)
    assert exc_403.value.status_code == 403

    # ValueError -> 409
    service.submit_decision = AsyncMock(side_effect=ValueError("Bad state"))
    with pytest.raises(HTTPException) as exc_409:
        await content_review.submit_review_decision(art_id, req, session, mock_lead_actor, service)
    assert exc_409.value.status_code == 409


@pytest.mark.asyncio
async def test_quarantine_artifact(mock_lead_actor):
    session = AsyncMock()
    service = MagicMock()
    art_id = uuid4()
    req = QuarantineRequest(reason_code="SAFETY_FAIL", reason="Unsafe prompt response")

    mock_art = SimpleNamespace(
        artifact_id=art_id,
        version_number=1,
        status="quarantined",
        approval_count=0,
        publication_eligible=False,
        approved_at=None,
        published_at=None,
    )
    service.quarantine_artifact = AsyncMock(return_value=mock_art)

    # Success
    res = await content_review.quarantine_artifact(art_id, req, session, mock_lead_actor, service)
    assert res.status == "quarantined"

    # LookupError -> 404
    service.quarantine_artifact = AsyncMock(side_effect=LookupError("Not found"))
    with pytest.raises(HTTPException) as exc_404:
        await content_review.quarantine_artifact(art_id, req, session, mock_lead_actor, service)
    assert exc_404.value.status_code == 404

    # ValueError -> 409
    service.quarantine_artifact = AsyncMock(side_effect=ValueError("Conflict"))
    with pytest.raises(HTTPException) as exc_409:
        await content_review.quarantine_artifact(art_id, req, session, mock_lead_actor, service)
    assert exc_409.value.status_code == 409


@pytest.mark.asyncio
async def test_create_artifact_revision(mock_lead_actor):
    session = AsyncMock()
    service = MagicMock()
    art_id = uuid4()
    new_id = uuid4()
    req = ArtifactRevisionRequest(
        expected_version=1,
        artifact_json={"updated": True},
        reason="Refining explanation",
    )

    mock_res = SimpleNamespace(
        previous_artifact_id=art_id,
        new_artifact_id=new_id,
        version_number=2,
        status="pending_review",
    )
    service.create_revision = AsyncMock(return_value=mock_res)

    # Success
    res = await content_review.create_artifact_revision(art_id, req, session, mock_lead_actor, service)
    assert res.new_artifact_id == new_id

    # LookupError -> 404
    service.create_revision = AsyncMock(side_effect=LookupError("Not found"))
    with pytest.raises(HTTPException) as exc_404:
        await content_review.create_artifact_revision(art_id, req, session, mock_lead_actor, service)
    assert exc_404.value.status_code == 404

    # ReviewConflictError -> 409
    service.create_revision = AsyncMock(side_effect=ReviewConflictError("Version mismatch"))
    with pytest.raises(HTTPException) as exc_409:
        await content_review.create_artifact_revision(art_id, req, session, mock_lead_actor, service)
    assert exc_409.value.status_code == 409


@pytest.mark.asyncio
async def test_record_answer_key_verification(monkeypatch, mock_lead_actor):
    session = AsyncMock()
    art_id = uuid4()
    ver_id = uuid4()

    req = AnswerKeyVerificationRequest(
        expected_version=1,
        artifact_hash="a" * 32,
        method="deterministic_recompute",
        passed=True,
        idempotency_key="idemp_ver_001",
        details={"result": "identical"},
    )

    mock_res = SimpleNamespace(
        verification_id=ver_id,
        artifact_id=art_id,
        artifact_version=1,
        artifact_hash="a" * 32,
        method="deterministic_recompute",
        passed=True,
        idempotent_replay=False,
    )

    mock_ak_svc = MagicMock()
    mock_ak_svc.record = AsyncMock(return_value=mock_res)
    monkeypatch.setattr(
        content_review,
        "ContentAnswerKeyVerificationService",
        lambda: mock_ak_svc,
    )

    # Success
    res = await content_review.record_answer_key_verification(art_id, req, session, mock_lead_actor)
    assert res.verification_id == ver_id

    # LookupError -> 404
    mock_ak_svc.record = AsyncMock(side_effect=LookupError("Not found"))
    with pytest.raises(HTTPException) as exc_404:
        await content_review.record_answer_key_verification(art_id, req, session, mock_lead_actor)
    assert exc_404.value.status_code == 404

    # ValueError -> 409
    mock_ak_svc.record = AsyncMock(side_effect=ValueError("Bad hash"))
    with pytest.raises(HTTPException) as exc_409:
        await content_review.record_answer_key_verification(art_id, req, session, mock_lead_actor)
    assert exc_409.value.status_code == 409


@pytest.mark.asyncio
async def test_publish_artifact(mock_lead_actor):
    session = AsyncMock()
    service = MagicMock()
    art_id = uuid4()
    req = ArtifactPublishRequest(
        expected_version=1,
        reason="Consensus reached",
    )

    mock_art = SimpleNamespace(
        artifact_id=art_id,
        version_number=1,
        status="published",
        approval_count=3,
        publication_eligible=True,
        approved_at=datetime.now(timezone.utc),
        published_at=datetime.now(timezone.utc),
    )
    service.publish_artifact = AsyncMock(return_value=mock_art)

    # Success
    res = await content_review.publish_artifact(art_id, req, session, mock_lead_actor, service)
    assert res.status == "published"

    # LookupError -> 404
    service.publish_artifact = AsyncMock(side_effect=LookupError("Not found"))
    with pytest.raises(HTTPException) as exc_404:
        await content_review.publish_artifact(art_id, req, session, mock_lead_actor, service)
    assert exc_404.value.status_code == 404

    # ValueError -> 409
    service.publish_artifact = AsyncMock(side_effect=ValueError("Not eligible"))
    with pytest.raises(HTTPException) as exc_409:
        await content_review.publish_artifact(art_id, req, session, mock_lead_actor, service)
    assert exc_409.value.status_code == 409


@pytest.mark.asyncio
async def test_get_review_history_and_list_stale(mock_lead_actor):
    session = AsyncMock()
    service = MagicMock()
    art_id = uuid4()
    dec_id = uuid4()
    evt_id = uuid4()
    asgn_id = uuid4()

    # 1. history
    mock_dec = SimpleNamespace(
        decision_id=dec_id,
        artifact_id=art_id,
        artifact_version=1,
        reviewer_id="rev_01",
        review_action=ContentReviewAction.APPROVE,
        reason_code=None,
        comments="Looks good",
        rubric_id="rubric_01",
        rubric_version="v1",
        rubric_results={"criteria": 5},
        policy_version="v2",
        correlation_id=None,
        created_at=datetime.now(timezone.utc),
    )
    mock_trans = SimpleNamespace(
        event_id=evt_id,
        artifact_id=art_id,
        artifact_version=1,
        previous_status="pending_review",
        new_status="approved",
        actor_id="rev_01",
        reason_code=None,
        reason="Approved by consensus",
        policy_version="v2",
        correlation_id=None,
        created_at=datetime.now(timezone.utc),
    )
    service.list_history = AsyncMock(
        return_value={"decisions": [mock_dec], "transitions": [mock_trans]}
    )

    hist = await content_review.get_review_history(art_id, session, mock_lead_actor, service)
    assert len(hist.decisions) == 1
    assert len(hist.transitions) == 1
    assert hist.decisions[0].action == "approve"

    # 2. stale assignments
    mock_stale = SimpleNamespace(
        id=asgn_id,
        artifact_id=art_id,
        artifact_version=1,
        assigned_to="rev_02",
        status="pending",
        assigned_at=datetime.now(timezone.utc),
        due_by=datetime.now(timezone.utc),
        priority="normal",
        reminder_count=2,
        last_reminded_at=datetime.now(timezone.utc),
        escalated_at=None,
        reassigned_from_id=None,
    )
    service.list_stale_assignments = AsyncMock(return_value=[mock_stale])

    stale_list = await content_review.list_stale_assignments(200, session, mock_lead_actor, service)
    assert len(stale_list) == 1
    assert stale_list[0].assignment_id == asgn_id
