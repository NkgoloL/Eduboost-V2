"""Content, CAPS, and educational-quality readiness routes for PRD-4."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.envelope_route import EnvelopedRoute
from app.modules.content_quality.acceptance import build_default_grade4_maths_content_quality_acceptance_report
from app.modules.content_quality.readiness import build_default_grade4_maths_readiness_report

router = APIRouter(route_class=EnvelopedRoute, prefix="/content-quality", tags=["content-quality"])


@router.get("/grade4-mathematics/readiness")
async def get_grade4_maths_content_quality_readiness() -> dict:
    """Return a deterministic Grade 4 Maths content-quality readiness view.

    The endpoint exposes the PRD-4 readiness contract. It does not authorise
    live learner traffic, public beta, deployment, or production release.
    """

    return build_default_grade4_maths_readiness_report().to_payload()


@router.get("/grade4-mathematics/final-acceptance")
async def get_grade4_maths_content_quality_final_acceptance() -> dict:
    """Return the final PRD-4 educational-readiness acceptance view.

    The endpoint confirms PRD-4 closure readiness while preserving the
    handoff boundary: PRD-5 is next, but PRD-5 implementation is not
    authorised here.
    """

    return build_default_grade4_maths_content_quality_acceptance_report().to_payload()
