"""Security assurance readiness routes for PRD-6."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.envelope_route import EnvelopedRoute
from app.modules.security_assurance import build_default_security_assurance_readiness_report

router = APIRouter(route_class=EnvelopedRoute, prefix="/security-assurance", tags=["security-assurance"])


@router.get("/readiness")
async def get_security_assurance_readiness() -> dict:
    """Return deterministic PRD-6 security assurance readiness.

    This endpoint exposes security-assurance controls and evidence readiness.
    It does not run scanners, modify branch protection, authorise PRD-7,
    authorise public beta, live learner traffic, billing, deployment, release
    tags, or production release.
    """

    return build_default_security_assurance_readiness_report().to_payload()
