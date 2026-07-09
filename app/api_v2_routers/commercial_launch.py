"""Billing and commercial launch readiness routes for PRD-9."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.envelope_route import EnvelopedRoute
from app.modules.commercial_launch import build_default_commercial_launch_readiness_report

router = APIRouter(route_class=EnvelopedRoute, prefix="/commercial-launch", tags=["commercial-launch"])


@router.get("/readiness")
async def get_commercial_launch_readiness() -> dict:
    """Return deterministic PRD-9 billing/commercial readiness.

    This endpoint exposes test-mode billing provider, pricing/packaging,
    checkout/webhook dry-run, subscription entitlement, invoicing/refund/tax,
    sponsorship/school procurement, support reconciliation, and terms/privacy
    launch-comms readiness. It does not authorise billing launch, live payment
    processing, live learner traffic, PRD-10 implementation, deployment, release
    tags, public beta, or production release.
    """

    return build_default_commercial_launch_readiness_report().to_payload()
