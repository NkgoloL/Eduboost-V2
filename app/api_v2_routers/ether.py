"""Legacy Ether onboarding compatibility router for auth-boundary coverage.

This file intentionally preserves the historical `ether.py` auth-boundary
contract while the canonical learner onboarding routes remain in
`app.api_v2_routers.onboarding`. The route is authenticated and learner-facing;
it is not added to ROUTER_REGISTRY in this slice to avoid expanding the public
OpenAPI surface without a separate route-alias decision.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.envelope_route import EnvelopedRoute
from app.services.ether import EtherService

router = APIRouter(route_class=EnvelopedRoute, prefix="/ether", tags=["ether"])
_ether = EtherService()


@router.get("/onboarding/questions")
async def get_questions(user: AuthContext = Depends(require_auth_context)):
    """Return authenticated visual onboarding questions for legacy Ether clients."""
    return _ether.get_onboarding_questions()
