"""Production release and deployment authorisation routes for PRD-11."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.envelope_route import EnvelopedRoute
from app.modules.production_release import build_default_production_release_preflight_report

router = APIRouter(route_class=EnvelopedRoute, prefix="/production-release", tags=["production-release"])


@router.get("/preflight")
async def get_production_release_preflight() -> dict:
    """Return PRD-11.0-11.4 production release preflight readiness.

    This route defines release candidate, versioning, tag freeze, deployment,
    secrets/config, migration, rollback, beta-to-production go/no-go, support,
    monitoring, incident, and release-communications gates. It does not
    authorise production release, deployment, release tagging, public beta,
    billing launch, or live payment processing.
    """

    return build_default_production_release_preflight_report().to_payload()
