"""Controlled beta and live learner traffic routes for PRD-10."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.envelope_route import EnvelopedRoute
from app.modules.controlled_beta import (
    build_default_controlled_beta_final_authorisation_report,
    build_default_controlled_beta_preflight_report,
)

router = APIRouter(route_class=EnvelopedRoute, prefix="/controlled-beta", tags=["controlled-beta"])


@router.get("/preflight")
async def get_controlled_beta_preflight() -> dict:
    """Return PRD-10.0-10.4 controlled beta/live traffic preflight readiness.

    This route defines the controlled beta cohort, guardian consent,
    eligibility, PyJWT auth-token regression, dry-run, kill-switch,
    rollback, support, monitoring, incident escalation, and go/no-go gates.
    It does not authorise live learner traffic, public beta, production
    release, deployment, billing launch, or live payment processing.
    """

    return build_default_controlled_beta_preflight_report().to_payload()


@router.get("/final-authorisation")
async def get_controlled_beta_final_authorisation() -> dict:
    """Return PRD-10.5-10.9 final controlled-beta authorisation decision.

    This route records the limited controlled-beta live learner traffic
    decision and keeps public beta, production release, deployment,
    billing launch, and live payment processing locked out.
    """

    return build_default_controlled_beta_final_authorisation_report().to_payload()
