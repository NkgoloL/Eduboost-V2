"""Strict API schemas for Phase 3 educator consensus and content governance."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.content_factory import ContentReviewAction


class StrictReviewModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReviewAssignmentCreateRequest(StrictReviewModel):
    reviewer_ids: list[str] = Field(min_length=2, max_length=10)
    reviewer_competencies: dict[str, list[str]] = Field(default_factory=dict)
    due_by: datetime | None = None
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=120)

    @field_validator("reviewer_ids")
    @classmethod
    def distinct_reviewers(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values if value.strip()]
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("reviewer_ids must be distinct")
        return cleaned


class ReviewAssignmentAcceptRequest(StrictReviewModel):
    conflict_of_interest: bool = False


class ReviewAssignmentReassignRequest(StrictReviewModel):
    new_reviewer_id: str = Field(min_length=1, max_length=80)
    reviewer_competencies: list[str] = Field(default_factory=list, max_length=20)
    due_by: datetime | None = None
    reason: str = Field(min_length=3, max_length=4000)
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=160)


class ReviewAssignmentGovernanceResponse(StrictReviewModel):
    assignment_ids: list[uuid.UUID]
    artifact_id: uuid.UUID
    artifact_version: int
    assigned_count: int


class ReviewDecisionRequest(StrictReviewModel):
    action: ContentReviewAction
    expected_version: int = Field(ge=1)
    rubric_results: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=8, max_length=160)
    reason_code: str | None = Field(default=None, max_length=80)
    comments: str | None = Field(default=None, max_length=4000)
    conflict_of_interest: bool = False
    correlation_id: str | None = Field(default=None, max_length=120)


class ReviewDecisionResponse(StrictReviewModel):
    decision_id: uuid.UUID
    artifact_id: uuid.UUID
    artifact_version: int
    action: str
    previous_status: str
    current_status: str
    approval_count: int
    quorum_threshold: int
    quorum_reached: bool
    idempotent_replay: bool = False


class QuarantineRequest(StrictReviewModel):
    reason_code: str = Field(min_length=2, max_length=80)
    reason: str = Field(min_length=3, max_length=4000)
    correlation_id: str | None = Field(default=None, max_length=120)


class ArtifactRevisionRequest(StrictReviewModel):
    expected_version: int = Field(ge=1)
    artifact_json: dict[str, Any]
    reason: str = Field(min_length=3, max_length=4000)
    correlation_id: str | None = Field(default=None, max_length=120)


class ArtifactRevisionResponse(StrictReviewModel):
    previous_artifact_id: uuid.UUID
    new_artifact_id: uuid.UUID
    version_number: int
    status: str


class ArtifactPublishRequest(StrictReviewModel):
    expected_version: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=4000)
    correlation_id: str | None = Field(default=None, max_length=120)


class ArtifactGovernanceStatusResponse(StrictReviewModel):
    artifact_id: uuid.UUID
    version_number: int
    status: str
    approval_count: int
    publication_eligible: bool
    approved_at: datetime | None = None
    published_at: datetime | None = None


class ReviewDecisionHistoryItem(StrictReviewModel):
    decision_id: uuid.UUID
    artifact_id: uuid.UUID
    artifact_version: int
    reviewer_id: str
    action: str
    reason_code: str | None
    comments: str | None
    rubric_id: str
    rubric_version: str
    rubric_results: dict[str, Any]
    policy_version: str
    correlation_id: str | None
    created_at: datetime


class StateTransitionHistoryItem(StrictReviewModel):
    event_id: uuid.UUID
    artifact_id: uuid.UUID
    artifact_version: int
    previous_status: str
    new_status: str
    actor_id: str
    reason_code: str | None
    reason: str | None
    policy_version: str
    correlation_id: str | None
    created_at: datetime


class ArtifactReviewHistoryResponse(StrictReviewModel):
    decisions: list[ReviewDecisionHistoryItem]
    transitions: list[StateTransitionHistoryItem]


class ReviewAssignmentItemResponse(StrictReviewModel):
    assignment_id: uuid.UUID
    artifact_id: uuid.UUID
    artifact_version: int
    assigned_to: str
    status: str
    assigned_at: datetime
    due_by: datetime | None
    priority: str
    reminder_count: int = 0
    last_reminded_at: datetime | None = None
    escalated_at: datetime | None = None
    reassigned_from_id: uuid.UUID | None = None


class StaleReviewAssignmentResponse(ReviewAssignmentItemResponse):
    pass
