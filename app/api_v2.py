"""
EduBoost V2 — FastAPI Application Entrypoint
Strict Modular Monolith. No Celery, no RabbitMQ, no microservices.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.api.version import __version__
from app.core.analytics import analytics_middleware
from app.services.consent_expiry_service import consent_expiry_loop

configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("eduboost_v2_starting", env=settings.ENVIRONMENT, version=settings.APP_VERSION)
    consent_task = None
    if settings.ENVIRONMENT != "test":
        consent_task = asyncio.create_task(consent_expiry_loop())
    yield
    if consent_task:
        consent_task.cancel()
    log.info("eduboost_v2_shutdown")


app = FastAPI(
    title="EduBoost SA V2",
    version=settings.APP_VERSION,
    description="AI-powered adaptive learning platform — Grade R to 7. CAPS-aligned. POPIA-compliant.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(analytics_middleware)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.api_v2_routers import auth, billing, diagnostics, learners, lessons, onboarding, parents  # noqa: E402
from app.api_v2_routers import audit, gamification, study_plans, system  # noqa: E402

API_V2 = "/api/v2"
app.include_router(auth.router, prefix=API_V2)
app.include_router(learners.router, prefix=API_V2)
app.include_router(lessons.router, prefix=API_V2)
app.include_router(diagnostics.router, prefix=API_V2)
app.include_router(onboarding.router, prefix=API_V2)
app.include_router(parents.router, prefix=API_V2)
app.include_router(billing.router, prefix=API_V2)
app.include_router(audit.router, prefix=API_V2)
app.include_router(gamification.router, prefix=API_V2)
app.include_router(study_plans.router, prefix=API_V2)
app.include_router(system.router, prefix=API_V2)


# ── Health & meta ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["ops"])
async def health():
    return {"status": "ok", "version": __version__, "environment": settings.ENVIRONMENT, "mode": "v2-baseline"}


@app.get("/", tags=["ops"])
async def root():
    return JSONResponse({"message": "EduBoost SA V2 — Ngiyabonga! 🦁", "docs": "/docs"})
