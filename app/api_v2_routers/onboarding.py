"""EduBoost V2 — Onboarding Router (Ether Cold-Start Fix)"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.schemas import OnboardingResult, OnboardingSubmit
from app.repositories.learner_repository import LearnerRepository
from app.services.archetype_service import ArchetypeService

router = APIRouter(prefix="/onboarding", tags=["onboarding"])
_ether = ArchetypeService()


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
    from app.services.learner_service import LearnerService
    
    svc = LearnerService(db)
    answers_raw = [{"question_id": a.question_id, "answer": a.answer} for a in body.answers]
    
    result = await svc.process_onboarding(body.learner_id, answers_raw)
    return OnboardingResult(**result)
