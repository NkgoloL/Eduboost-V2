"""
EduBoost V2 — FastAPI Application Entrypoint
Strict Modular Monolith. No Celery, no RabbitMQ, no microservices.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger

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

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.api_v2_routers import auth, billing, diagnostics, learners, lessons, onboarding, parents  # noqa: E402

API_V2 = "/api/v2"
app.include_router(auth.router, prefix=API_V2)
app.include_router(learners.router, prefix=API_V2)
app.include_router(lessons.router, prefix=API_V2)
app.include_router(diagnostics.router, prefix=API_V2)
app.include_router(onboarding.router, prefix=API_V2)
app.include_router(parents.router, prefix=API_V2)
app.include_router(billing.router, prefix=API_V2)


# ── Health & meta ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["ops"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION, "environment": settings.ENVIRONMENT}


@app.get("/", tags=["ops"])
async def root():
    return JSONResponse({"message": "EduBoost SA V2 — Ngiyabonga! 🦁", "docs": "/docs"})
