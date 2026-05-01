"""Ether (Psychological/Onboarding) routes for EduBoost V2."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.services.ether_service import EtherService, OnboardingResponse

router = APIRouter(prefix="/api/v2/ether", tags=["V2 Ether"])


@router.get("/onboarding/questions")
async def get_questions():
    """Get the visual onboarding question set."""
    return await EtherService().get_onboarding_questions()


@router.post("/onboarding/submit")
async def submit_onboarding(
    response: OnboardingResponse,
    user: dict = Depends(get_current_user),
):
    """Submit onboarding responses to determine learner archetype."""
    if user.get("role") not in {"Student", "Parent", "Admin"}:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return await EtherService().determine_archetype(response)
