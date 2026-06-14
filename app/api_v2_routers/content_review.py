"""Phase 3 educator consensus and content-governance API."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.database import get_db
from app.core.metrics import content_review_authorization_failures_total
from app.core.envelope_route import EnvelopedRoute
from app.domain.content_review_schemas import (
    ArtifactGovernanceStatusResponse,
    ArtifactPublishRequest,
    ArtifactReviewHistoryResponse,
    ArtifactRevisionRequest,
    ArtifactRevisionResponse,
    QuarantineRequest,
    ReviewAssignmentAcceptRequest,
    ReviewAssignmentCreateRequest,
    ReviewAssignmentItemResponse,
    ReviewAssignmentReassignRequest,
    ReviewAssignmentGovernanceResponse,
    ReviewDecisionHistoryItem,
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    StaleReviewAssignmentResponse,
    StateTransitionHistoryItem,
)
from app.models.content_factory import ContentGenerationArtifact
from app.services.content_review_governance import (
    ContentReviewGovernanceService,
    ReviewConflictError,
)


router = APIRouter(
    route_class=EnvelopedRoute,
    prefix="/content-review",
    tags=["content-review-governance"],
)


@dataclass(frozen=True)
class ReviewActor:
    user_id: str
    permissions: frozenset[str]
    competencies: tuple[str, ...]

    def require(self, permission: str) -> None:
        if permission not in self.permissions:
            content_review_authorization_failures_total.labels(permission=permission).inc()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Content review permission {permission!r} is required.",
            )


async def get_review_actor(
    current_user: AuthContext = Depends(require_auth_context),
) -> ReviewActor:
    raw_permissions = current_user.raw_claims.get("review_permissions") or []
    if isinstance(raw_permissions, str):
        raw_permissions = [raw_permissions]
    permissions = {str(value) for value in raw_permissions}
    raw_role = str(current_user.raw_claims.get("content_review_role") or "").lower()

    if current_user.is_teacher:
        permissions.update({"review", "history_read", "assignment_accept"})
    if current_user.is_admin:
        permissions.update(
            {
                "assign",
                "quarantine",
                "revise",
                "history_read",
                "stale_read",
            }
        )
    if raw_role in {"reviewer", "senior_reviewer", "curriculum_lead"}:
        permissions.update({"review", "history_read", "assignment_accept"})
    if raw_role in {"senior_reviewer", "curriculum_lead"}:
        permissions.update({"assign", "quarantine", "revise", "stale_read"})
    if raw_role == "curriculum_lead":
        permissions.add("publish")

    if not permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The authenticated actor has no content-review permissions.",
        )
    raw_competencies = current_user.raw_claims.get("reviewer_competencies") or []
    if isinstance(raw_competencies, str):
        raw_competencies = [raw_competencies]
    return ReviewActor(
        user_id=current_user.user_id,
        permissions=frozenset(permissions),
        competencies=tuple(str(value) for value in raw_competencies),
    )


def get_governance_service() -> ContentReviewGovernanceService:
    return ContentReviewGovernanceService()


@router.post(
    "/artifacts/{artifact_id}/assignments",
    response_model=ReviewAssignmentGovernanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_reviewers(
    artifact_id: uuid.UUID,
    request: ReviewAssignmentCreateRequest,
    session: AsyncSession = Depends(get_db),
    actor: ReviewActor = Depends(get_review_actor),
    service: ContentReviewGovernanceService = Depends(get_governance_service),
) -> ReviewAssignmentGovernanceResponse:
    actor.require("assign")
    try:
        result = await service.assign_reviewers(
            session,
            artifact_id=artifact_id,
            reviewer_ids=request.reviewer_ids,
            assigned_by=actor.user_id,
            reviewer_competencies=request.reviewer_competencies,
            due_by=request.due_by,
            priority=request.priority,
            idempotency_key=request.idempotency_key,
        )
        await session.commit()
        return ReviewAssignmentGovernanceResponse(**result.__dict__)
    except (LookupError, ValueError) as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/assignments/{assignment_id}/accept",
    response_model=ArtifactGovernanceStatusResponse,
)
async def accept_assignment(
    assignment_id: uuid.UUID,
    request: ReviewAssignmentAcceptRequest,
    session: AsyncSession = Depends(get_db),
    actor: ReviewActor = Depends(get_review_actor),
    service: ContentReviewGovernanceService = Depends(get_governance_service),
) -> ArtifactGovernanceStatusResponse:
    actor.require("assignment_accept")
    try:
        assignment = await service.accept_assignment(
            session,
            assignment_id=assignment_id,
            reviewer_id=actor.user_id,
            conflict_of_interest=request.conflict_of_interest,
        )
        artifact = await session.get(ContentGenerationArtifact, assignment.artifact_id)
        await session.commit()
        assert artifact is not None
        return _artifact_status(artifact)
    except LookupError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/assignments/{assignment_id}/reassign",
    response_model=ReviewAssignmentItemResponse,
)
async def reassign_review(
    assignment_id: uuid.UUID,
    request: ReviewAssignmentReassignRequest,
    session: AsyncSession = Depends(get_db),
    actor: ReviewActor = Depends(get_review_actor),
    service: ContentReviewGovernanceService = Depends(get_governance_service),
) -> ReviewAssignmentItemResponse:
    actor.require("assign")
    try:
        assignment = await service.reassign_assignment(
            session,
            assignment_id=assignment_id,
            new_reviewer_id=request.new_reviewer_id,
            assigned_by=actor.user_id,
            reviewer_competencies=request.reviewer_competencies,
            due_by=request.due_by,
            reason=request.reason,
            idempotency_key=request.idempotency_key,
        )
        await session.commit()
        return _assignment_item(assignment)
    except LookupError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ValueError, ReviewConflictError) as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/artifacts/{artifact_id}/decisions",
    response_model=ReviewDecisionResponse,
)
async def submit_review_decision(
    artifact_id: uuid.UUID,
    request: ReviewDecisionRequest,
    session: AsyncSession = Depends(get_db),
    actor: ReviewActor = Depends(get_review_actor),
    service: ContentReviewGovernanceService = Depends(get_governance_service),
    ) -> ReviewDecisionResponse:
    actor.require("review")
    try:
        result = await service.submit_decision(
            session,
            artifact_id=artifact_id,
            reviewer_id=actor.user_id,
            action=request.action,
            rubric_results=request.rubric_results,
            idempotency_key=request.idempotency_key,
            expected_version=request.expected_version,
            reason_code=request.reason_code,
            comments=request.comments,
            reviewer_competencies=list(actor.competencies),
            conflict_of_interest=request.conflict_of_interest,
            correlation_id=request.correlation_id,
        )
        await session.commit()
        return ReviewDecisionResponse(**result.__dict__)
    except LookupError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except (ValueError, ReviewConflictError) as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/artifacts/{artifact_id}/quarantine",
    response_model=ArtifactGovernanceStatusResponse,
)
async def quarantine_artifact(
    artifact_id: uuid.UUID,
    request: QuarantineRequest,
    session: AsyncSession = Depends(get_db),
    actor: ReviewActor = Depends(get_review_actor),
    service: ContentReviewGovernanceService = Depends(get_governance_service),
) -> ArtifactGovernanceStatusResponse:
    actor.require("quarantine")
    try:
        artifact = await service.quarantine_artifact(
            session,
            artifact_id=artifact_id,
            actor_id=actor.user_id,
            reason_code=request.reason_code,
            reason=request.reason,
            correlation_id=request.correlation_id,
        )
        await session.commit()
        return _artifact_status(artifact)
    except LookupError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ValueError, ReviewConflictError) as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/artifacts/{artifact_id}/revisions",
    response_model=ArtifactRevisionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_artifact_revision(
    artifact_id: uuid.UUID,
    request: ArtifactRevisionRequest,
    session: AsyncSession = Depends(get_db),
    actor: ReviewActor = Depends(get_review_actor),
    service: ContentReviewGovernanceService = Depends(get_governance_service),
) -> ArtifactRevisionResponse:
    actor.require("revise")
    try:
        result = await service.create_revision(
            session,
            artifact_id=artifact_id,
            actor_id=actor.user_id,
            artifact_json=request.artifact_json,
            reason=request.reason,
            expected_version=request.expected_version,
            correlation_id=request.correlation_id,
        )
        await session.commit()
        return ArtifactRevisionResponse(**result.__dict__)
    except LookupError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ValueError, ReviewConflictError) as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/artifacts/{artifact_id}/publish",
    response_model=ArtifactGovernanceStatusResponse,
)
async def publish_artifact(
    artifact_id: uuid.UUID,
    request: ArtifactPublishRequest,
    session: AsyncSession = Depends(get_db),
    actor: ReviewActor = Depends(get_review_actor),
    service: ContentReviewGovernanceService = Depends(get_governance_service),
) -> ArtifactGovernanceStatusResponse:
    actor.require("publish")
    try:
        artifact = await service.publish_artifact(
            session,
            artifact_id=artifact_id,
            actor_id=actor.user_id,
            expected_version=request.expected_version,
            reason=request.reason,
            correlation_id=request.correlation_id,
        )
        await session.commit()
        return _artifact_status(artifact)
    except LookupError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ValueError, ReviewConflictError) as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get(
    "/artifacts/{artifact_id}/history",
    response_model=ArtifactReviewHistoryResponse,
)
async def get_review_history(
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    actor: ReviewActor = Depends(get_review_actor),
    service: ContentReviewGovernanceService = Depends(get_governance_service),
) -> ArtifactReviewHistoryResponse:
    actor.require("history_read")
    history = await service.list_history(session, artifact_id)
    return ArtifactReviewHistoryResponse(
        decisions=[
            ReviewDecisionHistoryItem(
                decision_id=item.decision_id,
                artifact_id=item.artifact_id,
                artifact_version=item.artifact_version,
                reviewer_id=item.reviewer_id,
                action=_value(item.review_action),
                reason_code=item.reason_code,
                comments=item.comments,
                rubric_id=item.rubric_id,
                rubric_version=item.rubric_version,
                rubric_results=item.rubric_results or {},
                policy_version=item.policy_version,
                correlation_id=item.correlation_id,
                created_at=item.created_at,
            )
            for item in history["decisions"]
        ],
        transitions=[
            StateTransitionHistoryItem(
                event_id=item.event_id,
                artifact_id=item.artifact_id,
                artifact_version=item.artifact_version,
                previous_status=item.previous_status,
                new_status=item.new_status,
                actor_id=item.actor_id,
                reason_code=item.reason_code,
                reason=item.reason,
                policy_version=item.policy_version,
                correlation_id=item.correlation_id,
                created_at=item.created_at,
            )
            for item in history["transitions"]
        ],
    )


@router.get(
    "/assignments/stale",
    response_model=list[StaleReviewAssignmentResponse],
)
async def list_stale_assignments(
    limit: int = Query(default=200, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
    actor: ReviewActor = Depends(get_review_actor),
    service: ContentReviewGovernanceService = Depends(get_governance_service),
) -> list[StaleReviewAssignmentResponse]:
    actor.require("stale_read")
    assignments = await service.list_stale_assignments(session, limit=limit)
    return [
        StaleReviewAssignmentResponse(**_assignment_item(item).model_dump())
        for item in assignments
    ]


def _assignment_item(item: Any) -> ReviewAssignmentItemResponse:
    return ReviewAssignmentItemResponse(
        assignment_id=item.id,
        artifact_id=item.artifact_id,
        artifact_version=item.artifact_version,
        assigned_to=item.assigned_to,
        status=item.status,
        assigned_at=item.assigned_at,
        due_by=item.due_by,
        priority=item.priority,
        reminder_count=int(item.reminder_count or 0),
        last_reminded_at=item.last_reminded_at,
        escalated_at=item.escalated_at,
        reassigned_from_id=item.reassigned_from_id,
    )


def _artifact_status(artifact: ContentGenerationArtifact) -> ArtifactGovernanceStatusResponse:
    return ArtifactGovernanceStatusResponse(
        artifact_id=artifact.artifact_id,
        version_number=int(artifact.version_number or 1),
        status=_value(artifact.status),
        approval_count=int(artifact.approval_count or 0),
        publication_eligible=bool(artifact.publication_eligible),
        approved_at=artifact.approved_at,
        published_at=artifact.published_at,
    )


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)
