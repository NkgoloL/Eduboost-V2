"""POPIA live-data operations readiness routes for PRD-5."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.envelope_route import EnvelopedRoute
from app.modules.privacy_ops.assurance import build_default_privacy_final_assurance_report
from app.modules.privacy_ops.readiness import build_default_privacy_live_data_readiness_report

router = APIRouter(route_class=EnvelopedRoute, prefix="/privacy-operations", tags=["privacy-operations"])


@router.get("/live-data/readiness")
async def get_popia_live_data_operations_readiness() -> dict:
    """Return deterministic POPIA live-data operations readiness.

    This endpoint exposes PRD-5 readiness controls. It does not authorise
    public beta, live learner traffic, billing, deployment, or production
    release.
    """

    return build_default_privacy_live_data_readiness_report().to_payload()


@router.get("/live-data/final-assurance")
async def get_popia_live_data_operations_final_assurance() -> dict:
    """Return deterministic PRD-5 final POPIA privacy assurance.

    This endpoint closes PRD-5 privacy assurance visibility and records
    readiness for PRD-6 handoff. It does not authorise PRD-6
    implementation, live learner traffic, deployment, billing, public beta,
    release tags, or production release.
    """

    return build_default_privacy_final_assurance_report().to_payload()
