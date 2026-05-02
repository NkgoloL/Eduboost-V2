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


@router.get("/{guardian_id}/dashboard")
async def get_parent_dashboard(
    guardian_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
):
    if guardian_id != current_user["sub"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised for this dashboard")

    learner_repo = LearnerRepository(db)
    learners = await learner_repo.get_by_guardian(guardian_id)
    dashboard_rows = []
    for learner in learners:
        gaps = await KnowledgeGapRepository(db).get_active_gaps(learner.id)
        consent = await ConsentRepository(db).get_active(learner.id)
        lessons_count = await learner_repo.count_lessons(learner.id)
        dashboard_rows.append(
            {
                "learner_id": learner.id,
                "pseudonym_id": learner.pseudonym_id,
                "display_name": learner.display_name,
                "grade": learner.grade,
                "theta": learner.theta,
                "reading_level_label": _theta_label(learner.theta, learner.grade),
                "lessons_completed_7d": lessons_count,
                "lessons_completed_30d": lessons_count,
                "knowledge_gaps_active": len(gaps),
                "knowledge_gaps": [{"subject": gap.subject, "topic": gap.topic, "severity": gap.severity} for gap in gaps],
                "consent": {
                    "active": bool(consent),
                    "renewal_date": consent.expires_at if consent else None,
                    "policy_version": consent.policy_version if consent else None,
                },
            }
        )

    return {"guardian_id": guardian_id, "learners": dashboard_rows}


@router.get("/{guardian_id}/report")
async def get_parent_report(
    guardian_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
):
    if guardian_id != current_user["sub"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised for this report")

    learner_repo = LearnerRepository(db)
    learners = await learner_repo.get_by_guardian(guardian_id)
    summaries = []
    for learner in learners:
        gaps = await KnowledgeGapRepository(db).get_active_gaps(learner.id)
        gap_labels = [f"{gap.subject}: {gap.topic}" for gap in gaps]
        lessons_count = await learner_repo.count_lessons(learner.id)
        narrative = await _executive.generate_progress_summary(
            pseudonym_id=learner.pseudonym_id,
            gaps=gap_labels,
            lessons_done=lessons_count,
        )
        summaries.append(
            {
                "learner_id": learner.id,
                "pseudonym_id": learner.pseudonym_id,
                "grade": learner.grade,
                "summary": narrative,
            }
        )
    return {"guardian_id": guardian_id, "reports": summaries}


def _theta_label(theta: float, current_grade: int) -> str:
    estimated_grade = max(0, min(7, round(current_grade + theta)))
    return "Grade R level" if estimated_grade == 0 else f"Grade {estimated_grade} level"
