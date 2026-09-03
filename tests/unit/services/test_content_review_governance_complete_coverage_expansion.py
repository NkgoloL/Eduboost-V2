"""Comprehensive branch coverage expansion for ContentReviewGovernanceService."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.content_factory import (
    ContentAnswerKeyVerification,
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentLayer,
    ContentReviewAction,
    ContentReviewAssignment,
    ContentReviewDecision,
    ContentStateTransitionEvent,
)
from app.services.content_factory import ContentFactoryService
from app.services.content_review_governance import (
    REQUIRED_APPROVAL_RUBRIC_CRITERIA,
    ArtifactRevisionResult,
    ContentReviewEligibilityService,
    ContentReviewGovernanceService,
    ReviewConflictError,
    ReviewDecisionResult,
    ReviewGovernancePolicy,
    _env_bool,
    _rubric_passed,
    _source_payload,
    _value,
)


def _valid_rubric_results() -> dict[str, Any]:
    return {criterion: True for criterion in REQUIRED_APPROVAL_RUBRIC_CRITERIA}


@pytest.mark.unit
def test_review_governance_policy_from_environment():
    with patch.dict(os.environ, {
        "CONTENT_CONSENSUS_THRESHOLD": "4",
        "CONTENT_CONSENSUS_TIMEOUT_HOURS": "48",
        "CONTENT_CREATOR_APPROVAL_COUNTS": "true",
        "CONTENT_DIRECT_PUBLISH_ALLOWED": "1",
    }):
        policy = ReviewGovernancePolicy.from_environment()
        assert policy.quorum_threshold == 4
        assert policy.stale_after_hours == 48
        assert policy.creator_approval_counts is True
        assert policy.direct_publish_allowed is True

    # Validation errors
    with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "1"}):
        with pytest.raises(ValueError, match="between 2 and 10"):
            ReviewGovernancePolicy.from_environment()

    with patch.dict(os.environ, {"CONTENT_CONSENSUS_TIMEOUT_HOURS": "0"}):
        with pytest.raises(ValueError, match="must be positive"):
            ReviewGovernancePolicy.from_environment()


@pytest.mark.unit
def test_content_review_eligibility_service():
    art = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        status=ContentArtifactStatus.PROMOTED_PRODUCTION,
        publication_eligible=True,
        published_at=datetime.now(timezone.utc),
    )
    assert ContentReviewEligibilityService.is_retrieval_eligible(art) is True
    ContentReviewEligibilityService.assert_retrieval_eligible(art)

    # Ineligible retrieval
    art.publication_eligible = False
    assert ContentReviewEligibilityService.is_retrieval_eligible(art) is False
    with pytest.raises(ValueError, match="not eligible for semantic retrieval"):
        ContentReviewEligibilityService.assert_retrieval_eligible(art)

    # Learner delivery eligibility
    art.status = ContentArtifactStatus.PUBLISHED
    art.published_at = datetime.now(timezone.utc)
    assert ContentReviewEligibilityService.is_learner_eligible(art) is True
    ContentReviewEligibilityService.assert_learner_eligible(art)

    art.published_at = None
    assert ContentReviewEligibilityService.is_learner_eligible(art) is False
    with pytest.raises(ValueError, match="not eligible for learner delivery"):
        ContentReviewEligibilityService.assert_learner_eligible(art)


@pytest.mark.unit
def test_rubric_passed_and_helpers():
    assert _rubric_passed(True) is True
    assert _rubric_passed(False) is False
    assert _rubric_passed(0.85) is True
    assert _rubric_passed(0.70) is False
    assert _rubric_passed("pass") is True
    assert _rubric_passed("approved") is True
    assert _rubric_passed("rejected") is False
    assert _rubric_passed({"result": "yes"}) is True
    assert _rubric_passed({"passed": 0.9}) is True
    assert _rubric_passed(None) is False

    assert _env_bool("NON_EXISTENT_VAR", True) is True
    assert _env_bool("NON_EXISTENT_VAR", False) is False

    source = ContentArtifactSource(
        source_document_id=uuid.uuid4(),
        source_title="Source 1",
        source_type="textbook",
        source_metadata={"extra_key": "extra_val"},
    )
    payload = _source_payload(source)
    assert payload["source_title"] == "Source 1"
    assert payload["extra_key"] == "extra_val"


@pytest.mark.asyncio
async def test_assign_reviewers_validation_and_idempotency():
    policy = ReviewGovernancePolicy(quorum_threshold=3, creator_approval_counts=False)
    svc = ContentReviewGovernanceService(policy=policy)
    session = AsyncMock()
    art_id = uuid.uuid4()

    artifact = ContentGenerationArtifact(
        artifact_id=art_id,
        status=ContentArtifactStatus.GENERATED,
        created_by_actor_id="creator-1",
        version_number=1,
    )
    session.scalar = AsyncMock(return_value=artifact)

    # 1. Not pending_review
    with pytest.raises(ValueError, match="only be assigned to pending_review"):
        await svc.assign_reviewers(session, artifact_id=art_id, reviewer_ids=["r1", "r2", "r3"], assigned_by="admin-1")

    # 2. Too few reviewers
    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    with pytest.raises(ValueError, match="At least 3 distinct reviewers"):
        await svc.assign_reviewers(session, artifact_id=art_id, reviewer_ids=["r1", "r2"], assigned_by="admin-1")

    # 3. Creator cannot be assigned
    with pytest.raises(ValueError, match="creator cannot be assigned"):
        await svc.assign_reviewers(session, artifact_id=art_id, reviewer_ids=["r1", "r2", "creator-1"], assigned_by="admin-1")

    # 4. Success and existing assignment reuse
    existing_ass = ContentReviewAssignment(id=uuid.uuid4(), assigned_to="r1")
    # First scalar call is load artifact, then loop over r1 (found), r2 (None), r3 (None)
    session.scalar = AsyncMock(side_effect=[artifact, existing_ass, None, None])
    session.flush = AsyncMock()

    res = await svc.assign_reviewers(
        session,
        artifact_id=art_id,
        reviewer_ids=["r1", "r2", "r3"],
        assigned_by="admin-1",
        reviewer_competencies={"r2": ["caps"], "r3": ["subject"]},
        idempotency_key="idemp-key",
    )
    assert res.assigned_count == 3


@pytest.mark.asyncio
async def test_accept_assignment_validation():
    svc = ContentReviewGovernanceService()
    session = AsyncMock()
    ass_id = uuid.uuid4()

    # 1. Not found
    session.scalar = AsyncMock(return_value=None)
    with pytest.raises(LookupError, match="not found"):
        await svc.accept_assignment(session, assignment_id=ass_id, reviewer_id="r1", conflict_of_interest=False)

    # 2. Wrong reviewer
    ass = ContentReviewAssignment(id=ass_id, assigned_to="r2", status="assigned")
    session.scalar = AsyncMock(return_value=ass)
    with pytest.raises(PermissionError, match="only be accepted by the assigned reviewer"):
        await svc.accept_assignment(session, assignment_id=ass_id, reviewer_id="r1", conflict_of_interest=False)

    # 3. Closed assignment
    ass.assigned_to = "r1"
    ass.status = "resolved"
    with pytest.raises(ValueError, match="Only open review assignments"):
        await svc.accept_assignment(session, assignment_id=ass_id, reviewer_id="r1", conflict_of_interest=False)

    # 4. Accepted with conflict
    ass.status = "assigned"
    session.flush = AsyncMock()
    accepted_conflict = await svc.accept_assignment(session, assignment_id=ass_id, reviewer_id="r1", conflict_of_interest=True)
    assert accepted_conflict.status == "conflict"

    # 5. Accepted without conflict -> in_review
    ass.status = "assigned"
    accepted_ok = await svc.accept_assignment(session, assignment_id=ass_id, reviewer_id="r1", conflict_of_interest=False)
    assert accepted_ok.status == "in_review"


@pytest.mark.asyncio
async def test_submit_decision_replays_and_validations():
    policy = ReviewGovernancePolicy(quorum_threshold=2, creator_approval_counts=False)
    svc = ContentReviewGovernanceService(policy=policy)
    session = AsyncMock()
    art_id = uuid.uuid4()

    # 1. Empty idempotency key
    with pytest.raises(ValueError, match="require an idempotency key"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results={}, idempotency_key="", expected_version=1)

    # 2. Replay with different version or artifact
    replay_diff = ContentReviewDecision(decision_id=uuid.uuid4(), artifact_id=uuid.uuid4(), artifact_version=1, idempotency_key="k1", reviewer_id="r1")
    session.scalar = AsyncMock(return_value=replay_diff)
    with pytest.raises(ValueError, match="already used for a different decision"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results={}, idempotency_key="k1", expected_version=1)

    # 3. Valid idempotent replay
    replay_same = ContentReviewDecision(
        decision_id=uuid.uuid4(), artifact_id=art_id, artifact_version=1, idempotency_key="k1",
        reviewer_id="r1", review_action=ContentReviewAction.APPROVE,
    )
    artifact = ContentGenerationArtifact(artifact_id=art_id, version_number=1, status=ContentArtifactStatus.APPROVED, approval_count=2)
    session.scalar = AsyncMock(side_effect=[replay_same, artifact])
    res_replay = await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results={}, idempotency_key="k1", expected_version=1)
    assert res_replay.idempotent_replay is True

    # 4. Version mismatch
    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    artifact.created_by_actor_id = "creator-1"
    session.scalar = AsyncMock(side_effect=[None, artifact])
    with pytest.raises(ReviewConflictError, match="Artifact version changed"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results=_valid_rubric_results(), idempotency_key="k2", expected_version=2)

    # 5. Non pending_review status
    artifact.status = ContentArtifactStatus.PUBLISHED
    session.scalar = AsyncMock(side_effect=[None, artifact])
    with pytest.raises(ReviewConflictError, match="only be submitted for pending_review"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results=_valid_rubric_results(), idempotency_key="k2", expected_version=1)

    # 6. Creator reviewing own content
    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    session.scalar = AsyncMock(side_effect=[None, artifact])
    with pytest.raises(PermissionError, match="creators cannot review their own content"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="creator-1", action="approve", rubric_results=_valid_rubric_results(), idempotency_key="k2", expected_version=1)

    # 7. Unassigned reviewer
    session.scalar = AsyncMock(side_effect=[None, artifact, None])
    with pytest.raises(PermissionError, match="not assigned to this artifact version"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results=_valid_rubric_results(), idempotency_key="k2", expected_version=1)

    # 8. Conflicted assignment
    ass_conflict = ContentReviewAssignment(id=uuid.uuid4(), status="conflict", conflict_of_interest=True)
    session.scalar = AsyncMock(side_effect=[None, artifact, ass_conflict])
    with pytest.raises(PermissionError, match="conflicted reviewer cannot submit"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results=_valid_rubric_results(), idempotency_key="k2", expected_version=1)

    # 9. Already resolved assignment
    ass_resolved = ContentReviewAssignment(id=uuid.uuid4(), status="approved", conflict_of_interest=False)
    session.scalar = AsyncMock(side_effect=[None, artifact, ass_resolved])
    with pytest.raises(ReviewConflictError, match="already submitted a decision"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results=_valid_rubric_results(), idempotency_key="k2", expected_version=1)

    # 10. Rubric incomplete or missing reason code
    ass_open = ContentReviewAssignment(id=uuid.uuid4(), status="in_review", conflict_of_interest=False, reviewer_competencies=["caps"])
    session.scalar = AsyncMock(side_effect=[None, artifact, ass_open])
    with pytest.raises(ValueError, match="Approval rubric is incomplete"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results={"caps_alignment": True}, idempotency_key="k2", expected_version=1)

    session.scalar = AsyncMock(side_effect=[None, artifact, ass_open])
    with pytest.raises(ValueError, match="decisions require a reason code"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="reject", rubric_results={}, reason_code="", idempotency_key="k2", expected_version=1)


@pytest.mark.asyncio
async def test_submit_decision_approve_quorum_diagnostic_item():
    policy = ReviewGovernancePolicy(quorum_threshold=2, creator_approval_counts=False)
    factory_mock = MagicMock()
    factory_mock.assert_artifact_has_approved_sources = AsyncMock()
    svc = ContentReviewGovernanceService(policy=policy, factory_service=factory_mock)
    session = AsyncMock()
    art_id = uuid.uuid4()

    artifact = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
        status=ContentArtifactStatus.PENDING_REVIEW,
        artifact_type=ContentArtifactType.DIAGNOSTIC_ITEM,
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        language="en",
        created_by_actor_id="creator-1",
        approval_count=0,
        row_version=1,
    )
    assignment = ContentReviewAssignment(
        id=uuid.uuid4(),
        status="in_review",
        conflict_of_interest=False,
        reviewer_competencies=["caps", "subject"],
    )

    prev_approval = ContentReviewDecision(
        decision_id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        reviewer_id="r1",
        review_action=ContentReviewAction.APPROVE,
        conflict_of_interest=False,
        reviewer_competencies=["caps"],
    )
    curr_approval = ContentReviewDecision(
        decision_id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        reviewer_id="r2",
        review_action=ContentReviewAction.APPROVE,
        conflict_of_interest=False,
        reviewer_competencies=["subject"],
    )

    verif = ContentAnswerKeyVerification(
        verification_id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        passed=True,
    )

    # scalar calls:
    # 1. replay check -> None
    # 2. _load_artifact_for_update -> artifact
    # 3. assignment -> assignment
    # 4. _latest_answer_key_verification -> verif
    session.scalar = AsyncMock(side_effect=[None, artifact, assignment, verif])

    def make_scalars_result(items):
        m = MagicMock()
        m.all.return_value = items
        return m

    # scalars for _valid_approvals -> [prev_approval, curr_approval] (2 approvals reaches quorum 2)
    session.scalars = AsyncMock(return_value=make_scalars_result([prev_approval, curr_approval]))
    session.flush = AsyncMock()

    res = await svc.submit_decision(
        session,
        artifact_id=art_id,
        reviewer_id="r2",
        action=ContentReviewAction.APPROVE,
        rubric_results=_valid_rubric_results(),
        idempotency_key="k-approve",
        expected_version=1,
    )
    assert res.action == "approve"
    assert res.current_status == ContentArtifactStatus.APPROVED.value
    assert res.quorum_reached is True
    assert artifact.answer_key_verified is True
    assert artifact.publication_eligible is True


@pytest.mark.asyncio
async def test_quarantine_artifact_and_create_revision():
    factory_mock = MagicMock()
    factory_mock.create_artifact = AsyncMock()
    svc = ContentReviewGovernanceService(factory_service=factory_mock)
    session = AsyncMock()
    art_id = uuid.uuid4()

    # 1. Quarantine artifact
    artifact = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
        status=ContentArtifactStatus.PENDING_REVIEW,
        sources=[],
        artifact_hash="hash-1",
        row_version=1,
    )
    session.scalar = AsyncMock(return_value=artifact)
    session.flush = AsyncMock()

    with pytest.raises(ValueError, match="Quarantine requires a reason code"):
        await svc.quarantine_artifact(session, artifact_id=art_id, actor_id="admin-1", reason_code="", reason="")

    quarantined = await svc.quarantine_artifact(session, artifact_id=art_id, actor_id="admin-1", reason_code="safety_violation", reason="Contains unsafe text")
    assert quarantined.status == ContentArtifactStatus.QUARANTINED
    assert quarantined.publication_eligible is False

    # 2. Create revision
    with pytest.raises(ValueError, match="revised artifact payload is required"):
        await svc.create_revision(session, artifact_id=art_id, actor_id="editor-1", artifact_json={}, reason="Fix", expected_version=1)

    # Hash mismatch check
    artifact.status = ContentArtifactStatus.REVISION_REQUIRED
    revised_art = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        status=ContentArtifactStatus.GENERATED,
        version_number=2,
    )
    factory_mock.create_artifact.return_value = revised_art
    session.scalar = AsyncMock(return_value=artifact)

    rev_res = await svc.create_revision(
        session,
        artifact_id=art_id,
        actor_id="editor-1",
        artifact_json={"stem": "New text"},
        reason="Updated stem",
        expected_version=1,
    )
    assert rev_res.version_number == 2
    assert artifact.status == ContentArtifactStatus.SUPERSEDED


@pytest.mark.asyncio
async def test_publish_artifact_and_reassign():
    policy = ReviewGovernancePolicy(quorum_threshold=2, direct_publish_allowed=False)
    factory_mock = MagicMock()
    factory_mock.assert_artifact_has_approved_sources = AsyncMock()
    svc = ContentReviewGovernanceService(policy=policy, factory_service=factory_mock)
    session = AsyncMock()
    art_id = uuid.uuid4()

    artifact = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
        status=ContentArtifactStatus.APPROVED,
        publication_eligible=True,
        approval_count=2,
        answer_key_verified=True,
        artifact_type=ContentArtifactType.LESSON,
        content_layer=ContentLayer.LESSONS,
        row_version=1,
    )

    # 1. Publication requires promoted_production (when direct_publish_allowed is False)
    session.scalar = AsyncMock(return_value=artifact)
    with pytest.raises(ReviewConflictError, match="Publication requires promoted_production status"):
        await svc.publish_artifact(session, artifact_id=art_id, actor_id="admin-1", expected_version=1, reason="Release")

    # 2. Promoted production with blocking review decision
    artifact.status = ContentArtifactStatus.PROMOTED_PRODUCTION
    # First scalar is artifact, second is count of blocking decisions = 1
    session.scalar = AsyncMock(side_effect=[artifact, 1])
    with pytest.raises(ReviewConflictError, match="blocked by a review decision"):
        await svc.publish_artifact(session, artifact_id=art_id, actor_id="admin-1", expected_version=1, reason="Release")

    # 3. Successful publication
    session.scalar = AsyncMock(side_effect=[artifact, 0])
    session.flush = AsyncMock()
    pub = await svc.publish_artifact(session, artifact_id=art_id, actor_id="admin-1", expected_version=1, reason="Release")
    assert pub.status == ContentArtifactStatus.PUBLISHED
    assert pub.published_at is not None

    # 4. Reassign assignment
    ass_id = uuid.uuid4()
    ass_original = ContentReviewAssignment(
        id=ass_id,
        artifact_id=art_id,
        artifact_version=1,
        assigned_to="r1",
        status="assigned",
        priority="normal",
    )
    # scalar: 1. original assignment, 2. artifact, 3. existing replacement assignment (None)
    session.scalar = AsyncMock(side_effect=[ass_original, artifact, None])
    replacement = await svc.reassign_assignment(
        session,
        assignment_id=ass_id,
        new_reviewer_id="r2",
        assigned_by="admin-1",
        reason="Unavailable",
    )
    assert replacement.assigned_to == "r2"
    assert ass_original.status == "reassigned"


@pytest.mark.asyncio
async def test_submit_decision_remaining_actions_and_exceptions():
    policy = ReviewGovernancePolicy(quorum_threshold=2)
    factory_mock = MagicMock()
    factory_mock.assert_artifact_has_approved_sources = AsyncMock()
    svc = ContentReviewGovernanceService(policy=policy, factory_service=factory_mock)
    session = AsyncMock()
    art_id = uuid.uuid4()

    # 1. Assignment status not in {"assigned", "in_review"}
    artifact = ContentGenerationArtifact(
        artifact_id=art_id, version_number=1, status=ContentArtifactStatus.PENDING_REVIEW,
        language="en", created_by_actor_id="creator-1", approval_count=0, row_version=1,
    )
    ass_cancelled = ContentReviewAssignment(id=uuid.uuid4(), status="cancelled", conflict_of_interest=False)
    session.scalar = AsyncMock(side_effect=[None, artifact, ass_cancelled])
    with pytest.raises(ReviewConflictError, match="Review assignment is not open"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="reject", rubric_results={}, reason_code="poor_quality", idempotency_key="k1", expected_version=1)

    # 2. IntegrityError on decision flush
    ass_open = ContentReviewAssignment(id=uuid.uuid4(), status="assigned", conflict_of_interest=False)
    session.scalar = AsyncMock(side_effect=[None, artifact, ass_open])
    session.flush = AsyncMock(side_effect=IntegrityError("stmt", "params", Exception("orig")))
    with pytest.raises(ReviewConflictError, match="already submitted a decision"):

        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="reject", rubric_results={}, reason_code="poor_quality", idempotency_key="k2", expected_version=1)

    # 3. Actions: REJECT, QUARANTINE, REQUEST_CHANGES
    for act, expected_status in [
        (ContentReviewAction.REJECT, ContentArtifactStatus.REJECTED.value),
        (ContentReviewAction.QUARANTINE, ContentArtifactStatus.QUARANTINED.value),
        (ContentReviewAction.REQUEST_CHANGES, ContentArtifactStatus.REVISION_REQUIRED.value),
    ]:
        artifact.status = ContentArtifactStatus.PENDING_REVIEW
        ass_curr = ContentReviewAssignment(id=uuid.uuid4(), status="in_review", conflict_of_interest=False)
        session.scalar = AsyncMock(side_effect=[None, artifact, ass_curr])
        session.flush = AsyncMock()
        res = await svc.submit_decision(
            session, artifact_id=art_id, reviewer_id="r1", action=act, rubric_results={},
            reason_code="quality_issue", comments="Issues found", idempotency_key=f"k-{act.value}", expected_version=1,
        )
        assert res.current_status == expected_status

    # 4. Non-diagnostic item approve reaching quorum -> publication_eligible = True
    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    artifact.artifact_type = ContentArtifactType.LESSON
    artifact.content_layer = ContentLayer.LESSONS
    ass_appr = ContentReviewAssignment(id=uuid.uuid4(), status="in_review", conflict_of_interest=False)
    dec1 = ContentReviewDecision(decision_id=uuid.uuid4(), artifact_id=art_id, artifact_version=1, reviewer_id="r1", review_action=ContentReviewAction.APPROVE, conflict_of_interest=False, reviewer_competencies=["caps"])
    dec2 = ContentReviewDecision(decision_id=uuid.uuid4(), artifact_id=art_id, artifact_version=1, reviewer_id="r2", review_action=ContentReviewAction.APPROVE, conflict_of_interest=False, reviewer_competencies=["subject"])
    session.scalar = AsyncMock(side_effect=[None, artifact, ass_appr])
    mock_res = MagicMock()
    mock_res.all.return_value = [dec1, dec2]
    session.scalars = AsyncMock(return_value=mock_res)
    session.flush = AsyncMock()

    res_lesson = await svc.submit_decision(
        session, artifact_id=art_id, reviewer_id="r2", action="approve", rubric_results=_valid_rubric_results(),
        idempotency_key="k-appr-lesson", expected_version=1,
    )
    assert res_lesson.current_status == ContentArtifactStatus.APPROVED.value
    assert artifact.publication_eligible is True


@pytest.mark.asyncio
async def test_competency_and_rubric_failures():
    factory_mock = MagicMock()
    factory_mock.assert_artifact_has_approved_sources = AsyncMock()
    svc = ContentReviewGovernanceService(factory_service=factory_mock)
    session = AsyncMock()
    art_id = uuid.uuid4()

    # 1. Quorum missing CAPS/subject competency
    art_en = ContentGenerationArtifact(
        artifact_id=art_id, version_number=1, status=ContentArtifactStatus.PENDING_REVIEW,
        language="en", created_by_actor_id="creator-1", approval_count=0, row_version=1,
    )
    ass1 = ContentReviewAssignment(id=uuid.uuid4(), status="in_review", conflict_of_interest=False)
    dec_nocomp = ContentReviewDecision(decision_id=uuid.uuid4(), artifact_id=art_id, artifact_version=1, reviewer_id="r1", review_action=ContentReviewAction.APPROVE, conflict_of_interest=False, reviewer_competencies=["general_pedagogy"])
    session.scalar = AsyncMock(side_effect=[None, art_en, ass1])
    mock_res1 = MagicMock()
    mock_res1.all.return_value = [dec_nocomp, dec_nocomp, dec_nocomp]
    session.scalars = AsyncMock(return_value=mock_res1)
    with pytest.raises(ValueError, match="requires at least one subject/CAPS-competent reviewer"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results=_valid_rubric_results(), idempotency_key="k-comp1", expected_version=1)

    # 2. Non-English content missing language competency
    art_zu = ContentGenerationArtifact(
        artifact_id=art_id, version_number=1, status=ContentArtifactStatus.PENDING_REVIEW,
        language="zu", created_by_actor_id="creator-1", approval_count=0, row_version=1,
    )
    ass2 = ContentReviewAssignment(id=uuid.uuid4(), status="in_review", conflict_of_interest=False)
    dec_caps = ContentReviewDecision(decision_id=uuid.uuid4(), artifact_id=art_id, artifact_version=1, reviewer_id="r1", review_action=ContentReviewAction.APPROVE, conflict_of_interest=False, reviewer_competencies=["caps"])
    session.scalar = AsyncMock(side_effect=[None, art_zu, ass2])
    mock_res2 = MagicMock()
    mock_res2.all.return_value = [dec_caps, dec_caps, dec_caps]
    session.scalars = AsyncMock(return_value=mock_res2)
    with pytest.raises(ValueError, match="requires a language-competent reviewer"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results=_valid_rubric_results(), idempotency_key="k-comp2", expected_version=1)

    # 3. Rubric failure rejection in _validate_decision_input
    bad_rubric = _valid_rubric_results()
    bad_rubric["factual_accuracy"] = False
    ass3 = ContentReviewAssignment(id=uuid.uuid4(), status="in_review", conflict_of_interest=False)
    session.scalar = AsyncMock(side_effect=[None, art_en, ass3])
    with pytest.raises(ValueError, match="Approval is blocked by rubric failures"):
        await svc.submit_decision(session, artifact_id=art_id, reviewer_id="r1", action="approve", rubric_results=bad_rubric, idempotency_key="k-comp3", expected_version=1)



@pytest.mark.asyncio
async def test_quarantine_and_revision_edge_branches():
    factory_mock = MagicMock()
    svc = ContentReviewGovernanceService(factory_service=factory_mock)
    session = AsyncMock()
    art_id = uuid.uuid4()

    # 1. Quarantine already superseded artifact
    art_sup = ContentGenerationArtifact(artifact_id=art_id, status=ContentArtifactStatus.SUPERSEDED, row_version=1)
    session.scalar = AsyncMock(return_value=art_sup)
    with pytest.raises(ReviewConflictError, match="Superseded artifacts are already ineligible"):
        await svc.quarantine_artifact(session, artifact_id=art_id, actor_id="admin-1", reason_code="safety", reason="test")

    # 2. Create revision version mismatch
    art_v1 = ContentGenerationArtifact(artifact_id=art_id, version_number=1, status=ContentArtifactStatus.PENDING_REVIEW, artifact_hash="hash-1", row_version=1)
    session.scalar = AsyncMock(return_value=art_v1)
    with pytest.raises(ReviewConflictError, match="Artifact version changed"):
        await svc.create_revision(session, artifact_id=art_id, actor_id="admin-1", artifact_json={"stem": "new"}, reason="update", expected_version=2)

    # 3. Create revision on already superseded artifact
    art_v1.status = ContentArtifactStatus.SUPERSEDED
    session.scalar = AsyncMock(return_value=art_v1)
    with pytest.raises(ReviewConflictError, match="Superseded artifacts cannot be revised again"):
        await svc.create_revision(session, artifact_id=art_id, actor_id="admin-1", artifact_json={"stem": "new"}, reason="update", expected_version=1)


@pytest.mark.asyncio
async def test_publish_and_reassignment_edge_branches():
    policy = ReviewGovernancePolicy(quorum_threshold=2, direct_publish_allowed=True, creator_approval_counts=False)
    factory_mock = MagicMock()
    factory_mock.assert_artifact_has_approved_sources = AsyncMock()
    svc = ContentReviewGovernanceService(policy=policy, factory_service=factory_mock)
    session = AsyncMock()
    art_id = uuid.uuid4()

    # 1. Publication version mismatch
    artifact = ContentGenerationArtifact(
        artifact_id=art_id, version_number=1, status=ContentArtifactStatus.APPROVED,
        publication_eligible=True, approval_count=2, answer_key_verified=True, row_version=1,
    )

    session.scalar = AsyncMock(return_value=artifact)
    with pytest.raises(ReviewConflictError, match="Artifact version changed before publication"):
        await svc.publish_artifact(session, artifact_id=art_id, actor_id="admin-1", expected_version=2, reason="rel")

    # 2. Publication not eligible
    artifact.publication_eligible = False
    session.scalar = AsyncMock(return_value=artifact)
    with pytest.raises(ReviewConflictError, match="not publication eligible"):
        await svc.publish_artifact(session, artifact_id=art_id, actor_id="admin-1", expected_version=1, reason="rel")

    # 3. Diagnostic item unverified answer key
    artifact.publication_eligible = True
    artifact.artifact_type = ContentArtifactType.DIAGNOSTIC_ITEM
    artifact.answer_key_verified = False
    session.scalar = AsyncMock(return_value=artifact)
    with pytest.raises(ReviewConflictError, match="independent answer-key verification"):
        await svc.publish_artifact(session, artifact_id=art_id, actor_id="admin-1", expected_version=1, reason="rel")

    # 4. Quorum not reached
    artifact.answer_key_verified = True
    artifact.approval_count = 1
    session.scalar = AsyncMock(return_value=artifact)
    with pytest.raises(ReviewConflictError, match="configured educator quorum"):
        await svc.publish_artifact(session, artifact_id=art_id, actor_id="admin-1", expected_version=1, reason="rel")

    # 5. Direct publish allowed from APPROVED status
    artifact.approval_count = 2
    session.scalar = AsyncMock(side_effect=[artifact, 0])
    session.flush = AsyncMock()
    pub = await svc.publish_artifact(session, artifact_id=art_id, actor_id="admin-1", expected_version=1, reason="Direct publish")
    assert pub.status == ContentArtifactStatus.PUBLISHED

    # 6. Reassignment edge cases
    ass_id = uuid.uuid4()
    # 6a. Assignment not found
    session.scalar = AsyncMock(return_value=None)
    with pytest.raises(LookupError, match="not found"):
        await svc.reassign_assignment(session, assignment_id=ass_id, new_reviewer_id="r2", assigned_by="admin-1", reason="sick")

    # 6b. Assignment closed
    ass_closed = ContentReviewAssignment(id=ass_id, artifact_id=art_id, artifact_version=1, assigned_to="r1", status="resolved")
    session.scalar = AsyncMock(return_value=ass_closed)
    with pytest.raises(ReviewConflictError, match="Only active assignments can be reassigned"):
        await svc.reassign_assignment(session, assignment_id=ass_id, new_reviewer_id="r2", assigned_by="admin-1", reason="sick")

    # 6c. Replacement is same as original
    ass_active = ContentReviewAssignment(id=ass_id, artifact_id=art_id, artifact_version=1, assigned_to="r1", status="assigned")
    session.scalar = AsyncMock(return_value=ass_active)
    with pytest.raises(ValueError, match="replacement reviewer must be different"):
        await svc.reassign_assignment(session, assignment_id=ass_id, new_reviewer_id="r1", assigned_by="admin-1", reason="sick")

    # 6d. Stale artifact version
    art_v2 = ContentGenerationArtifact(artifact_id=art_id, version_number=2, created_by_actor_id="creator-1")
    session.scalar = AsyncMock(side_effect=[ass_active, art_v2])
    with pytest.raises(ReviewConflictError, match="stale artifact version"):
        await svc.reassign_assignment(session, assignment_id=ass_id, new_reviewer_id="r2", assigned_by="admin-1", reason="sick")

    # 6e. Replacement is creator
    art_v1 = ContentGenerationArtifact(artifact_id=art_id, version_number=1, created_by_actor_id="creator-1")
    session.scalar = AsyncMock(side_effect=[ass_active, art_v1])
    with pytest.raises(ValueError, match="creator cannot be assigned"):
        await svc.reassign_assignment(session, assignment_id=ass_id, new_reviewer_id="creator-1", assigned_by="admin-1", reason="sick")

    # 6f. Replacement is already assigned
    ass_existing = ContentReviewAssignment(id=uuid.uuid4(), assigned_to="r2")
    session.scalar = AsyncMock(side_effect=[ass_active, art_v1, ass_existing])
    with pytest.raises(ReviewConflictError, match="replacement reviewer is already assigned"):
        await svc.reassign_assignment(session, assignment_id=ass_id, new_reviewer_id="r2", assigned_by="admin-1", reason="sick")


@pytest.mark.asyncio
async def test_process_stale_assignments_and_history():
    policy = ReviewGovernancePolicy(stale_after_hours=24)
    svc = ContentReviewGovernanceService(policy=policy)
    session = AsyncMock()
    now = datetime.now(timezone.utc)

    ass_stale1 = ContentReviewAssignment(
        id=uuid.uuid4(),
        status="assigned",
        assigned_at=now - timedelta(hours=30),
        due_by=now - timedelta(hours=5),
        reminder_count=0,
        escalated_at=None,
    )
    ass_stale_hard = ContentReviewAssignment(
        id=uuid.uuid4(),
        status="in_review",
        assigned_at=now - timedelta(hours=60),
        due_by=now - timedelta(hours=50),
        reminder_count=1,
        escalated_at=None,
    )

    def make_scalars_result(items):
        m = MagicMock()
        m.all.return_value = items
        return m

    # scalars for list_stale_assignments
    session.scalars = AsyncMock(return_value=make_scalars_result([ass_stale1, ass_stale_hard]))
    session.flush = AsyncMock()

    stale_stats = await svc.process_stale_assignments(session, now=now)
    assert stale_stats["stale"] == 2
    assert stale_stats["reminded"] == 2
    assert stale_stats["escalated"] == 1
    assert ass_stale1.reminder_count == 1
    assert ass_stale_hard.escalated_at == now

    # list_history
    session.scalars = AsyncMock(side_effect=[
        make_scalars_result([]),  # decisions
        make_scalars_result([]),  # transitions
    ])
    history = await svc.list_history(session, uuid.uuid4())
    assert "decisions" in history
    assert "transitions" in history

    # record_external_transition
    art = ContentGenerationArtifact(artifact_id=uuid.uuid4(), version_number=1)
    session.flush = AsyncMock()
    trans = await svc.record_external_transition(
        session,
        artifact=art,
        previous_status="generated",
        new_status="pending_review",
        actor_id="etl-service",
        reason_code="generation_complete",
    )
    assert trans.previous_status == "generated"
    assert trans.new_status == "pending_review"

