"""Comprehensive unit tests for content review governance policies, eligibility, and consensus result dataclasses."""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock
import pytest

from app.services.content_review_governance import (
    REQUIRED_APPROVAL_RUBRIC_CRITERIA,
    ReviewGovernancePolicy,
    ReviewDecisionResult,
    ReviewAssignmentResult,
    ArtifactRevisionResult,
    ContentReviewEligibilityService,
)
from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact


class TestReviewGovernancePolicyAndRubric:
    def test_rubric_criteria_completeness(self):
        assert len(REQUIRED_APPROVAL_RUBRIC_CRITERIA) == 10
        assert "caps_alignment" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "factual_accuracy" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "answer_key_correctness" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "bias_and_safety" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "personal_information" in REQUIRED_APPROVAL_RUBRIC_CRITERIA

    def test_review_governance_policy_defaults(self):
        policy = ReviewGovernancePolicy()
        assert policy.quorum_threshold == 3
        assert policy.stale_after_hours == 72
        assert policy.creator_approval_counts is False
        assert policy.direct_publish_allowed is False

    def test_review_decision_result_dataclass(self):
        did = uuid.uuid4()
        aid = uuid.uuid4()
        res = ReviewDecisionResult(
            decision_id=did,
            artifact_id=aid,
            artifact_version=1,
            action="approve",
            previous_status="staged",
            current_status="approved",
            approval_count=3,
            quorum_threshold=3,
            quorum_reached=True,
        )
        assert res.decision_id == did
        assert res.quorum_reached is True
        assert res.idempotent_replay is False

    def test_review_assignment_result_dataclass(self):
        aid = uuid.uuid4()
        asg1 = uuid.uuid4()
        asg2 = uuid.uuid4()
        res = ReviewAssignmentResult(
            assignment_ids=[asg1, asg2],
            artifact_id=aid,
            artifact_version=1,
            assigned_count=2,
        )
        assert len(res.assignment_ids) == 2
        assert res.assigned_count == 2


class TestContentReviewEligibility:
    def test_is_retrieval_eligible(self):
        art_promoted = MagicMock(spec=ContentGenerationArtifact)
        art_promoted.status = ContentArtifactStatus.PROMOTED_PRODUCTION.value
        art_promoted.publication_eligible = True

        art_draft = MagicMock(spec=ContentGenerationArtifact)
        art_draft.status = ContentArtifactStatus.DRAFT.value
        art_draft.publication_eligible = False

        assert ContentReviewEligibilityService.is_retrieval_eligible(art_promoted) is True
        assert ContentReviewEligibilityService.is_retrieval_eligible(art_draft) is False

    def test_assert_retrieval_eligible_raises(self):
        art_draft = MagicMock(spec=ContentGenerationArtifact)
        art_draft.status = ContentArtifactStatus.DRAFT.value
        art_draft.publication_eligible = False

        with pytest.raises(ValueError, match="not eligible for semantic retrieval"):
            ContentReviewEligibilityService.assert_retrieval_eligible(art_draft)
