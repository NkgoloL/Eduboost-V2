"""Reviewer assignment workflow for Content Factory artifacts.

Assignments are version-scoped and reviewer-specific. Multiple reviewers may
be assigned to one artifact version, while database uniqueness prevents a
reviewer from receiving duplicate assignments for that same version.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import ContentGenerationArtifact, ContentReviewAssignment

OPEN_STATUSES = {"assigned", "in_review"}
RESOLVED_STATUSES = {"approved", "resolved", "cancelled", "expired", "conflict"}


@dataclass(frozen=True)
class ReviewerWorkload:
    reviewer_id: str
    assigned: int
    in_review: int
    overdue: int
    total_open: int


class ContentReviewerAssignmentService:
    async def assign_artifact(
        self,
        session: AsyncSession,
        artifact_id: str | uuid.UUID,
        reviewer_id: str,
        assigned_by: str,
        *,
        priority: str = "normal",
        due_by: datetime | None = None,
        competencies: list[str] | None = None,
        idempotency_key: str | None = None,
    ) -> ContentReviewAssignment:
        artifact = await session.get(
            ContentGenerationArtifact, uuid.UUID(str(artifact_id))
        )
        if artifact is None:
            raise LookupError(f"Artifact {artifact_id} not found.")
        existing = await self._reviewer_assignment(
            session,
            artifact.artifact_id,
            int(getattr(artifact, "version_number", 1) or 1),
            reviewer_id,
        )
        if existing is not None:
            if existing.status in RESOLVED_STATUSES:
                raise ValueError(
                    "Reviewer already completed or closed an assignment for this artifact version."
                )
            existing.assigned_by = assigned_by
            existing.priority = priority
            existing.due_by = due_by
            existing.reviewer_competencies = list(competencies or existing.reviewer_competencies or [])
            await session.flush()
            return existing
        assignment = ContentReviewAssignment(
            artifact_id=artifact.artifact_id,
            artifact_version=int(getattr(artifact, "version_number", 1) or 1),
            assigned_to=reviewer_id,
            assigned_by=assigned_by,
            priority=priority,
            due_by=due_by,
            status="assigned",
            reviewer_competencies=list(competencies or []),
            idempotency_key=idempotency_key,
        )
        session.add(assignment)
        await session.flush()
        return assignment

    async def assign_batch(
        self,
        session: AsyncSession,
        artifact_ids: list[str | uuid.UUID],
        reviewer_id: str,
        assigned_by: str,
        *,
        priority: str = "normal",
    ) -> list[ContentReviewAssignment]:
        assignments = []
        for artifact_id in artifact_ids:
            assignments.append(
                await self.assign_artifact(
                    session,
                    artifact_id,
                    reviewer_id,
                    assigned_by,
                    priority=priority,
                )
            )
        return assignments

    async def unassign_artifact(
        self,
        session: AsyncSession,
        artifact_id: str | uuid.UUID,
        actor_id: str,
        *,
        reviewer_id: str | None = None,
    ) -> ContentReviewAssignment:
        assignment = await self._open_assignment(
            session, uuid.UUID(str(artifact_id)), reviewer_id=reviewer_id
        )
        if assignment is None:
            raise LookupError(f"Open assignment for artifact {artifact_id} not found.")
        assignment.status = "cancelled"
        assignment.resolved_at = datetime.now(timezone.utc)
        assignment.completed_at = assignment.resolved_at
        await session.flush()
        return assignment

    async def get_reviewer_workload(
        self, session: AsyncSession, reviewer_id: str
    ) -> ReviewerWorkload:
        result = await session.execute(
            select(ContentReviewAssignment).where(
                ContentReviewAssignment.assigned_to == reviewer_id,
                ContentReviewAssignment.status.in_(list(OPEN_STATUSES)),
            )
        )
        assignments = list(result.scalars().all())
        now = datetime.now(timezone.utc)
        default_cutoff = now - timedelta(hours=72)
        return ReviewerWorkload(
            reviewer_id=reviewer_id,
            assigned=sum(1 for item in assignments if item.status == "assigned"),
            in_review=sum(1 for item in assignments if item.status == "in_review"),
            overdue=sum(
                1
                for item in assignments
                if (
                    item.due_by is not None
                    and item.due_by < now
                    or item.due_by is None
                    and getattr(item, "assigned_at", getattr(item, "created_at", now)) < default_cutoff
                )
            ),
            total_open=len(assignments),
        )

    async def list_assignments(
        self,
        session: AsyncSession,
        *,
        reviewer_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ContentReviewAssignment]:
        stmt = (
            select(ContentReviewAssignment)
            .order_by(ContentReviewAssignment.created_at.desc())
            .limit(limit)
        )
        if reviewer_id:
            stmt = stmt.where(ContentReviewAssignment.assigned_to == reviewer_id)
        if status:
            stmt = stmt.where(ContentReviewAssignment.status == status)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def _reviewer_assignment(
        self,
        session: AsyncSession,
        artifact_id: uuid.UUID,
        artifact_version: int,
        reviewer_id: str,
    ) -> ContentReviewAssignment | None:
        result = await session.execute(
            select(ContentReviewAssignment)
            .where(
                ContentReviewAssignment.artifact_id == artifact_id,
                ContentReviewAssignment.artifact_version == artifact_version,
                ContentReviewAssignment.assigned_to == reviewer_id,
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _open_assignment(
        self,
        session: AsyncSession,
        artifact_id: uuid.UUID,
        *,
        reviewer_id: str | None = None,
    ) -> ContentReviewAssignment | None:
        stmt = select(ContentReviewAssignment).where(
            ContentReviewAssignment.artifact_id == artifact_id,
            ContentReviewAssignment.status.in_(list(OPEN_STATUSES)),
        )
        if reviewer_id is not None:
            stmt = stmt.where(ContentReviewAssignment.assigned_to == reviewer_id)
        result = await session.execute(stmt.order_by(ContentReviewAssignment.created_at).limit(1))
        return result.scalar_one_or_none()
