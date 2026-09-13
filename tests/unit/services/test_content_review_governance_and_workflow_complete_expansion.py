from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest

from app.models.content_factory import (
    ContentAnswerKeyVerification,
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentReviewAction,
    ContentReviewAssignment,
    ContentReviewDecision,
    ContentStateTransitionEvent,
)
from app.services.content_file_review_workflow import (
    ContentFileReviewWorkflowService,
    ScopeReviewEvidenceStatus,
    _dev_approved_decision,
    _educator_approved_decision,
    _legal_approved_decision,
    _now_utc,
    _pending,
    _stage_unlocked_decision,
    _valid_evidence_url,
    _write_json,
)
from app.services.content_review_governance import (
    REQUIRED_APPROVAL_RUBRIC_CRITERIA,
    ArtifactRevisionResult,
    ContentReviewEligibilityService,
    ContentReviewGovernanceService,
    ReviewAssignmentResult,
    ReviewConflictError,
    ReviewDecisionResult,
    ReviewGovernancePolicy,
    _env_bool,
    _rubric_passed,
    _source_payload,
    _value,
)


# ============================================================================
# ContentFileReviewWorkflowService Tests
# ============================================================================
def test_content_file_review_workflow_helpers():
    # helper functions
    assert _stage_unlocked_decision("dev_approved") is True
    assert _stage_unlocked_decision("approved") is True
    assert _stage_unlocked_decision("rejected") is False

    assert _dev_approved_decision("dev_approved") is True
    assert _dev_approved_decision("approved") is False

    assert _educator_approved_decision("approved") is True
    assert _educator_approved_decision("accepted") is True
    assert _educator_approved_decision("pending") is False

    assert _legal_approved_decision("pass") is True
    assert _legal_approved_decision("passed") is True
    assert _legal_approved_decision("no") is False

    assert _pending(None) is True
    assert _pending("pending") is True
    assert _pending("none") is True
    assert _pending("rev_1") is False

    assert _valid_evidence_url(None) is False
    assert _valid_evidence_url("http://example.com") is False
    assert _valid_evidence_url("https://example.com/doc") is False
    assert _valid_evidence_url("https://localhost/doc") is False
    assert _valid_evidence_url("https://docs.eduboost.org/evidence/123") is True

    assert isinstance(_now_utc(), str)
    assert _now_utc().endswith("Z")


def test_content_file_review_workflow(tmp_path: Path):
    registry = MagicMock()
    readiness_service = MagicMock()

    mock_scope = MagicMock(scope_id="scope_math_g4", status=MagicMock(value="active"), review_policy_id="policy_v1")
    registry.get_scope.return_value = mock_scope

    readiness_manifest = {
        "staging_eligible": True,
        "production_eligible": True,
        "blockers": [],
        "layers": {
            "diagnostic_items": {
                "relative_path": "data/diag.jsonl",
                "sha256": "abc123hash",
                "record_count": 10,
                "review_ready_count": 10,
            }
        },
    }
    readiness_service.evaluate_scope.return_value = MagicMock(manifest=readiness_manifest)

    service = ContentFileReviewWorkflowService(
        project_root=tmp_path,
        registry=registry,
        readiness_service=readiness_service,
        manifest_dir=tmp_path / "manifests",
    )

    # 1. review_status when manifest file is missing
    missing_status = service.review_status("scope_math_g4")
    assert isinstance(missing_status, ScopeReviewEvidenceStatus)
    assert missing_status.status == "missing"
    assert missing_status.stage_unlocked is False

    # 2. build_review_packet pending
    packet_pending = service.build_review_packet("scope_math_g4")
    assert packet_pending["decision"] == "pending"
    assert packet_pending["stage_unlocked"] is False

    # 3. review_status with pending manifest
    status_pending = service.review_status("scope_math_g4")
    assert status_pending.status == "pending"
    assert "Review decision is not dev_approved or approved." in status_pending.stage_blockers

    # 4. build_review_packet dev_approved
    packet_dev = service.build_review_packet(
        "scope_math_g4",
        reviewer_id="lead_dev_1",
        decision="dev_approved",
        evidence_url="https://docs.eduboost.org/evidence/dev",
    )
    assert packet_dev["stage_unlocked"] is True
    assert packet_dev["dev_approved"] is True

    status_dev = service.review_status("scope_math_g4")
    assert status_dev.status == "dev_approved"
    assert status_dev.stage_unlocked is True
    assert status_dev.production_unlocked is False

    # 5. build_review_packet fully approved
    service.build_review_packet(
        "scope_math_g4",
        reviewer_id="educator_1",
        decision="approved",
        evidence_url="https://docs.eduboost.org/evidence/edu",
        legal_decision="approved",
        legal_evidence_url="https://docs.eduboost.org/evidence/legal",
        notes="Reviewed and confirmed valid.",
    )
    status_full = service.review_status("scope_math_g4")
    assert status_full.status == "approved"
    assert status_full.stage_unlocked is True
    # 6. review_status edge branches
    # Scope ID mismatch
    manifest_path = tmp_path / "manifests" / "scope_math_g4_educator_review.json"
    manifest_data = json.loads(manifest_path.read_text())
    manifest_data["scope_id"] = "different_scope"
    manifest_data["evidence_url"] = "https://example.com/fake"
    manifest_data["legal_evidence_url"] = "https://example.com/fake"
    manifest_data["layer_review"]["diagnostic_items"]["record_count"] = 0
    manifest_data["layer_review"]["diagnostic_items"]["sha256"] = ""
    manifest_path.write_text(json.dumps(manifest_data))

    status_bad = service.review_status("scope_math_g4")
    assert "Review packet scope_id does not match request." in status_bad.stage_blockers
    assert any("must be a real non-placeholder" in b for b in status_bad.production_blockers)
    assert any("has no records" in b for b in status_bad.stage_blockers)
    assert any("missing artifact hash" in b for b in status_bad.stage_blockers)

    # Educator approved but not production unlocked (e.g. legal not approved)
    manifest_data["scope_id"] = "scope_math_g4"
    manifest_data["evidence_url"] = "https://valid.docs/evidence"
    manifest_data["legal_evidence_url"] = "https://example.com/fake"
    manifest_data["layer_review"]["diagnostic_items"]["record_count"] = 5
    manifest_data["layer_review"]["diagnostic_items"]["sha256"] = "sha"
    manifest_path.write_text(json.dumps(manifest_data))
    status_edu = service.review_status("scope_math_g4")
    assert status_edu.status == "educator_approved"
    assert status_edu.stage_unlocked is True
    assert status_edu.production_unlocked is False


# ============================================================================

# ReviewGovernancePolicy & ContentReviewEligibilityService Tests
# ============================================================================
def test_review_governance_policy_and_eligibility():
    # Policy environment variables
    with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "1"}):
        with pytest.raises(ValueError, match="CONTENT_CONSENSUS_THRESHOLD must be between"):
            ReviewGovernancePolicy.from_environment()

    with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "3", "CONTENT_CONSENSUS_TIMEOUT_HOURS": "0"}):
        with pytest.raises(ValueError, match="CONTENT_CONSENSUS_TIMEOUT_HOURS must be positive"):
            ReviewGovernancePolicy.from_environment()

    with patch.dict(os.environ, {
        "CONTENT_CONSENSUS_THRESHOLD": "3",
        "CONTENT_CONSENSUS_TIMEOUT_HOURS": "48",
        "CONTENT_CREATOR_APPROVAL_COUNTS": "true",
        "CONTENT_DIRECT_PUBLISH_ALLOWED": "true",
    }):
        pol = ReviewGovernancePolicy.from_environment()
        assert pol.quorum_threshold == 3
        assert pol.stale_after_hours == 48
        assert pol.creator_approval_counts is True
        assert pol.direct_publish_allowed is True

    # Eligibility Service
    art = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        status=ContentArtifactStatus.PROMOTED_PRODUCTION,
        publication_eligible=True,
    )
    assert ContentReviewEligibilityService.is_retrieval_eligible(art) is True
    ContentReviewEligibilityService.assert_retrieval_eligible(art)

    art.publication_eligible = False
    assert ContentReviewEligibilityService.is_retrieval_eligible(art) is False
    with pytest.raises(ValueError, match="not eligible for semantic retrieval"):
        ContentReviewEligibilityService.assert_retrieval_eligible(art)

    art.status = ContentArtifactStatus.PUBLISHED
    art.published_at = datetime.now(timezone.utc)
    assert ContentReviewEligibilityService.is_learner_eligible(art) is True
    ContentReviewEligibilityService.assert_learner_eligible(art)

    art.published_at = None
    assert ContentReviewEligibilityService.is_learner_eligible(art) is False
    with pytest.raises(ValueError, match="not eligible for learner delivery"):
        ContentReviewEligibilityService.assert_learner_eligible(art)


# ============================================================================
# ContentReviewGovernanceService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_review_governance_service():
    from app.services.content_factory import ContentFactoryService
    factory_service = AsyncMock(spec=ContentFactoryService)
    factory_service.assert_artifact_has_approved_sources = AsyncMock()
    policy = ReviewGovernancePolicy(quorum_threshold=2, stale_after_hours=24, creator_approval_counts=False)

    service = ContentReviewGovernanceService(policy=policy, factory_service=factory_service)

    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    art_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    artifact = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
        status=ContentArtifactStatus.PENDING_REVIEW,
        created_by_actor_id="creator_1",
        approval_count=0,
        publication_eligible=False,
        row_version=1,
        language="en",
        content_layer="diagnostic_items",
        artifact_type="diagnostic_item",
        artifact_hash="hash123",
        sources=[],
    )

    # 1. assign_reviewers validation & execution
    # Status not pending_review
    service._load_artifact_for_update = AsyncMock(return_value=artifact)
    artifact.status = ContentArtifactStatus.APPROVED
    with pytest.raises(ValueError, match="Reviewers can only be assigned to pending_review"):
        await service.assign_reviewers(session, artifact_id=art_id, reviewer_ids=["rev1", "rev2"], assigned_by="lead")

    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    # Quorum threshold not met
    with pytest.raises(ValueError, match="distinct reviewers must be assigned"):
        await service.assign_reviewers(session, artifact_id=art_id, reviewer_ids=["rev1"], assigned_by="lead")

    # Creator assigned
    with pytest.raises(ValueError, match="The artifact creator cannot be assigned"):
        await service.assign_reviewers(session, artifact_id=art_id, reviewer_ids=["rev1", "creator_1"], assigned_by="lead")

    # Clean assignment
    session.scalar.side_effect = [None, None]  # no existing assignments
    assign_res = await service.assign_reviewers(
        session,
        artifact_id=art_id,
        reviewer_ids=["rev1", "rev2"],
        assigned_by="lead",
        reviewer_competencies={"rev1": ["caps", "subject"], "rev2": ["language"]},
        idempotency_key="idemp_1",
    )
    assert isinstance(assign_res, ReviewAssignmentResult)
    assert assign_res.assigned_count == 2

    # 2. accept_assignment
    assignment = ContentReviewAssignment(
        id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        assigned_to="rev1",
        status="assigned",
        assigned_at=now,
    )
    session.scalar.side_effect = None

    session.scalar.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await service.accept_assignment(session, assignment_id=assignment.id, reviewer_id="rev1", conflict_of_interest=False)

    session.scalar.return_value = assignment
    with pytest.raises(PermissionError, match="only be accepted by the assigned reviewer"):
        await service.accept_assignment(session, assignment_id=assignment.id, reviewer_id="other", conflict_of_interest=False)

    assignment.status = "conflict"
    with pytest.raises(ValueError, match="Only open review assignments may be accepted"):
        await service.accept_assignment(session, assignment_id=assignment.id, reviewer_id="rev1", conflict_of_interest=False)

    assignment.status = "assigned"
    accepted = await service.accept_assignment(session, assignment_id=assignment.id, reviewer_id="rev1", conflict_of_interest=False)
    assert accepted.status == "in_review"

    # Conflicted acceptance
    assignment.status = "assigned"
    conflicted = await service.accept_assignment(session, assignment_id=assignment.id, reviewer_id="rev1", conflict_of_interest=True)
    assert conflicted.status == "conflict"
    assert conflicted.conflict_of_interest is True

    # 3. submit_decision
    valid_rubric = {k: True for k in REQUIRED_APPROVAL_RUBRIC_CRITERIA}
    empty_rubric = {}

    # Empty idempotency key
    with pytest.raises(ValueError, match="require an idempotency key"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.APPROVE,
            rubric_results=valid_rubric,
            idempotency_key="   ",
            expected_version=1,
        )

    # Idempotent replay
    existing_dec = ContentReviewDecision(
        decision_id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        reviewer_id="rev1",
        review_action=ContentReviewAction.APPROVE,
        idempotency_key="idemp_dec",
    )
    session.scalar.return_value = existing_dec
    service._load_artifact = AsyncMock(return_value=artifact)
    replay_res = await service.submit_decision(
        session,
        artifact_id=art_id,
        reviewer_id="rev1",
        action=ContentReviewAction.APPROVE,
        rubric_results=valid_rubric,
        idempotency_key="idemp_dec",
        expected_version=1,
    )
    assert replay_res.idempotent_replay is True

    # Replay on different version/artifact
    existing_dec.artifact_version = 2
    with pytest.raises(ValueError, match="already used for a different decision"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.APPROVE,
            rubric_results=valid_rubric,
            idempotency_key="idemp_dec",
            expected_version=1,
        )

    # Version mismatch on current artifact
    session.scalar.return_value = None  # no replay
    artifact.version_number = 2
    with pytest.raises(ReviewConflictError, match="Artifact version changed"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.APPROVE,
            rubric_results=valid_rubric,
            idempotency_key="new_key",
            expected_version=1,
        )
    artifact.version_number = 1

    # Incomplete rubric for approval
    assignment.status = "in_review"
    assignment.conflict_of_interest = False
    session.scalar.side_effect = [None, assignment]  # no replay, assignment found
    with pytest.raises(ValueError, match="Approval rubric is incomplete"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.APPROVE,
            rubric_results=empty_rubric,
            idempotency_key="new_key",
            expected_version=1,
        )

    # Missing reason code on reject
    session.scalar.side_effect = [None, assignment]
    with pytest.raises(ValueError, match="require a reason code"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.REJECT,
            rubric_results={},
            idempotency_key="new_key",
            expected_version=1,
            reason_code=None,
        )

    # Successful reject decision
    session.scalar.side_effect = [None, assignment]
    rej_dec = await service.submit_decision(
        session,
        artifact_id=art_id,
        reviewer_id="rev1",
        action=ContentReviewAction.REJECT,
        rubric_results={},
        idempotency_key="new_key",
        expected_version=1,
        reason_code="factual_errors",
        comments="Incorrect formula used",
    )
    assert rej_dec.current_status == "rejected"
    assert artifact.status == ContentArtifactStatus.REJECTED

    # Successful approval reaching quorum
    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    assignment.status = "in_review"
    approvals = [
        ContentReviewDecision(
            decision_id=uuid.uuid4(),
            artifact_id=art_id,
            artifact_version=1,
            reviewer_id="rev1",
            review_action=ContentReviewAction.APPROVE,
            reviewer_competencies=["caps", "subject"],
        ),
        ContentReviewDecision(
            decision_id=uuid.uuid4(),
            artifact_id=art_id,
            artifact_version=1,
            reviewer_id="rev2",
            review_action=ContentReviewAction.APPROVE,
            reviewer_competencies=["language"],
        ),
    ]
    service._valid_approvals = AsyncMock(return_value=approvals)
    service._latest_answer_key_verification = AsyncMock(
        return_value=ContentAnswerKeyVerification(passed=True, verification_id=uuid.uuid4())
    )
    session.scalar.side_effect = [None, assignment]
    appr_dec = await service.submit_decision(
        session,
        artifact_id=art_id,
        reviewer_id="rev1",
        action=ContentReviewAction.APPROVE,
        rubric_results=valid_rubric,
        idempotency_key="key_appr_ok",
        expected_version=1,
    )
    assert appr_dec.current_status == "approved"
    assert appr_dec.quorum_reached is True
    assert artifact.publication_eligible is True

    # 4. quarantine_artifact
    q_art = await service.quarantine_artifact(
        session,
        artifact_id=art_id,
        actor_id="auditor_1",
        reason_code="flagged_pii",
        reason="Detected student ID",
    )
    assert q_art.status == ContentArtifactStatus.QUARANTINED
    assert q_art.publication_eligible is False

    # 5. create_revision
    artifact.artifact_hash = "oldhash"
    artifact.status = ContentArtifactStatus.REVISION_REQUIRED
    service._load_artifact_for_update = AsyncMock(return_value=artifact)
    factory_service.create_artifact.return_value = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        status=ContentArtifactStatus.GENERATED,
    )
    rev_res = await service.create_revision(
        session,
        artifact_id=art_id,
        actor_id="editor_1",
        artifact_json={"question": "updated question text for revision"},
        reason="Clarified terminology",
        expected_version=1,
    )
    assert isinstance(rev_res, ArtifactRevisionResult)
    assert rev_res.version_number == 2
    assert artifact.status == ContentArtifactStatus.SUPERSEDED

    # 6. publish_artifact
    artifact.status = ContentArtifactStatus.PROMOTED_PRODUCTION
    artifact.publication_eligible = True
    artifact.approval_count = 2
    artifact.answer_key_verified = True
    session.scalar.side_effect = None
    session.scalar.return_value = 0  # no blocking review decisions
    pub_art = await service.publish_artifact(
        session,
        artifact_id=art_id,
        actor_id="admin_pub",
        expected_version=1,
        reason="Publishing vetted diagnostic batch",
    )
    assert pub_art.status == ContentArtifactStatus.PUBLISHED
    assert pub_art.published_at is not None

    # 7. reassign_assignment
    session.scalar.side_effect = [assignment, None]  # original found, no duplicate replacement
    assignment.status = "in_review"
    assignment.assigned_to = "rev1"
    reassigned = await service.reassign_assignment(
        session,
        assignment_id=assignment.id,
        new_reviewer_id="rev3",
        assigned_by="lead",
        reason="Original reviewer unavailable",
    )
    assert reassigned.assigned_to == "rev3"
    assert assignment.status == "reassigned"

    # 8. process_stale_assignments & list_history
    service.list_stale_assignments = AsyncMock(return_value=[assignment])
    stale_stats = await service.process_stale_assignments(session, now=now)
    assert stale_stats["stale"] == 1
    assert stale_stats["reminded"] == 1

    session.scalars.return_value = MagicMock(all=MagicMock(return_value=[]))
    history = await service.list_history(session, art_id)
    assert "decisions" in history
    assert "transitions" in history

    # 9. Rubric & payload helpers
    assert _rubric_passed(True) is True
    assert _rubric_passed(0.9) is True
    assert _rubric_passed("pass") is True
    assert _rubric_passed({"passed": True}) is True
    assert _rubric_passed(False) is False
    assert _env_bool("NOT_SET", True) is True
    assert _value(ContentReviewAction.APPROVE) == "approve"

    src = ContentArtifactSource(
        source_id=uuid.uuid4(),
        source_document_id=uuid.uuid4(),
        source_title="Title",
        source_type="caps_document",
        source_quality_score=0.95,
        source_metadata={"topic": "fractions"},
    )
    payload = _source_payload(src)
    assert payload["source_title"] == "Title"
    assert payload["topic"] == "fractions"


@pytest.mark.asyncio
async def test_content_review_governance_branches():
    from app.services.content_factory import ContentFactoryService
    factory_service = AsyncMock(spec=ContentFactoryService)
    factory_service.assert_artifact_has_approved_sources = AsyncMock()
    policy = ReviewGovernancePolicy(quorum_threshold=2, stale_after_hours=24, creator_approval_counts=False)
    service = ContentReviewGovernanceService(policy=policy, factory_service=factory_service)

    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    art_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    artifact = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
        status=ContentArtifactStatus.PENDING_REVIEW,
        created_by_actor_id="creator_1",
        approval_count=0,
        publication_eligible=False,
        row_version=1,
        language="af",  # non-english language
        content_layer="lessons",
        artifact_type="lesson",
        artifact_hash="hash123",
        sources=[],
    )
    service._load_artifact_for_update = AsyncMock(return_value=artifact)
    service._load_artifact = AsyncMock(return_value=artifact)

    # 1. Existing reviewer in assign_reviewers
    existing_assign = ContentReviewAssignment(id=uuid.uuid4(), artifact_id=art_id, artifact_version=1, assigned_to="rev1", status="assigned")
    session.scalar.side_effect = [existing_assign, None]
    res_assign = await service.assign_reviewers(
        session,
        artifact_id=art_id,
        reviewer_ids=["rev1", "rev2"],
        assigned_by="lead",
    )
    assert res_assign.assigned_count == 2

    # 2. submit_decision branches:
    # creator reviewing own content
    assignment = ContentReviewAssignment(
        id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        assigned_to="rev1",
        status="assigned",
        assigned_at=now,
    )
    session.scalar.side_effect = None
    session.scalar.return_value = None  # no replay
    with pytest.raises(PermissionError, match="creators cannot review their own content"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="creator_1",
            action=ContentReviewAction.APPROVE,
            rubric_results={},
            idempotency_key="key",
            expected_version=1,
        )

    # reviewer not assigned
    session.scalar.side_effect = [None, None]
    with pytest.raises(PermissionError, match="not assigned to this artifact version"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.APPROVE,
            rubric_results={},
            idempotency_key="key",
            expected_version=1,
        )

    # assignment already approved
    assignment.status = "approved"
    session.scalar.side_effect = [None, assignment]
    with pytest.raises(ReviewConflictError, match="already submitted a decision"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.APPROVE,
            rubric_results={},
            idempotency_key="key",
            expected_version=1,
        )

    # assignment not open (e.g. cancelled)
    assignment.status = "cancelled"
    session.scalar.side_effect = [None, assignment]
    with pytest.raises(ReviewConflictError, match="assignment is not open"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.APPROVE,
            rubric_results={},
            idempotency_key="key",
            expected_version=1,
        )

    # REQUEST_CHANGES and QUARANTINE actions
    assignment.status = "assigned"
    session.scalar.side_effect = [None, assignment]
    res_rc = await service.submit_decision(
        session,
        artifact_id=art_id,
        reviewer_id="rev1",
        action=ContentReviewAction.REQUEST_CHANGES,
        rubric_results={},
        idempotency_key="key_rc",
        expected_version=1,
        reason_code="needs_more_examples",
    )
    assert res_rc.current_status == "revision_required"

    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    assignment.status = "assigned"
    session.scalar.side_effect = [None, assignment]
    res_quar = await service.submit_decision(
        session,
        artifact_id=art_id,
        reviewer_id="rev1",
        action=ContentReviewAction.QUARANTINE,
        rubric_results={},
        idempotency_key="key_q",
        expected_version=1,
        reason_code="safety_violation",
    )
    assert res_quar.current_status == "quarantined"

    # Non-diagnostic approval reaching quorum with non-english language check
    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    assignment.status = "assigned"

    valid_rubric = {k: True for k in REQUIRED_APPROVAL_RUBRIC_CRITERIA}
    # First test missing language competency
    approvals_no_lang = [
        ContentReviewDecision(
            decision_id=uuid.uuid4(),
            artifact_id=art_id,
            artifact_version=1,
            reviewer_id="rev1",
            review_action=ContentReviewAction.APPROVE,
            reviewer_competencies=["caps"],
        ),
        ContentReviewDecision(
            decision_id=uuid.uuid4(),
            artifact_id=art_id,
            artifact_version=1,
            reviewer_id="rev2",
            review_action=ContentReviewAction.APPROVE,
            reviewer_competencies=["subject"],
        ),
    ]
    service._valid_approvals = AsyncMock(return_value=approvals_no_lang)
    session.scalar.side_effect = [None, assignment]
    with pytest.raises(ValueError, match="requires a language-competent reviewer"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.APPROVE,
            rubric_results=valid_rubric,
            idempotency_key="key_appr_lang_fail",
            expected_version=1,
        )

    # Missing CAPS/subject competency
    assignment.status = "assigned"
    approvals_no_caps = [
        ContentReviewDecision(
            decision_id=uuid.uuid4(),
            artifact_id=art_id,
            artifact_version=1,
            reviewer_id="rev1",
            review_action=ContentReviewAction.APPROVE,
            reviewer_competencies=["language"],
        ),
        ContentReviewDecision(
            decision_id=uuid.uuid4(),
            artifact_id=art_id,
            artifact_version=1,
            reviewer_id="rev2",
            review_action=ContentReviewAction.APPROVE,
            reviewer_competencies=["language:af"],
        ),
    ]
    service._valid_approvals = AsyncMock(return_value=approvals_no_caps)
    session.scalar.side_effect = [None, assignment]
    with pytest.raises(ValueError, match="requires at least one subject/CAPS-competent"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.APPROVE,
            rubric_results=valid_rubric,
            idempotency_key="key_appr_caps_fail",
            expected_version=1,
        )

    # Rubric failures in _validate_decision_input
    assignment.status = "assigned"
    bad_rubric = dict(valid_rubric)
    bad_rubric["factual_accuracy"] = False
    session.scalar.side_effect = [None, assignment]
    with pytest.raises(ValueError, match="blocked by rubric failures"):
        await service.submit_decision(
            session,
            artifact_id=art_id,
            reviewer_id="rev1",
            action=ContentReviewAction.APPROVE,
            rubric_results=bad_rubric,
            idempotency_key="key_appr_rubric_fail",
            expected_version=1,
        )


    # 3. publish_artifact conflict errors
    # version mismatch
    artifact.version_number = 2
    with pytest.raises(ReviewConflictError, match="Artifact version changed before publication"):
        await service.publish_artifact(session, artifact_id=art_id, actor_id="admin", expected_version=1, reason="pub")

    artifact.version_number = 1
    # not promoted_production
    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    with pytest.raises(ReviewConflictError, match="requires promoted_production status"):
        await service.publish_artifact(session, artifact_id=art_id, actor_id="admin", expected_version=1, reason="pub")

    # not publication eligible
    artifact.status = ContentArtifactStatus.PROMOTED_PRODUCTION
    artifact.publication_eligible = False
    with pytest.raises(ReviewConflictError, match="not publication eligible"):
        await service.publish_artifact(session, artifact_id=art_id, actor_id="admin", expected_version=1, reason="pub")

    # diagnostic without verified answer key
    from app.models.content_factory import ContentLayer as ModelContentLayer
    artifact.publication_eligible = True
    artifact.content_layer = ModelContentLayer.DIAGNOSTIC_ITEMS
    artifact.artifact_type = ContentArtifactType.DIAGNOSTIC_ITEM
    artifact.answer_key_verified = False


    with pytest.raises(ReviewConflictError, match="independent answer-key verification"):
        await service.publish_artifact(session, artifact_id=art_id, actor_id="admin", expected_version=1, reason="pub")

    # insufficient quorum
    artifact.answer_key_verified = True
    artifact.approval_count = 1
    session.scalar.side_effect = None
    session.scalar.return_value = 0
    with pytest.raises(ReviewConflictError, match="configured educator quorum"):
        await service.publish_artifact(session, artifact_id=art_id, actor_id="admin", expected_version=1, reason="pub")

    # blocked by review decision
    artifact.approval_count = 2
    session.scalar.side_effect = None
    session.scalar.return_value = 1  # 1 blocking decision
    with pytest.raises(ReviewConflictError, match="blocked by a review decision"):
        await service.publish_artifact(session, artifact_id=art_id, actor_id="admin", expected_version=1, reason="pub")


    # 4. reassign_assignment error branches
    # original not found
    session.scalar.side_effect = None
    session.scalar.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await service.reassign_assignment(session, assignment_id=assignment.id, new_reviewer_id="rev2", assigned_by="admin", reason="r")

    # original inactive
    assignment.status = "resolved"
    session.scalar.return_value = assignment
    with pytest.raises(ReviewConflictError, match="Only active assignments can be reassigned"):
        await service.reassign_assignment(session, assignment_id=assignment.id, new_reviewer_id="rev2", assigned_by="admin", reason="r")

    # same reviewer
    assignment.status = "assigned"
    assignment.assigned_to = "rev2"
    with pytest.raises(ValueError, match="replacement reviewer must be different"):
        await service.reassign_assignment(session, assignment_id=assignment.id, new_reviewer_id="rev2", assigned_by="admin", reason="r")

    # creator as replacement reviewer
    assignment.assigned_to = "rev1"
    with pytest.raises(ValueError, match="creator cannot be assigned"):
        await service.reassign_assignment(session, assignment_id=assignment.id, new_reviewer_id="creator_1", assigned_by="admin", reason="r")

    # replacement reviewer already assigned
    existing_rep = ContentReviewAssignment(id=uuid.uuid4(), artifact_id=art_id, artifact_version=1, assigned_to="rev3", status="assigned")
    session.scalar.side_effect = [assignment, existing_rep]
    with pytest.raises(ReviewConflictError, match="replacement reviewer is already assigned"):
        await service.reassign_assignment(session, assignment_id=assignment.id, new_reviewer_id="rev3", assigned_by="admin", reason="r")

    # 5. record_external_transition & list_stale_assignments
    trans = await service.record_external_transition(
        session,
        artifact=artifact,
        previous_status="pending_review",
        new_status="approved",
        actor_id="admin",
        reason_code="manual",
    )
    assert isinstance(trans, ContentStateTransitionEvent)

    session.scalars.return_value = MagicMock(all=MagicMock(return_value=[assignment]))
    stale_list = await service.list_stale_assignments(session)
    assert len(stale_list) == 1

    # 6. Real _load_artifact and _load_artifact_for_update queries
    session.scalar.side_effect = None
    session.scalar.return_value = artifact
    loaded1 = await service._load_artifact(session, art_id, include_sources=True)
    assert loaded1 == artifact
    loaded2 = await service._load_artifact_for_update(session, art_id, include_sources=True)
    assert loaded2 == artifact

    # 7. Quarantine validation branches
    with pytest.raises(ValueError, match="Quarantine requires a reason code and explanation"):
        await service.quarantine_artifact(session, artifact_id=art_id, actor_id="admin", reason_code="", reason=" ")

    artifact.status = ContentArtifactStatus.SUPERSEDED
    with pytest.raises(ReviewConflictError, match="Superseded artifacts are already ineligible"):
        await service.quarantine_artifact(session, artifact_id=art_id, actor_id="admin", reason_code="code", reason="exp")

    # 8. Revision validation branches
    with pytest.raises(ValueError, match="revised artifact payload is required"):
        await service.create_revision(session, artifact_id=art_id, actor_id="admin", artifact_json={}, reason="r", expected_version=1)

    artifact.version_number = 2
    with pytest.raises(ReviewConflictError, match="Artifact version changed"):
        await service.create_revision(session, artifact_id=art_id, actor_id="admin", artifact_json={"q": 1}, reason="r", expected_version=1)

    artifact.version_number = 1
    artifact.status = ContentArtifactStatus.SUPERSEDED
    with pytest.raises(ReviewConflictError, match="Superseded artifacts cannot be revised again"):
        await service.create_revision(session, artifact_id=art_id, actor_id="admin", artifact_json={"q": 1}, reason="r", expected_version=1)

    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    from app.services.content_factory import stable_json_hash
    same_json = {"q": "same"}
    artifact.artifact_hash = stable_json_hash(same_json)
    with pytest.raises(ValueError, match="Material revisions must change"):
        await service.create_revision(session, artifact_id=art_id, actor_id="admin", artifact_json=same_json, reason="r", expected_version=1)


