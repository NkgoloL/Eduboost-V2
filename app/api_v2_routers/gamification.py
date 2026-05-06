"""Gamification routes for EduBoost V2."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.gamification_repository import GamificationRepository
from app.repositories.learner_repository import LearnerRepository
from app.repositories.lesson_repository import LessonRepository
from app.services.consent import ConsentService
from app.services.audit_service import AuditService
from app.services.gamification_service_v2 import GamificationServiceV2

router = APIRouter(prefix="/gamification", tags=["V2 Gamification"])


class AwardXPRequest(BaseModel):
    learner_id: str
    xp_amount: int = Field(ge=1, le=500)
    event_type: str = "lesson_completed"
    lesson_id: str | None = None


@router.get("/profile/{learner_id}")
async def get_profile(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    await ConsentService(db).require_active_consent(learner_id, actor_id=current_user.get("sub"))
    try:
        return await GamificationServiceV2(GamificationRepository(db)).get_profile(learner_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found") from exc


@router.post("/award-xp")
async def award_xp(
    body: AwardXPRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    await ConsentService(db).require_active_consent(body.learner_id, actor_id=current_user.get("sub"))
    learner = await LearnerRepository(db).get_by_id(body.learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

    learner_repo = LearnerRepository(db)
    await learner_repo.add_xp(body.learner_id, body.xp_amount)
    if body.lesson_id:
        await LessonRepository(db).mark_completed(body.lesson_id)

    await AuditService(db).record(
        event_type="gamification.xp_awarded",
        actor_id=current_user.get("sub"),
        learner_pseudonym=learner.pseudonym_id,
        resource_id=body.learner_id,
        payload={
            "learner_id": body.learner_id,
            "xp_amount": body.xp_amount,
            "event_type": body.event_type,
            "lesson_id": body.lesson_id,
        },
        constitutional_outcome="APPROVED",
    )
    await db.commit()
    updated_profile = await GamificationServiceV2(GamificationRepository(db)).get_profile(body.learner_id)
    return {
        "awarded": True,
        "xp_amount": body.xp_amount,
        "lesson_completed": bool(body.lesson_id),
        "profile": updated_profile,
    }


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await GamificationServiceV2(GamificationRepository(db)).leaderboard(limit=limit)
