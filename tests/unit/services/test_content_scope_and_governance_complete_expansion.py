"""Comprehensive unit tests covering content_scope_registry and content_review_governance."""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest

from app.domain.content_coverage import ContentLayer
from app.domain.content_scope import ContentScopeStatus
from app.models.content_factory import (
    ContentAnswerKeyVerification,
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
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
    ReviewAssignmentResult,
    ReviewConflictError,

    ReviewDecisionResult,
    ReviewGovernancePolicy,
    _env_bool,
    _rubric_passed,
    _source_payload,
    _value,
)
from app.services.content_scope_registry import (
    ContentScopeRegistry,
    ContentScopeRegistryError,
)


# ============================================================================
# ContentScopeRegistry Tests
# ============================================================================
def test_content_scope_registry_default():
    registry = ContentScopeRegistry()

    # list_scopes and list_active_scopes
    scopes = registry.list_scopes()
    assert len(scopes) > 0

    first_scope = scopes[0]
    scope_id = first_scope.scope_id

    assert registry.get_scope(scope_id).scope_id == scope_id
    refs = registry.get_scope_caps_refs(scope_id)
    assert isinstance(refs, list)

    targets = registry.get_scope_targets(scope_id)
    assert isinstance(targets, list)
    if targets:
        first_target = targets[0]
        # test get_coverage_target
        layer = ContentLayer.DIAGNOSTIC_ITEMS
        try:
            val = registry.get_coverage_target(scope_id, first_target.caps_ref, layer)
            assert isinstance(val, int)
        except LookupError:
            pass

    # Unknown scope lookup raises LookupError
    with pytest.raises(LookupError, match="Unknown content scope"):
        registry.get_scope("non_existent_scope_123")

    with pytest.raises(LookupError, match="No coverage target"):
        registry._get_target(scope_id, "99.NON_EXISTENT.1")


def test_content_scope_registry_errors(tmp_path):
    # Test duplicate scopes error
    scopes_file = tmp_path / "scopes.json"
    scopes_file.write_text(
        """{
        "schema_version": "1.0",
        "scopes": [
            {"scope_id": "dup_1", "grade": 1, "subject_code": "M", "subject": "Math", "language": "en", "curriculum": "CAPS", "status": "draft", "caps_refs": []},
            {"scope_id": "dup_1", "grade": 1, "subject_code": "M", "subject": "Math", "language": "en", "curriculum": "CAPS", "status": "draft", "caps_refs": []}
        ]}""",
        encoding="utf-8",
    )
    targets_file = tmp_path / "targets.json"
    targets_file.write_text('{"schema_version": "1.0", "targets": []}', encoding="utf-8")

    reg = ContentScopeRegistry(scopes_path=scopes_file, targets_path=targets_file, project_root=tmp_path)
    with pytest.raises(ContentScopeRegistryError, match="Duplicate scope_id"):
        _ = reg._scopes

    # Test active scope without topic_map_path
    scopes_file.write_text(
        """{
        "schema_version": "1.0",
        "scopes": [
            {"scope_id": "act_1", "grade": 1, "subject_code": "M", "subject": "Math", "language": "en", "curriculum": "CAPS", "status": "active", "caps_refs": []}
        ]}""",
        encoding="utf-8",
    )
    reg2 = ContentScopeRegistry(scopes_path=scopes_file, targets_path=targets_file, project_root=tmp_path)
    with pytest.raises(ContentScopeRegistryError, match="must declare topic_map_path"):
        _ = reg2._scopes

    # Test caps refs without topic_map_path
    scopes_file.write_text(
        """{
        "schema_version": "1.0",
        "scopes": [
            {"scope_id": "draft_1", "grade": 1, "subject_code": "M", "subject": "Math", "language": "en", "curriculum": "CAPS", "status": "draft", "caps_refs": ["1.M.1"]}
        ]}""",
        encoding="utf-8",
    )
    reg3 = ContentScopeRegistry(scopes_path=scopes_file, targets_path=targets_file, project_root=tmp_path)
    with pytest.raises(ContentScopeRegistryError, match="declares CAPS refs without a topic_map_path"):
        _ = reg3._scopes


def test_content_scope_registry_active_and_target_keys():
    reg = ContentScopeRegistry()
    active_scopes = reg.list_active_scopes()
    assert isinstance(active_scopes, list)
    if active_scopes:
        act = active_scopes[0]
        assert reg.is_scope_active(act.scope_id) is True
        assert reg.require_active_scope(act.scope_id).scope_id == act.scope_id

    # Test non-active require_active_scope
    non_active = [s for s in reg.list_scopes() if s.status != ContentScopeStatus.ACTIVE]
    if non_active:
        na_id = non_active[0].scope_id
        assert reg.is_scope_active(na_id) is False
        with pytest.raises(LookupError, match="is not active"):
            reg.require_active_scope(na_id)



# ============================================================================
# ReviewGovernancePolicy & Eligibility Tests
# ============================================================================
def test_governance_policy_and_eligibility():
    # Policy environment parsing
    with patch.dict("os.environ", {"CONTENT_CONSENSUS_THRESHOLD": "4", "CONTENT_CONSENSUS_TIMEOUT_HOURS": "48"}):
        pol = ReviewGovernancePolicy.from_environment()
        assert pol.quorum_threshold == 4
        assert pol.stale_after_hours == 48

    with patch.dict("os.environ", {"CONTENT_CONSENSUS_THRESHOLD": "1"}):
        with pytest.raises(ValueError, match="between 2 and 10"):
            ReviewGovernancePolicy.from_environment()

    with patch.dict("os.environ", {"CONTENT_CONSENSUS_THRESHOLD": "3", "CONTENT_CONSENSUS_TIMEOUT_HOURS": "0"}):
        with pytest.raises(ValueError, match="must be positive"):
            ReviewGovernancePolicy.from_environment()

    # Eligibility service
    art = ContentGenerationArtifact(
        artifact_id=uuid.uuid4(),
        status=ContentArtifactStatus.PROMOTED_PRODUCTION,
        publication_eligible=True,
        published_at=datetime.now(timezone.utc),
    )
    assert ContentReviewEligibilityService.is_retrieval_eligible(art) is True
    assert ContentReviewEligibilityService.is_learner_eligible(art) is False

    ContentReviewEligibilityService.assert_retrieval_eligible(art)
    with pytest.raises(ValueError, match="not eligible for learner delivery"):
        ContentReviewEligibilityService.assert_learner_eligible(art)

    art.status = ContentArtifactStatus.PUBLISHED
    assert ContentReviewEligibilityService.is_learner_eligible(art) is True
    ContentReviewEligibilityService.assert_learner_eligible(art)


# ============================================================================
# ContentReviewGovernanceService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_review_governance_assignment_and_decisions():
    factory_mock = AsyncMock(spec=ContentFactoryService)
    factory_mock.assert_artifact_has_approved_sources = AsyncMock()
    policy = ReviewGovernancePolicy(quorum_threshold=2, stale_after_hours=24)
    service = ContentReviewGovernanceService(policy=policy, factory_service=factory_mock)

    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    art_id = uuid.uuid4()
    art = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
        row_version=1,
        status=ContentArtifactStatus.PENDING_REVIEW,
        created_by_actor_id="creator_1",
        artifact_type="lesson",
        language="en",
        publication_eligible=False,
        approval_count=0,
    )
    service._load_artifact_for_update = AsyncMock(return_value=art)
    service._load_artifact = AsyncMock(return_value=art)

    # 1. assign_reviewers
    # Creator cannot be assigned
    with pytest.raises(ValueError, match="creator cannot be assigned"):
        await service.assign_reviewers(
            session,
            artifact_id=art_id,
            reviewer_ids=["creator_1", "rev_2"],
            assigned_by="admin",
        )

    # Quorum threshold check
    with pytest.raises(ValueError, match="distinct reviewers must be assigned"):
        await service.assign_reviewers(
            session,
            artifact_id=art_id,
            reviewer_ids=["rev_2"],
            assigned_by="admin",
        )

    session.scalar.return_value = None  # No existing assignment
    res_assign = await service.assign_reviewers(
        session,
        artifact_id=art_id,
        reviewer_ids=["rev_1", "rev_2"],
        assigned_by="admin",
        reviewer_competencies={"rev_1": ["subject", "caps"]},
        idempotency_key="key_1",
    )
    assert isinstance(res_assign, ReviewAssignmentResult)
    assert res_assign.assigned_count == 2

    # 2. accept_assignment
    assignment_id = uuid.uuid4()
    mock_assignment = ContentReviewAssignment(
        id=assignment_id,
        artifact_id=art_id,
        artifact_version=1,
        assigned_to="rev_1",
        status="assigned",
        reviewer_competencies=["subject"],
    )
    session.scalar.return_value = mock_assignment

    # Wrong reviewer
    with pytest.raises(PermissionError, match="assigned reviewer"):
        await service.accept_assignment(
            session, assignment_id=assignment_id, reviewer_id="wrong_rev", conflict_of_interest=False
        )

    # Successful acceptance with conflict
    acc_conf = await service.accept_assignment(
        session, assignment_id=assignment_id, reviewer_id="rev_1", conflict_of_interest=True
    )
    assert acc_conf.status == "conflict"
    assert acc_conf.conflict_of_interest is True

    # 3. submit_decision
    # Idempotent replay
    replay_decision = ContentReviewDecision(
        decision_id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        reviewer_id="rev_1",
        review_action=ContentReviewAction.APPROVE,
        idempotency_key="replay_key",
    )
    session.scalar.return_value = replay_decision
    res_replay = await service.submit_decision(
        session,
        artifact_id=art_id,
        reviewer_id="rev_1",
        action=ContentReviewAction.APPROVE,
        rubric_results={},
        idempotency_key="replay_key",
        expected_version=1,
    )
    assert res_replay.idempotent_replay is True

    # Fresh decision submission
    session.scalar.side_effect = [None, mock_assignment, None]  # replay check returns None, then assignment
    mock_assignment.status = "in_review"
    mock_assignment.conflict_of_interest = False

    # Valid rubric for approval
    full_rubric = {k: True for k in REQUIRED_APPROVAL_RUBRIC_CRITERIA}
    mock_approval_1 = ContentReviewDecision(
        decision_id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        reviewer_id="rev_1",
        review_action=ContentReviewAction.APPROVE,
        reviewer_competencies=["subject", "caps"],
        conflict_of_interest=False,
    )
    mock_approval_2 = ContentReviewDecision(
        decision_id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        reviewer_id="rev_2",
        review_action=ContentReviewAction.APPROVE,
        reviewer_competencies=["curriculum"],
        conflict_of_interest=False,
    )
    service._valid_approvals = AsyncMock(return_value=[mock_approval_1, mock_approval_2])

    res_dec = await service.submit_decision(
        session,
        artifact_id=art_id,
        reviewer_id="rev_1",
        action=ContentReviewAction.APPROVE,
        rubric_results=full_rubric,
        idempotency_key="fresh_key_1",
        expected_version=1,
    )
    assert res_dec.current_status == ContentArtifactStatus.APPROVED.value
    assert res_dec.quorum_reached is True

    # 4. quarantine_artifact & publish_artifact
    quar_art = await service.quarantine_artifact(
        session,
        artifact_id=art_id,
        actor_id="gov_admin",
        reason_code="toxic",
        reason="Offensive content reported",
    )
    assert quar_art.status == ContentArtifactStatus.QUARANTINED

    # publish_artifact checks
    art.status = ContentArtifactStatus.PROMOTED_PRODUCTION
    art.publication_eligible = True
    art.approval_count = 2
    session.scalar.return_value = 0  # No blocking decisions
    pub_art = await service.publish_artifact(
        session,
        artifact_id=art_id,
        actor_id="publisher_1",
        expected_version=1,
        reason="Ready for learner delivery",
    )
    assert pub_art.status == ContentArtifactStatus.PUBLISHED
    assert pub_art.published_at is not None

    # 5. create_revision
    factory_mock.create_artifact.return_value = MagicMock(
        artifact_id=uuid.uuid4(),
        version_number=2,
        status=ContentArtifactStatus.PENDING_REVIEW,
    )
    art.artifact_hash = "old_hash_1"
    art.sources = []
    rev_res = await service.create_revision(
        session,
        artifact_id=art_id,
        actor_id="editor_1",
        artifact_json={"updated_field": "new_value"},
        reason="Updated explanation for clarity",
        expected_version=1,
    )
    assert isinstance(rev_res, ArtifactRevisionResult)
    assert rev_res.version_number == 2

    # 6. reassign_assignment
    mock_assignment.status = "assigned"
    mock_assignment.assigned_to = "old_reviewer"
    mock_assignment.artifact_version = 1
    session.scalar.side_effect = [mock_assignment, None]  # original found, replacement not already assigned
    reassigned = await service.reassign_assignment(
        session,
        assignment_id=assignment_id,
        new_reviewer_id="new_reviewer",
        assigned_by="admin",
        reason="Unavailable reviewer",
    )
    assert reassigned.assigned_to == "new_reviewer"

    # 7. list_history
    session.scalars.return_value = MagicMock(all=MagicMock(return_value=[]))
    history = await service.list_history(session, art_id)
    assert "decisions" in history
    assert "transitions" in history

    # 8. Helpers
    assert _rubric_passed(True) is True
    assert _rubric_passed(0.9) is True
    assert _rubric_passed(0.5) is False
    assert _rubric_passed("approved") is True
    assert _rubric_passed({"result": "pass"}) is True
    assert _env_bool("NON_EXISTENT_VAR", True) is True
    assert _env_bool("NON_EXISTENT_VAR", False) is False

