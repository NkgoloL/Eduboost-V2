"""Observability, SRE, and incident-readiness routes for PRD-7."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.envelope_route import EnvelopedRoute
from app.modules.observability import build_default_observability_sre_readiness_report

router = APIRouter(route_class=EnvelopedRoute, prefix="/observability-sre", tags=["observability-sre"])


@router.get("/readiness")
async def get_observability_sre_readiness() -> dict:
    """Return deterministic PRD-7 observability/SRE readiness.

    This endpoint exposes dashboards, alerts, SLOs, runbooks, on-call,
    backup/restore/rollback, privacy escalation, and support-communications
    readiness. It does not connect to telemetry backends, modify infrastructure,
    authorise PRD-8, authorise public beta, live learner traffic, billing,
    deployment, release tags, or production release.
    """

    return build_default_observability_sre_readiness_report().to_payload()
