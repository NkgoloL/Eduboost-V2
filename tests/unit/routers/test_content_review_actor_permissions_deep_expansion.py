"""Comprehensive unit tests for content review actor permissions enforcement and request models."""
from __future__ import annotations

import uuid
import pytest
from fastapi import HTTPException

from app.api_v2_routers.content_review import ReviewActor
from app.models.content_factory import ContentReviewAction
from app.domain.content_review_schemas import (
    ReviewDecisionRequest,
    ArtifactRevisionRequest,
    QuarantineRequest,
)


class TestReviewActorPermissions:
    def test_require_permission_granted(self):
        actor = ReviewActor(
            user_id="teacher_1",
            permissions=frozenset({"review", "history_read"}),
            competencies=("grade4_mathematics",),
        )
        # Should not raise
        actor.require("review")
        actor.require("history_read")

    def test_require_permission_denied_raises_403(self):
        actor = ReviewActor(
            user_id="teacher_2",
            permissions=frozenset({"review"}),
            competencies=("grade4_mathematics",),
        )
        with pytest.raises(HTTPException) as exc_info:
            actor.require("quarantine")
        assert exc_info.value.status_code == 403
        assert "quarantine" in str(exc_info.value.detail)


class TestContentReviewRequestModels:
    def test_review_decision_request(self):
        req = ReviewDecisionRequest(
            action=ContentReviewAction.APPROVE,
            expected_version=1,
            idempotency_key="idemp_key_12345",
            rubric_results={"factual_accuracy": 5, "caps_alignment": 5},
            comments="Excellent alignment with Grade 4 CAPS requirements",
        )
        assert req.action == ContentReviewAction.APPROVE
        assert req.expected_version == 1
        assert req.rubric_results["caps_alignment"] == 5

    def test_quarantine_request(self):
        req = QuarantineRequest(
            reason_code="math_error",
            reason="Unverified mathematical claim in stem",
        )
        assert req.reason_code == "math_error"
        assert req.reason == "Unverified mathematical claim in stem"

    def test_artifact_revision_request(self):
        req = ArtifactRevisionRequest(
            expected_version=1,
            artifact_json={"question": "2+2"},
            reason="Please rephrase question 2 for clarity",
        )
        assert req.expected_version == 1
        assert req.reason == "Please rephrase question 2 for clarity"
