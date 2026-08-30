import os
import uuid
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.content_review_governance import (
    ReviewGovernancePolicy,
    ReviewDecisionResult,
    ReviewAssignmentResult,
    ArtifactRevisionResult,
    ContentReviewEligibilityService,
    ContentReviewGovernanceService,
    REQUIRED_APPROVAL_RUBRIC_CRITERIA,
    _env_bool,
    _value,
    _rubric_passed,
)
from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAssignment,
    ContentReviewDecision,
    ContentReviewAction,
)


def test_review_governance_policy_defaults_and_env():
    policy = ReviewGovernancePolicy()
    assert policy.quorum_threshold == 3
    assert policy.version == "phase3-v1"
    assert policy.creator_approval_counts is False

    with patch.dict(os.environ, {
        "CONTENT_CONSENSUS_THRESHOLD": "4",
        "CONTENT_CONSENSUS_TIMEOUT_HOURS": "48",
        "CONTENT_CREATOR_APPROVAL_COUNTS": "true",
        "CONTENT_DIRECT_PUBLISH_ALLOWED": "1",
    }):
        env_policy = ReviewGovernancePolicy.from_environment()
        assert env_policy.quorum_threshold == 4
        assert env_policy.stale_after_hours == 48
        assert env_policy.creator_approval_counts is True
        assert env_policy.direct_publish_allowed is True


def test_review_governance_policy_invalid_env():
    with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "1"}):
        with pytest.raises(ValueError, match="CONTENT_CONSENSUS_THRESHOLD must be between 2 and 10"):
            ReviewGovernancePolicy.from_environment()

    with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "3", "CONTENT_CONSENSUS_TIMEOUT_HOURS": "0"}):
        with pytest.raises(ValueError, match="CONTENT_CONSENSUS_TIMEOUT_HOURS must be positive"):
            ReviewGovernancePolicy.from_environment()


def test_eligibility_service():
    artifact = MagicMock(spec=ContentGenerationArtifact)
    artifact.status = ContentArtifactStatus.PROMOTED_PRODUCTION.value
    artifact.publication_eligible = True
    artifact.published_at = None

    assert ContentReviewEligibilityService.is_retrieval_eligible(artifact) is True
    assert ContentReviewEligibilityService.is_learner_eligible(artifact) is False

    ContentReviewEligibilityService.assert_retrieval_eligible(artifact)
    with pytest.raises(ValueError, match="Artifact is not eligible for learner delivery"):
        ContentReviewEligibilityService.assert_learner_eligible(artifact)

    artifact.status = ContentArtifactStatus.PUBLISHED.value
    artifact.published_at = datetime.now(timezone.utc)
    assert ContentReviewEligibilityService.is_learner_eligible(artifact) is True
    ContentReviewEligibilityService.assert_learner_eligible(artifact)

    artifact.publication_eligible = False
    assert ContentReviewEligibilityService.is_retrieval_eligible(artifact) is False
    with pytest.raises(ValueError, match="Artifact is not eligible for semantic retrieval"):
        ContentReviewEligibilityService.assert_retrieval_eligible(artifact)


def test_helpers_and_hashes():
    assert _env_bool("NOT_SET", True) is True
    with patch.dict(os.environ, {"TEST_KEY": "yes"}):
        assert _env_bool("TEST_KEY", False) is True
    with patch.dict(os.environ, {"TEST_KEY": "0"}):
        assert _env_bool("TEST_KEY", True) is False

    assert _rubric_passed({"passed": True}) is True
    assert _rubric_passed({"passed": False}) is False
    assert _rubric_passed(True) is True
    assert _rubric_passed(False) is False


@pytest.mark.asyncio
async def test_assign_reviewers_validation():
    service = ContentReviewGovernanceService(policy=ReviewGovernancePolicy(quorum_threshold=3, creator_approval_counts=False))
    session = AsyncMock()

    artifact = MagicMock()
    artifact.artifact_id = uuid.uuid4()
    artifact.status = "draft"
    artifact.created_by_actor_id = "creator1"
    artifact.version_number = 1

    service._load_artifact_for_update = AsyncMock(return_value=artifact)

    # Not pending_review
    with pytest.raises(ValueError, match="Reviewers can only be assigned to pending_review artifacts"):
        await service.assign_reviewers(session, artifact_id=artifact.artifact_id, reviewer_ids=["r1", "r2", "r3"], assigned_by="admin")

    artifact.status = ContentArtifactStatus.PENDING_REVIEW.value

    # Quorum too low
    with pytest.raises(ValueError, match="At least 3 distinct reviewers must be assigned"):
        await service.assign_reviewers(session, artifact_id=artifact.artifact_id, reviewer_ids=["r1", "r2"], assigned_by="admin")

    # Creator assigned
    with pytest.raises(ValueError, match="The artifact creator cannot be assigned"):
        await service.assign_reviewers(session, artifact_id=artifact.artifact_id, reviewer_ids=["creator1", "r2", "r3"], assigned_by="admin")


@pytest.mark.asyncio
async def test_accept_assignment_validation():
    service = ContentReviewGovernanceService()
    session = AsyncMock()
    assignment_id = uuid.uuid4()

    # Not found
    session.scalar.return_value = None
    with pytest.raises(LookupError, match="Review assignment .* not found"):
        await service.accept_assignment(session, assignment_id=assignment_id, reviewer_id="rev1", conflict_of_interest=False)

    # Not assigned reviewer
    assignment = MagicMock(spec=ContentReviewAssignment)
    assignment.assigned_to = "other_rev"
    assignment.status = "assigned"
    session.scalar.return_value = assignment
    with pytest.raises(PermissionError, match="Review assignments may only be accepted by the assigned reviewer"):
        await service.accept_assignment(session, assignment_id=assignment_id, reviewer_id="rev1", conflict_of_interest=False)

    # Status not open
    assignment.assigned_to = "rev1"
    assignment.status = "completed"
    with pytest.raises(ValueError, match="Only open review assignments may be accepted"):
        await service.accept_assignment(session, assignment_id=assignment_id, reviewer_id="rev1", conflict_of_interest=False)

    # Success case conflict
    assignment.status = "assigned"
    res = await service.accept_assignment(session, assignment_id=assignment_id, reviewer_id="rev1", conflict_of_interest=True)
    assert res.status == "conflict"
    assert res.conflict_of_interest is True

    # Success case in_review
    assignment.status = "assigned"
    res = await service.accept_assignment(session, assignment_id=assignment_id, reviewer_id="rev1", conflict_of_interest=False)
    assert res.status == "in_review"
    assert res.conflict_of_interest is False


@pytest.mark.asyncio
async def test_quarantine_artifact():
    service = ContentReviewGovernanceService()
    session = AsyncMock()
    artifact_id = uuid.uuid4()

    with pytest.raises(ValueError, match="Quarantine requires a reason code and explanation"):
        await service.quarantine_artifact(session, artifact_id=artifact_id, actor_id="admin", reason_code="", reason=" ")

    artifact = MagicMock(spec=ContentGenerationArtifact)
    artifact.status = ContentArtifactStatus.PENDING_REVIEW
    artifact.row_version = 1
    service._load_artifact_for_update = AsyncMock(return_value=artifact)
    service._record_transition = AsyncMock()

    res = await service.quarantine_artifact(session, artifact_id=artifact_id, actor_id="admin", reason_code="SAFETY", reason="Severe bias detected")
    assert res.status == ContentArtifactStatus.QUARANTINED
    assert res.publication_eligible is False
    assert res.row_version == 2
    service._record_transition.assert_awaited_once()


@pytest.mark.asyncio
async def test_submit_decision_validations():
    service = ContentReviewGovernanceService()
    session = AsyncMock()
    artifact_id = uuid.uuid4()

    with pytest.raises(ValueError, match="Review decisions require an idempotency key"):
        await service.submit_decision(
            session,
            artifact_id=artifact_id,
            reviewer_id="rev1",
            action="approve",
            rubric_results={},
            idempotency_key="   ",
            expected_version=1,
        )

    # Replay with mismatched metadata
    replay = MagicMock()
    replay.artifact_id = uuid.uuid4() # Mismatch
    replay.artifact_version = 1
    session.scalar.return_value = replay
    with pytest.raises(ValueError, match="Idempotency key was already used for a different decision"):
        await service.submit_decision(
            session,
            artifact_id=artifact_id,
            reviewer_id="rev1",
            action="approve",
            rubric_results={},
            idempotency_key="idem-key-1",
            expected_version=1,
        )

