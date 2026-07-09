"""Content, CAPS, and educational-quality readiness route for PRD-4.0-4.4."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.envelope_route import EnvelopedRoute
from app.modules.content_quality.readiness import build_default_grade4_maths_readiness_report

router = APIRouter(route_class=EnvelopedRoute, prefix="/content-quality", tags=["content-quality"])


@router.get("/grade4-mathematics/readiness")
async def get_grade4_maths_content_quality_readiness() -> dict:
    """Return a deterministic Grade 4 Maths content-quality readiness view.

    The endpoint exposes the PRD-4 readiness contract. It does not authorise
    live learner traffic, public beta, deployment, or production release.
    """

    return build_default_grade4_maths_readiness_report().to_payload()
