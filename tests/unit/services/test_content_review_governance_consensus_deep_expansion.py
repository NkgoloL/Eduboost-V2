"""Comprehensive unit tests for educator review governance consensus and eligibility services."""
from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock
import pytest

from app.models.content_factory import ContentArtifactStatus
from app.services.content_review_governance import (
    REQUIRED_APPROVAL_RUBRIC_CRITERIA,
    ReviewGovernancePolicy,
    ReviewDecisionResult,
    ReviewAssignmentResult,
    ArtifactRevisionResult,
    ContentReviewEligibilityService,
)


class TestReviewGovernancePolicy:
    def test_default_policy(self):
        policy = ReviewGovernancePolicy()
        assert policy.quorum_threshold == 3
        assert policy.stale_after_hours == 72
        assert policy.creator_approval_counts is False

    def test_from_environment_custom(self, monkeypatch):
        monkeypatch.setenv("CONTENT_CONSENSUS_THRESHOLD", "4")
        monkeypatch.setenv("CONTENT_CONSENSUS_TIMEOUT_HOURS", "48")
        policy = ReviewGovernancePolicy.from_environment()
        assert policy.quorum_threshold == 4
        assert policy.stale_after_hours == 48

    def test_from_environment_invalid_threshold(self, monkeypatch):
        monkeypatch.setenv("CONTENT_CONSENSUS_THRESHOLD", "1")
        with pytest.raises(ValueError, match="between 2 and 10"):
            ReviewGovernancePolicy.from_environment()

    def test_from_environment_invalid_timeout(self, monkeypatch):
        monkeypatch.setenv("CONTENT_CONSENSUS_TIMEOUT_HOURS", "0")
        with pytest.raises(ValueError, match="must be positive"):
            ReviewGovernancePolicy.from_environment()


class TestContentReviewEligibilityService:
    def test_is_retrieval_eligible(self):
        art_promoted = MagicMock()
        art_promoted.status = ContentArtifactStatus.PROMOTED_PRODUCTION.value
        art_promoted.publication_eligible = True
        assert ContentReviewEligibilityService.is_retrieval_eligible(art_promoted) is True

        art_draft = MagicMock()
        art_draft.status = ContentArtifactStatus.DRAFT.value
        art_draft.publication_eligible = False
        assert ContentReviewEligibilityService.is_retrieval_eligible(art_draft) is False

    def test_is_learner_eligible(self):
        art_published = MagicMock()
        art_published.status = ContentArtifactStatus.PUBLISHED.value
        art_published.published_at = datetime.now(UTC)
        assert ContentReviewEligibilityService.is_learner_eligible(art_published) is True

        art_not_published = MagicMock()
        art_not_published.status = ContentArtifactStatus.PUBLISHED.value
        art_not_published.published_at = None
        assert ContentReviewEligibilityService.is_learner_eligible(art_not_published) is False

    def test_assert_retrieval_eligible_raises(self):
        art_draft = MagicMock()
        art_draft.status = ContentArtifactStatus.DRAFT.value
        art_draft.publication_eligible = False
        with pytest.raises(ValueError, match="not eligible for semantic retrieval"):
            ContentReviewEligibilityService.assert_retrieval_eligible(art_draft)

    def test_assert_learner_eligible_raises(self):
        art_draft = MagicMock()
        art_draft.status = ContentArtifactStatus.DRAFT.value
        art_draft.published_at = None
        with pytest.raises(ValueError, match="not eligible for learner delivery"):
            ContentReviewEligibilityService.assert_learner_eligible(art_draft)


class TestReviewGovernanceDataclasses:
    def test_rubric_criteria_contents(self):
        assert "caps_alignment" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "factual_accuracy" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert "answer_key_correctness" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
        assert len(REQUIRED_APPROVAL_RUBRIC_CRITERIA) == 10

    def test_review_decision_result(self):
        did = uuid.uuid4()
        aid = uuid.uuid4()
        res = ReviewDecisionResult(
            decision_id=did,
            artifact_id=aid,
            artifact_version=1,
            action="approve",
            previous_status="pending_review",
            current_status="approved",
            approval_count=3,
            quorum_threshold=3,
            quorum_reached=True,
        )
        assert res.decision_id == did
        assert res.quorum_reached is True

    def test_review_assignment_result(self):
        aid = uuid.uuid4()
        asid = uuid.uuid4()
        res = ReviewAssignmentResult(
            assignment_ids=[asid],
            artifact_id=aid,
            artifact_version=1,
            assigned_count=1,
        )
        assert res.assigned_count == 1

    def test_artifact_revision_result(self):
        p_id = uuid.uuid4()
        n_id = uuid.uuid4()
        res = ArtifactRevisionResult(
            previous_artifact_id=p_id,
            new_artifact_id=n_id,
            version_number=2,
            status="draft",
        )
        assert res.version_number == 2
