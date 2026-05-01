"""EduBoost V2 API entrypoint.

This app is intentionally lean and aligned with the V2 manifesto. It coexists
with the legacy runtime while migration proceeds.
"""

from __future__ import annotations

from fastapi import FastAPI

from app.core.logging import configure_logging
from app.core.config import get_v2_settings
from app.domain.schemas import HealthResponse
from app.api_v2_routers import auth, learners, diagnostics, study_plans, parents, audit, lessons, gamification, system, assessments

settings = get_v2_settings()
configure_logging(settings.log_level)
app = FastAPI(
    title="EduBoost V2 API",
    version="2.0.0-alpha",
    description="Strict modular-monolith baseline for EduBoost V2",
)


@app.get("/health", response_model=HealthResponse, tags=["V2 System"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", mode="v2-baseline")


app.include_router(auth.router)
app.include_router(learners.router)
app.include_router(diagnostics.router)
app.include_router(study_plans.router)
app.include_router(parents.router)
app.include_router(audit.router)
app.include_router(lessons.router)
app.include_router(gamification.router)
app.include_router(system.router)
app.include_router(assessments.router)
