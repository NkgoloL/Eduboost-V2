"""Judiciary (Governance/Validation) routes for EduBoost V2."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from app.core.envelope_route import EnvelopedRoute

from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.dependencies import RequireRole
from app.models import UserRole
from app.core.security import get_current_user  # noqa: F401
from app.services.judiciary_service_v2 import JudiciaryServiceV2

router = APIRouter(route_class=EnvelopedRoute, prefix="/api/v2/judiciary", tags=["V2 Judiciary"])


@router.post("/screen")
async def screen_content(
    text: str,
    user: AuthContext = Depends(require_auth_context),
):
    """Manually trigger content screening (Admin/Teacher only)."""
    if not any(role in {UserRole.ADMIN, UserRole.TEACHER} for role in user.roles):
        raise HTTPException(status_code=403, detail="Forbidden")
        
    is_safe = await JudiciaryServiceV2().screen_content(text)
    return {"is_safe": is_safe}


@router.get("/status", dependencies=[Depends(RequireRole(["Admin"]))])
async def get_judiciary_status():
    """Get the current status of the constitutional engine."""
    return {
        "engine": "V2_Modular_Baseline",
        "rules_active": 3,
        "enforcement_mode": "STRICT",
    }
