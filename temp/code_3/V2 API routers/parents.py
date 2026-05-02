"""EduBoost V2 — Parent Portal Router (Phase 5)"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_parent_or_admin
from app.domain.schemas import ConsentStatus, ProgressSummary
from app.repositories.repositories import (
    ConsentRepository,
    KnowledgeGapRepository,
    LearnerRepository,
)
from app.services.executive import ExecutiveService

router = APIRouter(prefix="/parents", tags=["parent-portal"])
_executive = ExecutiveService()


@router.get("/learners", response_model=list[dict])
async def list_my_learners(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
):
    learners = await LearnerRepository(db).get_by_guardian(current_user["sub"])
    return [
        {
            "id": l.id,
            "display_name": l.display_name,
            "grade": l.grade,
            "xp": l.xp,
            "streak_days": l.streak_days,
            "archetype": l.archetype,
        }
        for l in learners
    ]


@router.get("/learners/{learner_id}/progress", response_model=ProgressSummary)
async def get_learner_progress(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
):
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_by_id(learner_id)
    if not learner or learner.guardian_id != current_user["sub"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

    gaps = await KnowledgeGapRepository(db).get_active_gaps(learner_id)
    lessons_count = await learner_repo.count_lessons(learner_id)
    gap_labels = [f"{g.subject}: {g.topic}" for g in gaps]

    ai_summary = await _executive.generate_progress_summary(
        pseudonym_id=learner.pseudonym_id,
        gaps=gap_labels,
        lessons_done=lessons_count,
    )

    return ProgressSummary(
        learner_id=learner_id,
        display_name=learner.display_name,
        grade=learner.grade,
        theta=learner.theta,
        xp=learner.xp,
        streak_days=learner.streak_days,
        lessons_completed=lessons_count,
        active_gaps=len(gaps),
        ai_summary=ai_summary,
    )


@router.get("/learners/{learner_id}/consent", response_model=ConsentStatus)
async def get_consent_status(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
):
    consent = await ConsentRepository(db).get_active(learner_id)
    if not consent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active consent found")
    return ConsentStatus.model_validate(consent)
