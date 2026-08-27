"""EduBoost V2 — Onboarding Router (Ether Cold-Start Fix)"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.envelope_route import EnvelopedRoute
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.security import get_current_user  # noqa: F401
from app.domain.schemas import OnboardingResult, OnboardingSubmit
from app.services.learner_service import LearnerService
from app.services.ether import EtherService
from app.security.dependencies import require_active_consent_for_current_user, require_learner_write_for_current_user

router = APIRouter(route_class=EnvelopedRoute, prefix="/onboarding", tags=["onboarding"])
_ether = EtherService()


@router.get("/questions")
async def get_onboarding_questions(current_user: AuthContext = Depends(require_auth_context)):
    return _ether.get_onboarding_questions()


@router.post("/submit", response_model=OnboardingResult)
@router.post("/archetype", response_model=OnboardingResult)
async def submit_onboarding(
    body: OnboardingSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_auth_context),
):
    learner_svc = LearnerService(db)
    learner = await learner_svc.get_learner_summary(body.learner_id)
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_write_for_current_user(current_user, body.learner_id)
    await require_active_consent_for_current_user(db, current_user, body.learner_id)

    answers_raw = [{"question_id": a.question_id, "answer": a.answer} for a in body.answers]
    res = await learner_svc.process_onboarding(body.learner_id, answers_raw)

    return OnboardingResult(
        learner_id=res["learner_id"],
        archetype=res["archetype"],
        description=res["description"],
        probabilities=res["probabilities"],
    )
