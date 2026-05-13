"""Ether (Psychological/Onboarding) routes for EduBoost V2."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from app.core.envelope_route import EnvelopedRoute
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.services.ether_service import EtherService, OnboardingResponse
from app.security.dependencies import require_active_consent_for_current_user
from app.core.database import get_db

router = APIRouter(route_class=EnvelopedRoute, prefix="/api/v2/ether", tags=["V2 Ether"])


@router.get("/onboarding/questions")
async def get_questions(user: dict = Depends(get_current_user)):
    """Get the visual onboarding question set."""
    return await EtherService().get_onboarding_questions()


@router.post("/onboarding/submit")
async def submit_onboarding(
    response: OnboardingResponse,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit onboarding responses to determine learner archetype."""
    if user.get("role") not in {"Student", "Parent", "Admin"}:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return await EtherService().determine_archetype(response)
