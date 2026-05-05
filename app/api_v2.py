"""
EduBoost V2 — FastAPI Application Entrypoint
Strict Modular Monolith. No Celery, no RabbitMQ, no microservices.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

from slowapi.errors import RateLimitExceeded

from app.core.analytics import analytics_middleware
from app.core.config import settings
from app.core.health import gather_deep_health
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.metrics import REGISTRY
from app.core.middleware import RequestIDMiddleware, StructuredLoggingMiddleware, TimingMiddleware
from app.core.rate_limit import limiter
from app.core.secret_rotation import key_vault_rotation_loop
from app.services.consent_expiry_service import consent_expiry_loop
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

configure_logging()
log = get_logger(__name__)

# SecurityHeadersMiddleware moved to app/middleware/security_headers.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("eduboost_v2_starting", env=settings.ENVIRONMENT, version=settings.APP_VERSION)
    consent_task = None
    secret_rotation_task = None
    if settings.ENVIRONMENT != "test":
        consent_task = asyncio.create_task(consent_expiry_loop())
        if settings.is_production() and settings.AZURE_KEY_VAULT_URL:
            secret_rotation_task = asyncio.create_task(key_vault_rotation_loop())
    yield
    if consent_task:
        consent_task.cancel()
    if secret_rotation_task:
        secret_rotation_task.cancel()
    log.info("eduboost_v2_shutdown")


app = FastAPI(
    title="EduBoost SA V2",
    version=settings.APP_VERSION,
    description="AI-powered adaptive learning platform — Grade R to 7. CAPS-aligned. POPIA-compliant.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Rate Limiter (attach to app for per-endpoint limits) ─────────────────────
app.state.limiter = limiter
register_exception_handlers(app)


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please upgrade to Premium for higher limits."},
    )


# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.middleware("http")(analytics_middleware)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.api_v2_routers import auth, billing, consent, consent_renewal, diagnostics, gamification, jobs, learners, lessons, onboarding, parents, popia, study_plans  # noqa: E402

API_V2 = "/api/v2"
for prefix in (API_V2, "/v2"):
    app.include_router(auth.router, prefix=prefix)
    app.include_router(learners.router, prefix=prefix)
    app.include_router(lessons.router, prefix=prefix)
    app.include_router(study_plans.router, prefix=prefix)
    app.include_router(diagnostics.router, prefix=prefix)
    app.include_router(gamification.router, prefix=prefix)
    app.include_router(onboarding.router, prefix=prefix)
    app.include_router(parents.router, prefix=prefix)
    app.include_router(billing.router, prefix=prefix)
    app.include_router(consent.router, prefix=prefix)
    app.include_router(consent_renewal.router, prefix=prefix)
    app.include_router(popia.router, prefix=prefix)
    app.include_router(jobs.router, prefix=prefix)


# ── Health & meta ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["ops"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION, "environment": settings.ENVIRONMENT, "mode": "v2-baseline"}


@app.get("/ready", tags=["ops"])
async def ready():
    # Perform deep health checks and return appropriate status
    # 'ok' or 'degraded' returns 200, 'error' returns 503
    health_data = await gather_deep_health()
    status_code = 200 if health_data["status"] in ("ok", "degraded") else 503
    return JSONResponse(status_code=status_code, content=health_data)



@app.get("/api/v2/health/deep", tags=["ops"])
@app.get("/v2/health/deep", tags=["ops"])
async def deep_health():
    payload = await gather_deep_health()
    status_code = 200 if payload["status"] in ("ok", "degraded") else 503
    return JSONResponse(status_code=status_code, content=payload)


@app.get("/metrics", tags=["ops"])
async def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


@app.get("/", tags=["ops"])
async def root():
    return JSONResponse({"message": "EduBoost SA V2 — Ngiyabonga! 🦁", "docs": "/docs"})
