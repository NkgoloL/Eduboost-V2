"""Batch 211: Unit tests for content_review_governance.py covering ReviewGovernancePolicy, ContentReviewEligibilityService, and ContentReviewGovernanceService assignment/decision workflows."""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact, ContentReviewAssignment
from app.services.content_review_governance import (
    ReviewGovernancePolicy,
    ReviewDecisionResult,
    ReviewAssignmentResult,
    ContentReviewEligibilityService,
    ContentReviewGovernanceService,
    REQUIRED_APPROVAL_RUBRIC_CRITERIA,
)


class TestReviewGovernancePolicyAndEligibility:
    def test_required_criteria_constants(self):
        assert "caps_alignment" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "factual_accuracy" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "answer_key_correctness" in REQUIRED_APPROVAL_RUBRIC_CRITERIA

    def test_policy_from_environment_defaults(self):
        policy = ReviewGovernancePolicy.from_environment()
        assert policy.quorum_threshold == 3
        assert policy.stale_after_hours == 72
        assert policy.creator_approval_counts is False

    def test_policy_invalid_threshold(self):
        with patch.dict("os.environ", {"CONTENT_CONSENSUS_THRESHOLD": "1"}):
            with pytest.raises(ValueError, match="between 2 and 10"):
                ReviewGovernancePolicy.from_environment()

    def test_eligibility_retrieval_and_learner(self):
        art = MagicMock()
        art.status = ContentArtifactStatus.PROMOTED_PRODUCTION.value
        art.publication_eligible = True
        art.published_at = None

        assert ContentReviewEligibilityService.is_retrieval_eligible(art) is True
        assert ContentReviewEligibilityService.is_learner_eligible(art) is False

        art.status = ContentArtifactStatus.PUBLISHED.value
        from datetime import datetime, timezone
        art.published_at = datetime.now(timezone.utc)
        assert ContentReviewEligibilityService.is_learner_eligible(art) is True

    def test_assert_eligibility_raises(self):
        art = MagicMock()
        art.status = ContentArtifactStatus.DRAFT.value
        art.publication_eligible = False
        art.published_at = None

        with pytest.raises(ValueError, match="not eligible for semantic retrieval"):
            ContentReviewEligibilityService.assert_retrieval_eligible(art)

        with pytest.raises(ValueError, match="not eligible for learner delivery"):
            ContentReviewEligibilityService.assert_learner_eligible(art)


class TestContentReviewGovernanceServiceOperations:
    @pytest.mark.asyncio
    async def test_assign_reviewers_insufficient_count_raises(self):
        service = ContentReviewGovernanceService()
        art_id = uuid.uuid4()
        
        mock_art = MagicMock()
        mock_art.status = ContentArtifactStatus.PENDING_REVIEW.value
        mock_art.created_by_actor_id = "creator-01"
        service._load_artifact_for_update = AsyncMock(return_value=mock_art)

        session = MagicMock()
        with pytest.raises(ValueError, match="distinct reviewers must be assigned"):
            await service.assign_reviewers(
                session,
                artifact_id=art_id,
                reviewer_ids=["rev1"],  # only 1, needs quorum 3
                assigned_by="lead",
            )

    @pytest.mark.asyncio
    async def test_accept_assignment_conflict_flow(self):
        service = ContentReviewGovernanceService()
        asgn_id = uuid.uuid4()

        mock_asgn = MagicMock()
        mock_asgn.id = asgn_id
        mock_asgn.assigned_to = "educator_1"
        mock_asgn.status = "assigned"

        session = MagicMock()
        session.scalar = AsyncMock(return_value=mock_asgn)
        session.flush = AsyncMock()

        res = await service.accept_assignment(
            session,
            assignment_id=asgn_id,
            reviewer_id="educator_1",
            conflict_of_interest=True,
        )
        assert res.status == "conflict"
        assert res.conflict_of_interest is True
        assert res.accepted_at is not None

    @pytest.mark.asyncio
    async def test_accept_assignment_unauthorized_raises(self):
        service = ContentReviewGovernanceService()
        asgn_id = uuid.uuid4()

        mock_asgn = MagicMock()
        mock_asgn.assigned_to = "educator_1"
        mock_asgn.status = "assigned"

        session = MagicMock()
        session.scalar = AsyncMock(return_value=mock_asgn)

        with pytest.raises(PermissionError, match="may only be accepted by the assigned reviewer"):
            await service.accept_assignment(
                session,
                assignment_id=asgn_id,
                reviewer_id="imposter",
                conflict_of_interest=False,
            )
