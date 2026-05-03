"""
EduBoost V2 — FastAPI Application Entrypoint
Strict Modular Monolith. No Celery, no RabbitMQ, no microservices.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.rate_limit import limiter

configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("eduboost_v2_starting", env=settings.ENVIRONMENT, version=settings.APP_VERSION)
    yield
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

# ── Routers ───────────────────────────────────────────────────────────────────
from app.api_v2_routers import auth, billing, diagnostics, learners, lessons, onboarding, parents, popia  # noqa: E402

API_V2 = "/api/v2"
app.include_router(auth.router, prefix=API_V2)
app.include_router(learners.router, prefix=API_V2)
app.include_router(lessons.router, prefix=API_V2)
app.include_router(diagnostics.router, prefix=API_V2)
app.include_router(onboarding.router, prefix=API_V2)
app.include_router(parents.router, prefix=API_V2)
app.include_router(billing.router, prefix=API_V2)
app.include_router(popia.router, prefix=API_V2)


# ── Health & meta ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["ops"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION, "environment": settings.ENVIRONMENT}


@app.get("/", tags=["ops"])
async def root():
    return JSONResponse({"message": "EduBoost SA V2 — Ngiyabonga! 🦁", "docs": "/docs"})
