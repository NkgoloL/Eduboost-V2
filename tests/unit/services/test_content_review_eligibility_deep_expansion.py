import uuid
import pytest
from unittest.mock import MagicMock

from app.models.content_factory import ContentGenerationArtifact, ContentArtifactStatus
from app.services.content_review_governance import (
    REQUIRED_APPROVAL_RUBRIC_CRITERIA,
    ReviewGovernancePolicy,
    ContentReviewEligibilityService,
)


def test_rubric_criteria_and_policy():
    assert "caps_alignment" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
    assert "factual_accuracy" in REQUIRED_APPROVAL_RUBRIC_CRITERIA
    assert len(REQUIRED_APPROVAL_RUBRIC_CRITERIA) == 10

    policy = ReviewGovernancePolicy.from_environment()
    assert policy.quorum_threshold >= 2
    assert policy.stale_after_hours >= 1


def test_eligibility_service():
    artifact = MagicMock(spec=ContentGenerationArtifact)
    artifact.status = ContentArtifactStatus.PROMOTED_PRODUCTION
    artifact.publication_eligible = True
    artifact.published_at = None

    assert ContentReviewEligibilityService.is_retrieval_eligible(artifact) is True
    assert ContentReviewEligibilityService.is_learner_eligible(artifact) is False

    with pytest.raises(ValueError, match="not eligible for learner delivery"):
        ContentReviewEligibilityService.assert_learner_eligible(artifact)
