"""EduBoost V2 — Onboarding Router (Ether Cold-Start Fix)"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.schemas import OnboardingResult, OnboardingSubmit
from app.repositories.learner_repository import LearnerRepository
from app.services.ether import EtherService

router = APIRouter(prefix="/onboarding", tags=["onboarding"])
_ether = EtherService()


@router.get("/questions")
async def get_onboarding_questions(_: dict = Depends(get_current_user)):
    return _ether.get_onboarding_questions()


@router.post("/submit", response_model=OnboardingResult)
@router.post("/archetype", response_model=OnboardingResult)
async def submit_onboarding(
    body: OnboardingSubmit,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_by_id(body.learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")

    answers_raw = [{"question_id": a.question_id, "answer": a.answer} for a in body.answers]
    archetype, description, probabilities = _ether.classify_archetype(answers_raw)

    await learner_repo.update_archetype(body.learner_id, archetype.value)

    return OnboardingResult(
        learner_id=body.learner_id,
        archetype=archetype.value,
        description=description,
        probabilities=probabilities,
    )
