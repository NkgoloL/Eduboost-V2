"""Judiciary (Governance/Validation) routes for EduBoost V2."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user, RequireRole
from app.services.judiciary_service_v2 import PolicyServiceV2

router = APIRouter(prefix="/api/v2/judiciary", tags=["V2 Judiciary"])


@router.post("/screen")
async def screen_content(
    text: str,
    user: dict = Depends(get_current_user),
):
    """Manually trigger content screening (Admin/Teacher only)."""
    if user.get("role") not in {"Admin", "Teacher"}:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    is_safe = await PolicyServiceV2().screen_content(text)
    return {"is_safe": is_safe}


@router.get("/status", dependencies=[Depends(RequireRole(["Admin"]))])
async def get_judiciary_status():
    """Get the current status of the constitutional engine."""
    return {
        "engine": "V2_Modular_Baseline",
        "rules_active": 3,
        "enforcement_mode": "STRICT",
    }
