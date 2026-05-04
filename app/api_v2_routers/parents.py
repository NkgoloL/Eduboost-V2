"""EduBoost V2 — Parent portal router."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_parent_or_admin
from app.domain.schemas import ParentDashboardLearner, ParentDashboardResponse
from app.models import Guardian, KnowledgeGap, Lesson
from app.repositories.repositories import LearnerRepository
from app.services.consent import ConsentService
from app.services.fourth_estate import FourthEstateService

router = APIRouter(prefix="/parents", tags=["parents"])


@router.get("/dashboard", response_model=ParentDashboardResponse)
async def get_parent_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
) -> ParentDashboardResponse:
    guardian = await db.get(Guardian, current_user["sub"])
    if guardian is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guardian not found")

    learners = await LearnerRepository(db).get_by_guardian(current_user["sub"])
    consent_service = ConsentService(db)
    one_week_ago = datetime.now(UTC) - timedelta(days=7)

    dashboard_learners: list[ParentDashboardLearner] = []
    total_lessons_generated = 0

    for learner in learners:
        try:
            await consent_service.require_active_consent(learner.id, actor_id=current_user["sub"])
        except HTTPException:
            continue

        lessons_this_week = await db.scalar(
            select(func.count(Lesson.id)).where(
                Lesson.learner_id == learner.id,
                Lesson.created_at >= one_week_ago,
            )
        )
        active_gaps = await db.scalar(
            select(func.count(KnowledgeGap.id)).where(
                KnowledgeGap.learner_id == learner.id,
                KnowledgeGap.resolved == False,  # noqa: E712
            )
        )
        last_lesson_at = await db.scalar(
            select(Lesson.created_at)
            .where(Lesson.learner_id == learner.id)
            .order_by(Lesson.created_at.desc())
            .limit(1)
        )
        learner_total_lessons = await db.scalar(
            select(func.count(Lesson.id)).where(Lesson.learner_id == learner.id)
        )
        total_lessons_generated += learner_total_lessons or 0

        dashboard_learners.append(
            ParentDashboardLearner(
                learner_id=learner.id,
                display_name=learner.display_name,
                grade_level=str(learner.grade),
                archetype=learner.archetype,
                irt_theta=round(learner.theta, 3),
                lessons_this_week=lessons_this_week or 0,
                active_knowledge_gaps=active_gaps or 0,
                last_lesson_at=last_lesson_at,
            )
        )

    return ParentDashboardResponse(
        guardian_id=guardian.id,
        learners=dashboard_learners,
        total_lessons_generated=total_lessons_generated,
        subscription_tier=guardian.subscription_tier,
    )


@router.get("/learners/{learner_id}/progress")
async def get_learner_progress(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
) -> dict:
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    if learner.guardian_id != current_user["sub"] and str(current_user.get("role", "")).lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to view this learner")

    await ConsentService(db).require_active_consent(learner_id, actor_id=current_user["sub"])

    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
    lessons = (
        await db.execute(
            select(Lesson.created_at, Lesson.subject)
            .where(Lesson.learner_id == learner_id, Lesson.created_at >= thirty_days_ago)
            .order_by(Lesson.created_at)
        )
    ).all()
    gaps = (
        await db.execute(
            select(KnowledgeGap.subject, KnowledgeGap.resolved)
            .where(KnowledgeGap.learner_id == learner_id)
            .order_by(KnowledgeGap.subject)
        )
    ).all()

    daily_counts: dict[str, int] = {}
    for created_at, _subject in lessons:
        day = created_at.strftime("%Y-%m-%d")
        daily_counts[day] = daily_counts.get(day, 0) + 1

    gap_summary: dict[str, dict[str, int | str]] = {}
    for subject, resolved in gaps:
        entry = gap_summary.setdefault(subject, {"subject": subject, "active": 0, "resolved": 0})
        key = "resolved" if resolved else "active"
        entry[key] += 1

    return {
        "learner_id": learner.id,
        "display_name": learner.display_name,
        "grade_level": learner.grade,
        "archetype": learner.archetype,
        "irt_theta": round(learner.theta, 3),
        "lessons_last_30_days": [{"date": day, "lessons": count} for day, count in sorted(daily_counts.items())],
        "knowledge_gap_breakdown": list(gap_summary.values()),
        "total_lessons": len(lessons),
    }


@router.delete("/learners/{learner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def request_erasure(
    learner_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
) -> Response:
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    if learner.guardian_id != current_user["sub"] and str(current_user.get("role", "")).lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to erase this learner")

    consent_service = ConsentService(db)
    await consent_service.execute_erasure(current_user["sub"], learner_id)
    await LearnerRepository(db).soft_delete(learner_id)

    await FourthEstateService(db).record(
        "learner.erasure_requested",
        actor_id=current_user["sub"],
        learner_pseudonym=learner.pseudonym_id,
        resource_id=learner_id,
        payload={"learner_id": learner_id, "source": "parents_router"},
        constitutional_outcome="APPROVED",
    )

    background_tasks.add_task(_log_purge_request, learner_id, learner.pseudonym_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _log_purge_request(learner_id: str, learner_pseudonym: str) -> None:
    return None
