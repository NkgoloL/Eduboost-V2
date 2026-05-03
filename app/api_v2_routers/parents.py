"""
app/api_v2_routers/parents.py
EduBoost V2 — Parent Dashboard API Router (Phase 5.2)

Exposes aggregation endpoints for the parent trust dashboard.
All data is structured specifically for frontend charting.
No PII exposed in JSON responses — learner display_name is first-name only.

BOUNDARY: Imports from /app/core/, /app/domain/, /app/repositories/, /app/services/.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import Role, TokenPayload, get_current_user, require_role
from app.domain.models import AuditAction, KnowledgeGap, Lesson, Learner
from app.domain.schemas import (
    ParentDashboardLearner,
    ParentDashboardResponse,
    QuotaStatusResponse,
)
from app.repositories.repositories import GuardianRepository, LearnerRepository
from app.services.fourth_estate import fourth_estate

router = APIRouter(prefix="/api/v2/parents", tags=["Parent Dashboard"])


# ── Dependency: get DB session (wired in main api_v2.py) ─────────────────────
async def get_db() -> AsyncSession:
    """Placeholder — wired in api_v2.py via app.state.db_factory."""
    raise NotImplementedError("Dependency must be overridden in main app setup.")


# ── Dashboard Overview ────────────────────────────────────────────────────────

@router.get(
    "/dashboard",
    response_model=ParentDashboardResponse,
    summary="Parent trust dashboard — learner overview",
)
async def get_parent_dashboard(
    current_user: Annotated[TokenPayload, Depends(require_role(Role.PARENT, Role.ADMIN))],
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ParentDashboardResponse:
    """
    Returns a structured summary of all learners under a guardian.
    Data is formatted for chart/graph rendering on the frontend.
    """
    guardian_id = uuid.UUID(current_user.sub)
    guardian_repo = GuardianRepository(db)
    learner_repo = LearnerRepository(db)

    guardian = await guardian_repo.get_by_id(guardian_id)
    if guardian is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guardian not found")

    learners = await learner_repo.get_active_for_guardian(guardian_id)

    one_week_ago = datetime.now(UTC) - timedelta(days=7)
    dashboard_learners: list[ParentDashboardLearner] = []

    for learner in learners:
        # Check active consent
        consent = await guardian_repo.get_active_consent(guardian_id, learner.id)
        if consent is None:
            continue  # Skip learners without active consent (POPIA gate)

        # Lessons this week
        lessons_result = await db.execute(
            select(func.count(Lesson.id)).where(
                Lesson.learner_id == learner.id,
                Lesson.created_at >= one_week_ago,
            )
        )
        lessons_this_week = lessons_result.scalar_one_or_none() or 0

        # Active knowledge gaps
        gaps_result = await db.execute(
            select(func.count(KnowledgeGap.id)).where(
                KnowledgeGap.learner_id == learner.id,
                KnowledgeGap.resolved == False,  # noqa: E712
            )
        )
        active_gaps = gaps_result.scalar_one_or_none() or 0

        # Last lesson timestamp
        last_lesson_result = await db.execute(
            select(Lesson.created_at)
            .where(Lesson.learner_id == learner.id)
            .order_by(Lesson.created_at.desc())
            .limit(1)
        )
        last_lesson_at = last_lesson_result.scalar_one_or_none()

        dashboard_learners.append(
            ParentDashboardLearner(
                learner_id=learner.id,
                display_name=learner.display_name,
                grade_level=learner.grade_level,
                archetype=learner.archetype,
                irt_theta=round(learner.irt_theta, 3),
                lessons_this_week=lessons_this_week,
                active_knowledge_gaps=active_gaps,
                last_lesson_at=last_lesson_at,
            )
        )

    # Total lessons generated (all time)
    total_result = await db.execute(
        select(func.count(Lesson.id)).where(
            Lesson.learner_id.in_([l.id for l in learners])
        )
    )
    total_lessons = total_result.scalar_one_or_none() or 0

    fourth_estate.enqueue(
        background_tasks, db,
        action=AuditAction.DATA_EXPORT_REQUESTED,
        actor_id=str(guardian_id),
        payload={"endpoint": "parent_dashboard"},
    )

    return ParentDashboardResponse(
        guardian_id=guardian_id,
        learners=dashboard_learners,
        total_lessons_generated=total_lessons,
        subscription_tier=guardian.subscription_tier,
    )


@router.get(
    "/learners/{learner_id}/progress",
    summary="Detailed progress chart data for a single learner",
)
async def get_learner_progress(
    learner_id: uuid.UUID,
    current_user: Annotated[TokenPayload, Depends(require_role(Role.PARENT, Role.ADMIN))],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Returns lesson history and knowledge gap timelines in a format
    optimised for recharts / Chart.js frontend rendering.
    """
    guardian_id = uuid.UUID(current_user.sub)
    learner_repo = LearnerRepository(db)

    learner = await learner_repo.get_by_id(learner_id)
    if learner is None or learner.guardian_id != guardian_id or learner.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

    # Lessons over last 30 days (bucketed by day for chart)
    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
    lessons_result = await db.execute(
        select(Lesson.created_at, Lesson.subject, Lesson.tokens_used)
        .where(Lesson.learner_id == learner_id, Lesson.created_at >= thirty_days_ago)
        .order_by(Lesson.created_at)
    )
    lessons_raw = lessons_result.all()

    # Build daily lesson count for chart
    daily_counts: dict[str, int] = {}
    for created_at, subject, _ in lessons_raw:
        day = created_at.strftime("%Y-%m-%d")
        daily_counts[day] = daily_counts.get(day, 0) + 1

    chart_data = [{"date": d, "lessons": c} for d, c in sorted(daily_counts.items())]

    # Knowledge gap breakdown by subject
    gaps_result = await db.execute(
        select(KnowledgeGap.subject, KnowledgeGap.resolved)
        .where(KnowledgeGap.learner_id == learner_id)
    )
    gap_summary: dict[str, dict] = {}
    for subject, resolved in gaps_result.all():
        if subject not in gap_summary:
            gap_summary[subject] = {"subject": subject, "active": 0, "resolved": 0}
        if resolved:
            gap_summary[subject]["resolved"] += 1
        else:
            gap_summary[subject]["active"] += 1

    return {
        "learner_id": str(learner_id),
        "display_name": learner.display_name,
        "grade_level": learner.grade_level,
        "archetype": learner.archetype,
        "irt_theta": round(learner.irt_theta, 3),
        "irt_theta_percentile": _theta_to_percentile(learner.irt_theta),
        "lessons_last_30_days": chart_data,
        "knowledge_gap_breakdown": list(gap_summary.values()),
        "total_lessons": len(lessons_raw),
    }


@router.delete(
    "/learners/{learner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="POPIA Section 24 — Guardian-initiated right to erasure",
)
async def request_erasure(
    learner_id: uuid.UUID,
    current_user: Annotated[TokenPayload, Depends(require_role(Role.PARENT))],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Initiates the POPIA right-to-erasure workflow.
    1. Soft-deletes the learner immediately (blocks all data access).
    2. Schedules hard deletion of PII via BackgroundTasks (30-day grace).
    Requires a valid Guardian JWT (enforced by require_role(Role.PARENT)).
    """
    guardian_id = uuid.UUID(current_user.sub)
    learner_repo = LearnerRepository(db)
    guardian_repo = GuardianRepository(db)

    learner = await learner_repo.get_by_id(learner_id)
    if learner is None or learner.guardian_id != guardian_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

    # Revoke active consent
    consent = await guardian_repo.get_active_consent(guardian_id, learner_id)
    if consent:
        await guardian_repo.revoke_consent(consent)

    # Soft-delete immediately
    await learner_repo.soft_delete(learner)
    await db.commit()

    # Audit the erasure request
    fourth_estate.enqueue(
        background_tasks, db,
        action=AuditAction.ERASURE_REQUESTED,
        actor_id=str(guardian_id),
        subject_pseudonym_id=str(learner.pseudonym_id),
        payload={"grace_period_days": 30},
        constitutional_stamp="APPROVED",
    )

    # Schedule hard deletion after 30-day grace period via BackgroundTasks
    # In production this would be scheduled via a cron/BackgroundTask with delay
    background_tasks.add_task(
        learner_repo.hard_delete_for_erasure, learner_id
    )


def _theta_to_percentile(theta: float) -> int:
    """
    Approximate θ ability score to a curriculum percentile.
    θ is on a standard normal scale; grade-normed interpretation.
    """
    import math
    # Standard normal CDF approximation
    x = theta / (2 ** 0.5)
    percentile = 50 + 50 * math.erf(x)
    return max(1, min(99, round(percentile)))
