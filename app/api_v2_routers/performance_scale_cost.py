"""Performance, scale, and cost execution routes for PRD-8."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.envelope_route import EnvelopedRoute
from app.modules.performance_scale_cost import (
    build_default_performance_scale_cost_final_assurance_report,
    build_default_performance_scale_cost_readiness_report,
)

router = APIRouter(route_class=EnvelopedRoute, prefix="/performance-scale-cost", tags=["performance-scale-cost"])


@router.get("/readiness")
async def get_performance_scale_cost_readiness() -> dict:
    """Return deterministic PRD-8 performance, scale, and cost readiness.

    This endpoint exposes load-test, runtime-KG query-performance, database/index,
    LLM cost, queue/backpressure, frontend-budget, and capacity-plan readiness. It
    does not run load tests, modify infrastructure, authorise PRD-9, authorise
    public beta, live learner traffic, billing, deployment, release tags, or
    production release.
    """

    return build_default_performance_scale_cost_readiness_report().to_payload()


@router.get("/final-assurance")
async def get_performance_scale_cost_final_assurance() -> dict:
    """Return deterministic PRD-8 final performance, scale, and cost assurance.

    This endpoint exposes final load-test, runtime-KG query-performance,
    database/index, LLM-cost, queue/backpressure, capacity, and frontend-budget
    evidence acceptance. It does not authorise PRD-9 implementation, billing,
    live payment processing, live learner traffic, deployment, release tags,
    public beta, or production release.
    """

    return build_default_performance_scale_cost_final_assurance_report().to_payload()
