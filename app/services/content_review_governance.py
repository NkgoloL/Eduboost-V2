"""Phase 3 educator consensus and content-governance services.

This module is the authoritative write boundary for educator review decisions.
Review decisions and state transitions are append-only. Artifact status is
changed only while holding a PostgreSQL row lock, so concurrent final reviews
cannot over-count approvals or publish conflicting state.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.metrics import (
    content_review_decisions_total,
    content_review_state_transitions_total,
)
from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAction,
    ContentReviewAssignment,
    ContentReviewDecision,
    ContentStateTransitionEvent,
)
from app.services.content_factory import ContentFactoryService, stable_json_hash


REQUIRED_APPROVAL_RUBRIC_CRITERIA = (
    "caps_alignment",
    "factual_accuracy",
    "answer_key_correctness",
    "grade_suitability",
    "language_quality",
    "cultural_appropriateness",
    "bias_and_safety",
    "accessibility_and_clarity",
    "source_grounding",
    "personal_information",
)


@dataclass(frozen=True)
class ReviewGovernancePolicy:
    version: str = "phase3-v1"
    rubric_id: str = "educator-content-review"
    rubric_version: str = "1.0"
    quorum_threshold: int = 3
    stale_after_hours: int = 72
    creator_approval_counts: bool = False
    direct_publish_allowed: bool = False

    @classmethod
    def from_environment(cls) -> "ReviewGovernancePolicy":
        threshold = int(os.getenv("CONTENT_CONSENSUS_THRESHOLD", "3"))
        if threshold < 2 or threshold > 10:
            raise ValueError("CONTENT_CONSENSUS_THRESHOLD must be between 2 and 10.")
        stale_hours = int(os.getenv("CONTENT_CONSENSUS_TIMEOUT_HOURS", "72"))
        if stale_hours < 1:
            raise ValueError("CONTENT_CONSENSUS_TIMEOUT_HOURS must be positive.")
        return cls(
            version=os.getenv("CONTENT_REVIEW_POLICY_VERSION", "phase3-v1"),
            rubric_id=os.getenv("CONTENT_REVIEW_RUBRIC_ID", "educator-content-review"),
            rubric_version=os.getenv("CONTENT_REVIEW_RUBRIC_VERSION", "1.0"),
            quorum_threshold=threshold,
            stale_after_hours=stale_hours,
            creator_approval_counts=_env_bool("CONTENT_CREATOR_APPROVAL_COUNTS", False),
            direct_publish_allowed=_env_bool("CONTENT_DIRECT_PUBLISH_ALLOWED", False),
        )


@dataclass(frozen=True)
class ReviewDecisionResult:
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


@dataclass(frozen=True)
class ReviewAssignmentResult:
    assignment_ids: list[uuid.UUID]
    artifact_id: uuid.UUID
    artifact_version: int
    assigned_count: int


@dataclass(frozen=True)
class ArtifactRevisionResult:
    previous_artifact_id: uuid.UUID
    new_artifact_id: uuid.UUID
    version_number: int
    status: str


class ContentReviewEligibilityService:
    """Single eligibility policy shared by delivery, retrieval, and export paths."""

    RETRIEVAL_ELIGIBLE = frozenset(
        {
            ContentArtifactStatus.PROMOTED_PRODUCTION.value,
            ContentArtifactStatus.PUBLISHED.value,
        }
    )
    LEARNER_ELIGIBLE = frozenset({ContentArtifactStatus.PUBLISHED.value})

    @classmethod
    def is_retrieval_eligible(cls, artifact: ContentGenerationArtifact) -> bool:
        return _value(artifact.status) in cls.RETRIEVAL_ELIGIBLE and bool(
            artifact.publication_eligible
        )

    @classmethod
    def is_learner_eligible(cls, artifact: ContentGenerationArtifact) -> bool:
        return _value(artifact.status) in cls.LEARNER_ELIGIBLE and artifact.published_at is not None

    @classmethod
    def assert_retrieval_eligible(cls, artifact: ContentGenerationArtifact) -> None:
        if not cls.is_retrieval_eligible(artifact):
            raise ValueError("Artifact is not eligible for semantic retrieval or training export.")

    @classmethod
    def assert_learner_eligible(cls, artifact: ContentGenerationArtifact) -> None:
        if not cls.is_learner_eligible(artifact):
            raise ValueError("Artifact is not eligible for learner delivery.")


class ContentReviewGovernanceService:
    def __init__(
        self,
        *,
        policy: ReviewGovernancePolicy | None = None,
        factory_service: ContentFactoryService | None = None,
    ) -> None:
        self.policy = policy or ReviewGovernancePolicy.from_environment()
        self.factory_service = factory_service or ContentFactoryService()

    async def assign_reviewers(
        self,
        session: AsyncSession,
        *,
        artifact_id: uuid.UUID,
        reviewer_ids: list[str],
        assigned_by: str,
        reviewer_competencies: dict[str, list[str]] | None = None,
        due_by: datetime | None = None,
        priority: str = "normal",
        idempotency_key: str | None = None,
    ) -> ReviewAssignmentResult:
        artifact = await self._load_artifact_for_update(session, artifact_id)
        if _value(artifact.status) != ContentArtifactStatus.PENDING_REVIEW.value:
            raise ValueError("Reviewers can only be assigned to pending_review artifacts.")
        unique_reviewers = list(dict.fromkeys(value.strip() for value in reviewer_ids if value.strip()))
        if len(unique_reviewers) < self.policy.quorum_threshold:
            raise ValueError(
                f"At least {self.policy.quorum_threshold} distinct reviewers must be assigned."
            )
        if not self.policy.creator_approval_counts and artifact.created_by_actor_id in unique_reviewers:
            raise ValueError("The artifact creator cannot be assigned as a counting reviewer.")

        result_ids: list[uuid.UUID] = []
        competencies = reviewer_competencies or {}
        for reviewer_id in unique_reviewers:
            existing = await session.scalar(
                select(ContentReviewAssignment).where(
                    ContentReviewAssignment.artifact_id == artifact.artifact_id,
                    ContentReviewAssignment.artifact_version == artifact.version_number,
                    ContentReviewAssignment.assigned_to == reviewer_id,
                )
            )
            if existing is not None:
                result_ids.append(existing.id)
                continue
            assignment = ContentReviewAssignment(
                artifact_id=artifact.artifact_id,
                artifact_version=int(getattr(artifact, "version_number", 1) or 1),
                assigned_to=reviewer_id,
                assigned_by=assigned_by,
                priority=priority,
                due_by=due_by,
                status="assigned",
                reviewer_competencies=list(competencies.get(reviewer_id) or []),
                policy_version=self.policy.version,
                idempotency_key=(
                    f"{idempotency_key}:{reviewer_id}" if idempotency_key else None
                ),
            )
            session.add(assignment)
            await session.flush()
            result_ids.append(assignment.id)
        return ReviewAssignmentResult(
            assignment_ids=result_ids,
            artifact_id=artifact.artifact_id,
            artifact_version=int(getattr(artifact, "version_number", 1) or 1),
            assigned_count=len(result_ids),
        )

    async def accept_assignment(
        self,
        session: AsyncSession,
        *,
        assignment_id: uuid.UUID,
        reviewer_id: str,
        conflict_of_interest: bool,
    ) -> ContentReviewAssignment:
        assignment = await session.scalar(
            select(ContentReviewAssignment)
            .where(ContentReviewAssignment.id == assignment_id)
            .with_for_update()
        )
        if assignment is None:
            raise LookupError(f"Review assignment {assignment_id} not found.")
        if assignment.assigned_to != reviewer_id:
            raise PermissionError("Review assignments may only be accepted by the assigned reviewer.")
        if assignment.status not in {"assigned", "in_review"}:
            raise ValueError("Only open review assignments may be accepted.")
        assignment.conflict_of_interest = bool(conflict_of_interest)
        assignment.accepted_at = datetime.now(timezone.utc)
        assignment.status = "conflict" if conflict_of_interest else "in_review"
        await session.flush()
        return assignment

    async def submit_decision(
        self,
        session: AsyncSession,
        *,
        artifact_id: uuid.UUID,
        reviewer_id: str,
        action: ContentReviewAction | str,
        rubric_results: dict[str, Any],
        idempotency_key: str,
        expected_version: int,
        reason_code: str | None = None,
        comments: str | None = None,
        reviewer_competencies: list[str] | None = None,
        conflict_of_interest: bool = False,
        correlation_id: str | None = None,
    ) -> ReviewDecisionResult:
        action = ContentReviewAction(action)
        if not idempotency_key.strip():
            raise ValueError("Review decisions require an idempotency key.")

        replay = await session.scalar(
            select(ContentReviewDecision).where(
                ContentReviewDecision.reviewer_id == reviewer_id,
                ContentReviewDecision.idempotency_key == idempotency_key,
            )
        )
        if replay is not None:
            if replay.artifact_id != artifact_id or replay.artifact_version != expected_version:
                raise ValueError("Idempotency key was already used for a different decision.")
            artifact = await self._load_artifact(session, artifact_id)
            return self._decision_result(replay, artifact, idempotent_replay=True)

        artifact = await self._load_artifact_for_update(session, artifact_id)
        previous_status = _value(artifact.status)
        if artifact.version_number != expected_version:
            raise ReviewConflictError(
                f"Artifact version changed: expected {expected_version}, current {artifact.version_number}."
            )
        if previous_status != ContentArtifactStatus.PENDING_REVIEW.value:
            raise ReviewConflictError("Decisions may only be submitted for pending_review artifacts.")
        if not self.policy.creator_approval_counts and artifact.created_by_actor_id == reviewer_id:
            raise PermissionError("Artifact creators cannot review their own content.")

        assignment = await session.scalar(
            select(ContentReviewAssignment)
            .where(
                ContentReviewAssignment.artifact_id == artifact.artifact_id,
                ContentReviewAssignment.artifact_version == artifact.version_number,
                ContentReviewAssignment.assigned_to == reviewer_id,
            )
            .with_for_update()
        )
        if assignment is None:
            raise PermissionError("Reviewer is not assigned to this artifact version.")
        if assignment.status == "conflict" or assignment.conflict_of_interest or conflict_of_interest:
            raise PermissionError("A conflicted reviewer cannot submit a content decision.")
        if assignment.status in {"approved", "resolved"}:
            raise ReviewConflictError("Reviewer already submitted a decision for this artifact version.")
        if assignment.status not in {"assigned", "in_review"}:
            raise ReviewConflictError("Review assignment is not open.")

        competencies = list(
            reviewer_competencies
            if reviewer_competencies is not None
            else assignment.reviewer_competencies or []
        )
        self._validate_decision_input(
            action=action,
            rubric_results=rubric_results,
            reason_code=reason_code,
        )
        decision = ContentReviewDecision(
            artifact_id=artifact.artifact_id,
            artifact_version=int(getattr(artifact, "version_number", 1) or 1),
            reviewer_id=reviewer_id,
            review_action=action,
            reason_code=reason_code,
            comments=comments,
            rubric_id=self.policy.rubric_id,
            rubric_version=self.policy.rubric_version,
            rubric_results=rubric_results,
            policy_version=self.policy.version,
            idempotency_key=idempotency_key,
            conflict_of_interest=False,
            reviewer_competencies=competencies,
            correlation_id=correlation_id,
        )
        session.add(decision)
        try:
            await session.flush()
        except IntegrityError as exc:
            raise ReviewConflictError(
                "Reviewer already submitted a decision for this artifact version."
            ) from exc

        content_review_decisions_total.labels(action=_value(action), result="accepted").inc()
        assignment.status = "approved" if action is ContentReviewAction.APPROVE else "resolved"
        assignment.resolved_at = datetime.now(timezone.utc)
        assignment.completed_at = assignment.resolved_at

        new_status = previous_status
        if action is ContentReviewAction.REJECT:
            new_status = ContentArtifactStatus.REJECTED.value
        elif action is ContentReviewAction.QUARANTINE:
            new_status = ContentArtifactStatus.QUARANTINED.value
        elif action is ContentReviewAction.REQUEST_CHANGES:
            new_status = ContentArtifactStatus.REVISION_REQUIRED.value
        elif action is ContentReviewAction.APPROVE:
            await self.factory_service.assert_artifact_has_approved_sources(
                session, artifact.artifact_id
            )
            approvals = await self._valid_approvals(session, artifact)
            artifact.approval_count = len(approvals)
            if artifact.approval_count >= self.policy.quorum_threshold:
                self._assert_approval_competencies(artifact, approvals)
                new_status = ContentArtifactStatus.APPROVED.value
                artifact.approved_at = datetime.now(timezone.utc)
                artifact.publication_eligible = True
                if _value(artifact.artifact_type) == "diagnostic_item":
                    artifact.answer_key_verified = True

        if new_status != previous_status:
            artifact.status = ContentArtifactStatus(new_status)
            artifact.row_version += 1
            await self._record_transition(
                session,
                artifact=artifact,
                previous_status=previous_status,
                new_status=new_status,
                actor_id=reviewer_id,
                reason_code=reason_code,
                reason=comments,
                triggering_decision_id=decision.decision_id,
                correlation_id=correlation_id,
            )
        await session.flush()
        return self._decision_result(decision, artifact)

    async def quarantine_artifact(
        self,
        session: AsyncSession,
        *,
        artifact_id: uuid.UUID,
        actor_id: str,
        reason_code: str,
        reason: str,
        correlation_id: str | None = None,
    ) -> ContentGenerationArtifact:
        if not reason_code or not reason.strip():
            raise ValueError("Quarantine requires a reason code and explanation.")
        artifact = await self._load_artifact_for_update(session, artifact_id)
        previous = _value(artifact.status)
        if previous == ContentArtifactStatus.SUPERSEDED.value:
            raise ReviewConflictError("Superseded artifacts are already ineligible.")
        artifact.status = ContentArtifactStatus.QUARANTINED
        artifact.publication_eligible = False
        artifact.row_version += 1
        await self._record_transition(
            session,
            artifact=artifact,
            previous_status=previous,
            new_status=ContentArtifactStatus.QUARANTINED.value,
            actor_id=actor_id,
            reason_code=reason_code,
            reason=reason,
            correlation_id=correlation_id,
        )
        await session.flush()
        return artifact

    async def create_revision(
        self,
        session: AsyncSession,
        *,
        artifact_id: uuid.UUID,
        actor_id: str,
        artifact_json: dict[str, Any],
        reason: str,
        expected_version: int,
        correlation_id: str | None = None,
    ) -> ArtifactRevisionResult:
        if not artifact_json:
            raise ValueError("A revised artifact payload is required.")
        original = await self._load_artifact_for_update(session, artifact_id, include_sources=True)
        if original.version_number != expected_version:
            raise ReviewConflictError(
                f"Artifact version changed: expected {expected_version}, current {original.version_number}."
            )
        if _value(original.status) == ContentArtifactStatus.SUPERSEDED.value:
            raise ReviewConflictError("Superseded artifacts cannot be revised again.")
        revised_hash = stable_json_hash(artifact_json)
        if revised_hash == original.artifact_hash:
            raise ValueError("Material revisions must change the artifact content hash.")

        sources = [_source_payload(source) for source in original.sources]
        payload = {
            "scope_id": original.scope_id,
            "content_layer": original.content_layer,
            "artifact_type": original.artifact_type,
            "artifact_json": artifact_json,
            "caps_ref": original.caps_ref,
            "grade": original.grade,
            "subject_code": original.subject_code,
            "language": original.language,
            "schema_version": original.schema_version,
            "provider": original.provider,
            "model": original.model,
            "prompt_version": original.prompt_version,
            "token_usage": original.token_usage,
            "cost_metadata": original.cost_metadata,
            "quality_score": original.quality_score,
            "safety_status": original.safety_status,
            "answer_key_verified": False,
            "caps_alignment_score": original.caps_alignment_score,
            "sources": sources,
        }
        revised = await self.factory_service.create_artifact(session, payload=payload)
        revised.root_artifact_id = original.root_artifact_id or original.artifact_id
        revised.supersedes_artifact_id = original.artifact_id
        revised.version_number = original.version_number + 1
        revised.row_version = 1
        revised.created_by_actor_id = actor_id
        revised.approval_count = 0
        revised.review_policy_version = self.policy.version
        revised.rubric_version = self.policy.rubric_version
        revised.publication_eligible = False

        previous = _value(original.status)
        original.status = ContentArtifactStatus.SUPERSEDED
        original.superseded_by_artifact_id = revised.artifact_id
        original.publication_eligible = False
        original.row_version += 1
        await self._record_transition(
            session,
            artifact=original,
            previous_status=previous,
            new_status=ContentArtifactStatus.SUPERSEDED.value,
            actor_id=actor_id,
            reason_code="material_revision",
            reason=reason,
            correlation_id=correlation_id,
        )
        await self._record_transition(
            session,
            artifact=revised,
            previous_status=ContentArtifactStatus.GENERATED.value,
            new_status=_value(revised.status),
            actor_id=actor_id,
            reason_code="revision_created",
            reason=reason,
            correlation_id=correlation_id,
        )
        await session.flush()
        return ArtifactRevisionResult(
            previous_artifact_id=original.artifact_id,
            new_artifact_id=revised.artifact_id,
            version_number=revised.version_number,
            status=_value(revised.status),
        )

    async def publish_artifact(
        self,
        session: AsyncSession,
        *,
        artifact_id: uuid.UUID,
        actor_id: str,
        expected_version: int,
        reason: str,
        correlation_id: str | None = None,
    ) -> ContentGenerationArtifact:
        artifact = await self._load_artifact_for_update(session, artifact_id)
        if artifact.version_number != expected_version:
            raise ReviewConflictError("Artifact version changed before publication.")
        current = _value(artifact.status)
        allowed = {ContentArtifactStatus.PROMOTED_PRODUCTION.value}
        if self.policy.direct_publish_allowed:
            allowed.add(ContentArtifactStatus.APPROVED.value)
        if current not in allowed:
            raise ReviewConflictError(
                "Publication requires promoted_production status; direct publication is disabled."
            )
        if not artifact.publication_eligible:
            raise ReviewConflictError("Artifact is not publication eligible.")
        if artifact.approval_count < self.policy.quorum_threshold:
            raise ReviewConflictError("Publication requires the configured educator quorum.")
        blocking_count = await session.scalar(
            select(func.count(ContentReviewDecision.decision_id)).where(
                ContentReviewDecision.artifact_id == artifact.artifact_id,
                ContentReviewDecision.artifact_version == artifact.version_number,
                ContentReviewDecision.review_action.in_(
                    [
                        ContentReviewAction.REJECT,
                        ContentReviewAction.QUARANTINE,
                        ContentReviewAction.REQUEST_CHANGES,
                    ]
                ),
            )
        )
        if int(blocking_count or 0):
            raise ReviewConflictError("Publication is blocked by a review decision.")
        await self.factory_service.assert_artifact_has_approved_sources(
            session, artifact.artifact_id
        )
        artifact.status = ContentArtifactStatus.PUBLISHED
        artifact.published_at = datetime.now(timezone.utc)
        artifact.row_version += 1
        await self._record_transition(
            session,
            artifact=artifact,
            previous_status=current,
            new_status=ContentArtifactStatus.PUBLISHED.value,
            actor_id=actor_id,
            reason_code="publication_approved",
            reason=reason,
            correlation_id=correlation_id,
        )
        await session.flush()
        return artifact

    async def reassign_assignment(
        self,
        session: AsyncSession,
        *,
        assignment_id: uuid.UUID,
        new_reviewer_id: str,
        assigned_by: str,
        reviewer_competencies: list[str] | None = None,
        due_by: datetime | None = None,
        reason: str,
        idempotency_key: str | None = None,
    ) -> ContentReviewAssignment:
        if not reason.strip():
            raise ValueError("Reassignment requires a reason.")
        original = await session.scalar(
            select(ContentReviewAssignment)
            .where(ContentReviewAssignment.id == assignment_id)
            .with_for_update()
        )
        if original is None:
            raise LookupError(f"Review assignment {assignment_id} not found.")
        if original.status not in {"assigned", "in_review"}:
            raise ReviewConflictError("Only active assignments can be reassigned.")
        if new_reviewer_id == original.assigned_to:
            raise ValueError("The replacement reviewer must be different.")
        artifact = await self._load_artifact_for_update(session, original.artifact_id)
        if artifact.version_number != original.artifact_version:
            raise ReviewConflictError("Assignment belongs to a stale artifact version.")
        if not self.policy.creator_approval_counts and new_reviewer_id == artifact.created_by_actor_id:
            raise ValueError("The artifact creator cannot be assigned as a counting reviewer.")
        existing = await session.scalar(
            select(ContentReviewAssignment).where(
                ContentReviewAssignment.artifact_id == original.artifact_id,
                ContentReviewAssignment.artifact_version == original.artifact_version,
                ContentReviewAssignment.assigned_to == new_reviewer_id,
            )
        )
        if existing is not None:
            raise ReviewConflictError("The replacement reviewer is already assigned.")
        current = datetime.now(timezone.utc)
        original.status = "reassigned"
        original.completed_at = current
        original.resolved_at = current
        replacement = ContentReviewAssignment(
            artifact_id=original.artifact_id,
            artifact_version=original.artifact_version,
            assigned_to=new_reviewer_id,
            assigned_by=assigned_by,
            assigned_at=current,
            due_by=due_by,
            priority=original.priority,
            status="assigned",
            reviewer_competencies=list(reviewer_competencies or []),
            policy_version=self.policy.version,
            idempotency_key=idempotency_key,
            reassigned_from_id=original.id,
        )
        session.add(replacement)
        await session.flush()
        return replacement

    async def process_stale_assignments(
        self,
        session: AsyncSession,
        *,
        now: datetime | None = None,
        limit: int = 500,
    ) -> dict[str, int]:
        current = now or datetime.now(timezone.utc)
        stale = await self.list_stale_assignments(session, now=current, limit=limit)
        reminded = 0
        escalated = 0
        hard_cutoff = current - timedelta(hours=self.policy.stale_after_hours * 2)
        for assignment in stale:
            assignment.reminder_count = int(assignment.reminder_count or 0) + 1
            assignment.last_reminded_at = current
            reminded += 1
            baseline = assignment.due_by or assignment.assigned_at
            if baseline <= hard_cutoff and assignment.escalated_at is None:
                assignment.escalated_at = current
                escalated += 1
        await session.flush()
        return {"stale": len(stale), "reminded": reminded, "escalated": escalated}

    async def list_history(
        self, session: AsyncSession, artifact_id: uuid.UUID
    ) -> dict[str, list[Any]]:
        decisions = list(
            (
                await session.scalars(
                    select(ContentReviewDecision)
                    .where(ContentReviewDecision.artifact_id == artifact_id)
                    .order_by(ContentReviewDecision.created_at, ContentReviewDecision.decision_id)
                )
            ).all()
        )
        transitions = list(
            (
                await session.scalars(
                    select(ContentStateTransitionEvent)
                    .where(ContentStateTransitionEvent.artifact_id == artifact_id)
                    .order_by(
                        ContentStateTransitionEvent.created_at,
                        ContentStateTransitionEvent.event_id,
                    )
                )
            ).all()
        )
        return {"decisions": decisions, "transitions": transitions}

    async def list_stale_assignments(
        self,
        session: AsyncSession,
        *,
        now: datetime | None = None,
        limit: int = 200,
    ) -> list[ContentReviewAssignment]:
        current = now or datetime.now(timezone.utc)
        default_cutoff = current - timedelta(hours=self.policy.stale_after_hours)
        result = await session.scalars(
            select(ContentReviewAssignment)
            .where(
                ContentReviewAssignment.status.in_(["assigned", "in_review"]),
                (
                    (ContentReviewAssignment.due_by.is_not(None) & (ContentReviewAssignment.due_by <= current))
                    | (ContentReviewAssignment.due_by.is_(None) & (ContentReviewAssignment.assigned_at <= default_cutoff))
                ),
            )
            .order_by(ContentReviewAssignment.due_by, ContentReviewAssignment.assigned_at)
            .limit(limit)
        )
        return list(result.all())

    async def record_external_transition(
        self,
        session: AsyncSession,
        *,
        artifact: ContentGenerationArtifact,
        previous_status: str,
        new_status: str,
        actor_id: str,
        reason_code: str | None = None,
        reason: str | None = None,
        correlation_id: str | None = None,
    ) -> ContentStateTransitionEvent:
        return await self._record_transition(
            session,
            artifact=artifact,
            previous_status=previous_status,
            new_status=new_status,
            actor_id=actor_id,
            reason_code=reason_code,
            reason=reason,
            correlation_id=correlation_id,
        )

    async def _valid_approvals(
        self,
        session: AsyncSession,
        artifact: ContentGenerationArtifact,
    ) -> list[ContentReviewDecision]:
        result = await session.scalars(
            select(ContentReviewDecision).where(
                ContentReviewDecision.artifact_id == artifact.artifact_id,
                ContentReviewDecision.artifact_version == artifact.version_number,
                ContentReviewDecision.review_action == ContentReviewAction.APPROVE,
                ContentReviewDecision.conflict_of_interest.is_(False),
            )
        )
        approvals = list(result.all())
        if not self.policy.creator_approval_counts and artifact.created_by_actor_id:
            approvals = [
                decision
                for decision in approvals
                if decision.reviewer_id != artifact.created_by_actor_id
            ]
        return approvals

    def _assert_approval_competencies(
        self,
        artifact: ContentGenerationArtifact,
        approvals: Iterable[ContentReviewDecision],
    ) -> None:
        competencies = {
            competency.lower()
            for approval in approvals
            for competency in (approval.reviewer_competencies or [])
        }
        if not ({"subject", "caps", "curriculum"} & competencies):
            raise ValueError("Quorum requires at least one subject/CAPS-competent reviewer.")
        language = (artifact.language or "en").lower()
        if language != "en" and not (
            "language" in competencies or f"language:{language}" in competencies
        ):
            raise ValueError(
                f"Quorum for {language} content requires a language-competent reviewer."
            )

    def _validate_decision_input(
        self,
        *,
        action: ContentReviewAction,
        rubric_results: dict[str, Any],
        reason_code: str | None,
    ) -> None:
        if action is ContentReviewAction.APPROVE:
            missing = [
                criterion
                for criterion in REQUIRED_APPROVAL_RUBRIC_CRITERIA
                if criterion not in rubric_results
            ]
            if missing:
                raise ValueError(
                    "Approval rubric is incomplete: " + ", ".join(missing)
                )
            failed = [
                criterion
                for criterion in REQUIRED_APPROVAL_RUBRIC_CRITERIA
                if not _rubric_passed(rubric_results[criterion])
            ]
            if failed:
                raise ValueError(
                    "Approval is blocked by rubric failures: " + ", ".join(failed)
                )
        elif not reason_code:
            raise ValueError(f"{action.value} decisions require a reason code.")

    async def _record_transition(
        self,
        session: AsyncSession,
        *,
        artifact: ContentGenerationArtifact,
        previous_status: str,
        new_status: str,
        actor_id: str,
        reason_code: str | None = None,
        reason: str | None = None,
        triggering_decision_id: uuid.UUID | None = None,
        correlation_id: str | None = None,
    ) -> ContentStateTransitionEvent:
        event = ContentStateTransitionEvent(
            artifact_id=artifact.artifact_id,
            artifact_version=int(getattr(artifact, "version_number", 1) or 1),
            previous_status=previous_status,
            new_status=new_status,
            actor_id=actor_id,
            reason_code=reason_code,
            reason=reason,
            triggering_decision_id=triggering_decision_id,
            policy_version=self.policy.version,
            correlation_id=correlation_id,
        )
        session.add(event)
        await session.flush()
        content_review_state_transitions_total.labels(
            from_status=previous_status, to_status=new_status
        ).inc()
        return event

    async def _load_artifact(
        self,
        session: AsyncSession,
        artifact_id: uuid.UUID,
        *,
        include_sources: bool = False,
    ) -> ContentGenerationArtifact:
        stmt = select(ContentGenerationArtifact).where(
            ContentGenerationArtifact.artifact_id == artifact_id
        )
        if include_sources:
            stmt = stmt.options(selectinload(ContentGenerationArtifact.sources))
        artifact = await session.scalar(stmt)
        if artifact is None:
            raise LookupError(f"Artifact {artifact_id} not found.")
        return artifact

    async def _load_artifact_for_update(
        self,
        session: AsyncSession,
        artifact_id: uuid.UUID,
        *,
        include_sources: bool = False,
    ) -> ContentGenerationArtifact:
        stmt = (
            select(ContentGenerationArtifact)
            .where(ContentGenerationArtifact.artifact_id == artifact_id)
            .with_for_update()
        )
        if include_sources:
            stmt = stmt.options(selectinload(ContentGenerationArtifact.sources))
        artifact = await session.scalar(stmt)
        if artifact is None:
            raise LookupError(f"Artifact {artifact_id} not found.")
        return artifact

    def _decision_result(
        self,
        decision: ContentReviewDecision,
        artifact: ContentGenerationArtifact,
        *,
        idempotent_replay: bool = False,
    ) -> ReviewDecisionResult:
        current = _value(artifact.status)
        return ReviewDecisionResult(
            decision_id=decision.decision_id,
            artifact_id=artifact.artifact_id,
            artifact_version=int(getattr(artifact, "version_number", 1) or 1),
            action=_value(decision.review_action),
            previous_status=(
                ContentArtifactStatus.PENDING_REVIEW.value
                if current == ContentArtifactStatus.APPROVED.value
                else current
            ),
            current_status=current,
            approval_count=int(artifact.approval_count or 0),
            quorum_threshold=self.policy.quorum_threshold,
            quorum_reached=current == ContentArtifactStatus.APPROVED.value,
            idempotent_replay=idempotent_replay,
        )


class ReviewConflictError(ValueError):
    """Raised when a decision conflicts with current artifact state/version."""


def _source_payload(source: ContentArtifactSource) -> dict[str, Any]:
    metadata = dict(source.source_metadata or {})
    return {
        "source_document_id": source.source_document_id,
        "source_chunk_id": source.source_chunk_id,
        "source_title": source.source_title,
        "source_type": source.source_type,
        "source_uri": source.source_uri,
        "citation_text": source.citation_text,
        "caps_ref": source.caps_ref,
        "grade": source.grade,
        "subject_code": source.subject_code,
        "language": source.language,
        "license_status": source.license_status,
        "source_quality_score": (
            float(source.source_quality_score)
            if source.source_quality_score is not None
            else None
        ),
        "etl_version": source.etl_version,
        "document_version_id": source.document_version_id,
        "chunk_hash": source.chunk_hash,
        "curriculum_mapping_id": source.curriculum_mapping_id,
        "source_hash": source.source_hash,
        "source_role": source.source_role,
        **metadata,
    }


def _rubric_passed(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, (int, float)):
        return value >= 0.8
    if isinstance(value, str):
        return value.strip().lower() in {"pass", "passed", "approved", "yes"}
    if isinstance(value, dict):
        return _rubric_passed(value.get("result") or value.get("passed"))
    return False


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}
