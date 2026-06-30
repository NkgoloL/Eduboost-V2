"""Ether (Psychological/Onboarding) routes for EduBoost V2."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from app.core.envelope_route import EnvelopedRoute
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.models import UserRole
from app.core.security import get_current_user  # noqa: F401
from app.services.ether_service import EtherService, OnboardingResponse
from app.security.dependencies import require_active_consent_for_current_user
from app.core.database import get_db

router = APIRouter(route_class=EnvelopedRoute, prefix="/api/v2/ether", tags=["V2 Ether"])


@router.get("/onboarding/questions")
async def get_questions(user: AuthContext = Depends(require_auth_context)):
    """Get the visual onboarding question set."""
    return await EtherService().get_onboarding_questions()


@router.post("/onboarding/submit")
async def submit_onboarding(
    response: OnboardingResponse,
    user: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Submit onboarding responses to determine learner archetype."""
    if not any(role in {UserRole.STUDENT, UserRole.PARENT, UserRole.ADMIN} for role in user.roles):
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return await EtherService().determine_archetype(response)
