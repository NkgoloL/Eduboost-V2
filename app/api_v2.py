"""
EduBoost V2 — FastAPI Application Entrypoint
Strict Modular Monolith. No Celery, no RabbitMQ, no microservices.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from ipaddress import ip_address, ip_network

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.core.analytics import analytics_middleware
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.health import gather_deep_health
from app.core.logging import configure_logging, get_logger
from app.core.metrics import REGISTRY
from app.core.middleware import RequestIDMiddleware, StructuredLoggingMiddleware, TimingMiddleware
from app.core.rate_limit import limiter
from app.core.secret_rotation import key_vault_rotation_loop
from app.middleware.api_deprecation import APIDeprecationMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.services.consent_expiry_service import consent_expiry_loop
from app.services.launch_content_seed import seed_launch_content_if_needed
from app.services.jwt_keyring import validate_jwt_keyring_environment

validate_jwt_keyring_environment()

configure_logging()
log = get_logger(__name__)

METRICS_ALLOWED_NETWORKS = tuple(
    ip_network(network)
    for network in (
        "127.0.0.0/8",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "::1/128",
        "fc00::/7",
        "fe80::/10",
    )
)


def _is_private_metrics_client(client_ip: str) -> bool:
    """Return whether a metrics scrape originated from an allowed private range."""
    try:
        address = ip_address(client_ip)
    except ValueError:
        return False
    return any(address in network for network in METRICS_ALLOWED_NETWORKS)


def _metrics_client_ip(request: Request) -> str:
    """Resolve the direct peer IP for metrics access control.

    Forwarded headers are intentionally ignored here. They can only be trusted
    after the deployment defines an explicit trusted-proxy allowlist.
    """
    return request.client.host if request.client else ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("eduboost_v2_starting", env=settings.ENVIRONMENT, version=settings.APP_VERSION)
    await seed_launch_content_if_needed()
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


OPENAPI_TAGS = [
    {"name": "ops", "description": "Health, readiness, and system status"},
    {"name": "auth", "description": "Authentication and token management"},
    {"name": "learners", "description": "Learner profiles and progress"},
    {"name": "lessons", "description": "CAPS-aligned lesson content"},
    {"name": "learner-tutor", "description": "Safe lesson-scoped learner tutor"},
    {"name": "study_plans", "description": "Personalised study plans"},
    {"name": "diagnostics", "description": "Diagnostic assessments"},
    {"name": "practice", "description": "Practice activities and attempts"},
    {"name": "gamification", "description": "Points, badges, and streaks"},
    {"name": "onboarding", "description": "New learner and parent onboarding"},
    {"name": "parents", "description": "Parent/guardian management"},
    {"name": "vertical-journey", "description": "Learner and parent vertical journey hardening"},
    {"name": "content-quality", "description": "Content, CAPS, and educational quality readiness"},
    {"name": "billing", "description": "Subscription and payment"},
    {"name": "commercial-launch", "description": "Billing and commercial launch readiness"},
    {"name": "controlled-beta", "description": "Controlled beta and live learner traffic preflight readiness"},
    {"name": "consent", "description": "POPIA consent collection"},
    {"name": "popia", "description": "POPIA data subject rights"},
    {"name": "privacy-operations", "description": "POPIA live-data operations and privacy assurance"},
    {"name": "security-assurance", "description": "Security assurance and external review readiness"},
    {"name": "observability-sre", "description": "Observability, SRE, and incident readiness"},
    {"name": "performance-scale-cost", "description": "Performance, scale, and cost execution readiness"},
    {"name": "jobs", "description": "Background job status"},
    {"name": "admin-content-factory", "description": "Admin-only content factory and ETL provenance controls"},
    {"name": "admin-etl", "description": "Admin-only read visibility into ETL source material"},
    {"name": "admin-ai-operations", "description": "Admin-only AI usage, budget, and provider operations"},
    {"name": "admin-curriculum-expansion", "description": "Admin-only curriculum coverage and training dataset governance"},
    {"name": "learner-content", "description": "Learner-facing production content from Content Factory"},
    {"name": "admin-irt-quality", "description": "Admin-only IRT calibration and intervention controls"},
]

app = FastAPI(
    title="EduBoost SA V2",
    version=settings.APP_VERSION,
    openapi_tags=OPENAPI_TAGS,
    description="AI-powered adaptive learning platform — Grade R to 7. CAPS-aligned. POPIA-compliant.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Rate Limiter (attach to app for per-endpoint limits) ─────────────────────
app.state.limiter = limiter
register_exception_handlers(app)


# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(APIDeprecationMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.middleware("http")(analytics_middleware)


# ── Routers ───────────────────────────────────────────────────────────────────
from app.modules.practice import router as practice_router  # noqa: E402
from app.api_v2_routers import (  # noqa: E402
    curriculum_expansion,
    ai_operations,
    assessments,
    auth,
    auth_extended,
    audit,
    billing,
    commercial_launch,
    controlled_beta,
    consent,
    consent_renewal,
    content_factory,
    content_review,
    content_quality,
    admin_etl,
    diagnostics,
    gamification,
    generation,
    jobs,
    learner_content,
    irt_quality,
    learners,
    lessons,
    onboarding,
    observability_sre,
    performance_scale_cost,
    production_release,
    parents,
    popia,
    privacy_operations,
    security_assurance,
    study_plans,
    system,
    tutor,
    vertical_journey,
)

API_V2 = "/api/v2"
API_PREFIXES = (API_V2, "/v2")
ROUTER_REGISTRY = (
    ("curriculum_expansion", curriculum_expansion.router),
    ("ai_operations", ai_operations.router),
    ("assessments", assessments.router),
    ("auth", auth.router),
    ("auth_extended", auth_extended.router),
    ("audit", audit.router),
    ("learners", learners.router),
    ("lessons", lessons.router),
    ("tutor", tutor.router),
    ("study_plans", study_plans.router),
    ("diagnostics", diagnostics.router),
    ("practice", practice_router.router),
    ("gamification", gamification.router),
    ("generation", generation.router),
    ("onboarding", onboarding.router),
    ("parents", parents.router),
    ("vertical_journey", vertical_journey.router),
    ("billing", billing.router),
    ("commercial_launch", commercial_launch.router),
    ("controlled_beta", controlled_beta.router),
    ("consent", consent.router),
    ("consent_renewal", consent_renewal.router),
    ("content_factory", content_factory.router),
    ("content_review", content_review.router),
    ("content_quality", content_quality.router),
    ("irt_quality", irt_quality.router),
    ("admin_etl", admin_etl.router),
    ("popia", popia.router),
    ("privacy_operations", privacy_operations.router),
    ("security_assurance", security_assurance.router),
    ("observability_sre", observability_sre.router),
    ("performance_scale_cost", performance_scale_cost.router),
    ("production_release", production_release.router),
    ("jobs", jobs.router),
    ("system", system.router),
    ("learner_content", learner_content.router),
)

# ── Operational Routes ─────────────────────────────────────────────────────────

@app.get("/health", tags=["ops"])
async def health():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "mode": "v2-baseline",
    }


@app.get("/ready", tags=["ops"])
@app.get("/v2/health/deep", tags=["ops"])
@app.get("/api/v2/health/deep", tags=["ops"])
async def ready():
    # Perform deep health checks and return appropriate status.
    # 'ok' or 'degraded' returns 200, 'error' returns 503.
    health_data = await gather_deep_health()
    status_code = 200 if health_data["status"] in ("ok", "degraded") else 503
    return JSONResponse(status_code=status_code, content=health_data)


@app.get("/metrics", tags=["ops"], include_in_schema=False)
async def metrics(request: Request):
    """Prometheus scrape endpoint.

    Access control (7.7):
    - In production: only allow requests from the private network (RFC-1918
      ranges) or localhost. External traffic must be blocked at the infra
      layer (Nginx/ACA ingress) — this app-level check is a defence-in-depth
      fallback.
    - In non-production: open for local Prometheus/Grafana scraping.

    See ADR-027 for the full decision rationale.
    """
    if settings.is_production():
        client_ip = _metrics_client_ip(request)
        if not _is_private_metrics_client(client_ip):
            return Response(status_code=403, content=b"Forbidden")
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


@app.get("/", tags=["ops"])
async def root():
    return JSONResponse({"message": "EduBoost SA V2 — Ngiyabonga! 🦁", "docs": "/docs"})


# ── Router Registration ───────────────────────────────────────────────────────

for prefix in API_PREFIXES:
    for _router_name, router in ROUTER_REGISTRY:
        app.include_router(router, prefix=prefix)


# Dev-only helper to simulate a slow DB query for testing slow-query logging.
# Executes `pg_sleep(0.02)` via an AsyncSession; only enabled outside production.
@app.get("/__dev/slow_query", tags=["dev"])
async def dev_slow_query():
    if settings.is_production():
        return JSONResponse(status_code=404, content={"detail": "not found"})
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text

        async with AsyncSessionLocal() as session:
            # 0.02s sleep should exceed low thresholds like 0.01s
            await session.execute(text("SELECT pg_sleep(0.02)"))
        return JSONResponse({"status": "ok", "note": "executed pg_sleep(0.02)"})
    except Exception as exc:  # pragma: no cover - dev helper
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(exc)})
