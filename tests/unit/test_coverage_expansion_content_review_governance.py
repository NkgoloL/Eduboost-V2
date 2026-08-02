"""
Unit tests for app.services.content_review_governance module.
Covers ReviewGovernancePolicy initialization/environment parsing,
ContentReviewEligibilityService assertion logic, dataclasses, and
pure governance methods.
"""
from __future__ import annotations

import os
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact
from app.services.content_review_governance import (
    ArtifactRevisionResult,
    ContentReviewEligibilityService,
    ContentReviewGovernanceService,
    REQUIRED_APPROVAL_RUBRIC_CRITERIA,
    ReviewAssignmentResult,
    ReviewDecisionResult,
    ReviewGovernancePolicy,
)


class TestReviewGovernancePolicy:
    def test_default_init(self):
        policy = ReviewGovernancePolicy()
        assert policy.version == "phase3-v1"
        assert policy.quorum_threshold == 3
        assert policy.stale_after_hours == 72
        assert policy.creator_approval_counts is False
        assert policy.direct_publish_allowed is False

    def test_from_environment_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            policy = ReviewGovernancePolicy.from_environment()
            assert policy.quorum_threshold == 3
            assert policy.stale_after_hours == 72

    def test_from_environment_custom_valid(self):
        env = {
            "CONTENT_CONSENSUS_THRESHOLD": "5",
            "CONTENT_CONSENSUS_TIMEOUT_HOURS": "48",
            "CONTENT_CREATOR_APPROVAL_COUNTS": "true",
            "CONTENT_DIRECT_PUBLISH_ALLOWED": "1",
        }
        with patch.dict(os.environ, env, clear=True):
            policy = ReviewGovernancePolicy.from_environment()
            assert policy.quorum_threshold == 5
            assert policy.stale_after_hours == 48
            assert policy.creator_approval_counts is True
            assert policy.direct_publish_allowed is True

    def test_from_environment_invalid_threshold_low(self):
        with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "1"}, clear=True):
            with pytest.raises(ValueError, match="CONTENT_CONSENSUS_THRESHOLD must be between 2 and 10"):
                ReviewGovernancePolicy.from_environment()

    def test_from_environment_invalid_threshold_high(self):
        with patch.dict(os.environ, {"CONTENT_CONSENSUS_THRESHOLD": "11"}, clear=True):
            with pytest.raises(ValueError, match="CONTENT_CONSENSUS_THRESHOLD must be between 2 and 10"):
                ReviewGovernancePolicy.from_environment()

    def test_from_environment_invalid_timeout(self):
        with patch.dict(os.environ, {"CONTENT_CONSENSUS_TIMEOUT_HOURS": "0"}, clear=True):
            with pytest.raises(ValueError, match="CONTENT_CONSENSUS_TIMEOUT_HOURS must be positive"):
                ReviewGovernancePolicy.from_environment()


class TestDataclasses:
    def test_review_decision_result(self):
        d_id = uuid.uuid4()
        a_id = uuid.uuid4()
        res = ReviewDecisionResult(
            decision_id=d_id,
            artifact_id=a_id,
            artifact_version=1,
            action="approve",
            previous_status="pending_review",
            current_status="approved",
            approval_count=3,
            quorum_threshold=3,
            quorum_reached=True,
        )
        assert res.decision_id == d_id
        assert res.quorum_reached is True
        assert res.idempotent_replay is False

    def test_review_assignment_result(self):
        a_id = uuid.uuid4()
        as_ids = [uuid.uuid4(), uuid.uuid4()]
        res = ReviewAssignmentResult(
            assignment_ids=as_ids,
            artifact_id=a_id,
            artifact_version=1,
            assigned_count=2,
        )
        assert res.assigned_count == 2
        assert len(res.assignment_ids) == 2

    def test_artifact_revision_result(self):
        prev = uuid.uuid4()
        new = uuid.uuid4()
        res = ArtifactRevisionResult(
            previous_artifact_id=prev,
            new_artifact_id=new,
            version_number=2,
            status="pending_review",
        )
        assert res.version_number == 2
        assert res.status == "pending_review"


class TestContentReviewEligibilityService:
    def test_retrieval_eligible_true(self):
        art = MagicMock(spec=ContentGenerationArtifact)
        art.status = ContentArtifactStatus.PUBLISHED
        art.publication_eligible = True
        assert ContentReviewEligibilityService.is_retrieval_eligible(art) is True

    def test_retrieval_eligible_promoted_production(self):
        art = MagicMock(spec=ContentGenerationArtifact)
        art.status = ContentArtifactStatus.PROMOTED_PRODUCTION
        art.publication_eligible = True
        assert ContentReviewEligibilityService.is_retrieval_eligible(art) is True

    def test_retrieval_eligible_false_when_not_publication_eligible(self):
        art = MagicMock(spec=ContentGenerationArtifact)
        art.status = ContentArtifactStatus.PUBLISHED
        art.publication_eligible = False
        assert ContentReviewEligibilityService.is_retrieval_eligible(art) is False

    def test_retrieval_eligible_false_unsupported_status(self):
        art = MagicMock(spec=ContentGenerationArtifact)
        art.status = ContentArtifactStatus.PENDING_REVIEW
        art.publication_eligible = True
        assert ContentReviewEligibilityService.is_retrieval_eligible(art) is False

    def test_assert_retrieval_eligible_raises(self):
        art = MagicMock(spec=ContentGenerationArtifact)
        art.status = ContentArtifactStatus.PENDING_REVIEW
        art.publication_eligible = False
        with pytest.raises(ValueError, match="not eligible for semantic retrieval"):
            ContentReviewEligibilityService.assert_retrieval_eligible(art)

    def test_learner_eligible_true(self):
        art = MagicMock(spec=ContentGenerationArtifact)
        art.status = ContentArtifactStatus.PUBLISHED
        art.published_at = "2026-08-01T00:00:00Z"
        assert ContentReviewEligibilityService.is_learner_eligible(art) is True

    def test_learner_eligible_false_when_not_published_at(self):
        art = MagicMock(spec=ContentGenerationArtifact)
        art.status = ContentArtifactStatus.PUBLISHED
        art.published_at = None
        assert ContentReviewEligibilityService.is_learner_eligible(art) is False

    def test_assert_learner_eligible_raises(self):
        art = MagicMock(spec=ContentGenerationArtifact)
        art.status = ContentArtifactStatus.APPROVED
        art.published_at = None
        with pytest.raises(ValueError, match="not eligible for learner delivery"):
            ContentReviewEligibilityService.assert_learner_eligible(art)


class TestContentReviewGovernanceServiceInit:
    def test_init_defaults(self):
        svc = ContentReviewGovernanceService()
        assert svc.policy is not None
        assert svc.factory_service is not None

    def test_required_criteria_present(self):
        assert "caps_alignment" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "factual_accuracy" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "bias_and_safety" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
