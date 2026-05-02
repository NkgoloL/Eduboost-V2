"""
EduBoost SA — FastAPI V2 Application Entrypoint
Single modular monolith. No legacy V1 code.
"""
from __future__ import annotations

import logging
import logging.config
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler  # type: ignore[import-untyped]
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.metrics import make_metrics_app
from app.core.middleware import (
    RequestIDMiddleware,
    StructuredLoggingMiddleware,
    TimingMiddleware,
)

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    cfg = get_settings()
    logger.info("EduBoost V2 starting — env=%s", cfg.app_env)

    # Verify DB connectivity on startup
    try:
        from sqlalchemy import text
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        logger.info("Database connection: OK")
    except Exception as exc:
        logger.error("Database connection failed: %s", exc)

    yield

    logger.info("EduBoost V2 shutting down")


# ── App Factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    cfg = get_settings()

    app = FastAPI(
        title=cfg.app_name,
        version=cfg.app_version,
        description=(
            "EduBoost SA — AI-powered adaptive learning platform. "
            "POPIA-compliant. CAPS-aligned. Multilingual."
        ),
        docs_url="/docs" if not cfg.is_production() else None,
        redoc_url="/redoc" if not cfg.is_production() else None,
        openapi_url="/openapi.json" if not cfg.is_production() else None,
        lifespan=lifespan,
    )

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    limiter = Limiter(key_func=get_remote_address, default_limits=[cfg.rate_limit_default])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_middleware(SlowAPIMiddleware)

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=cfg.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom Middleware (order: outermost first) ─────────────────────────────
    app.add_middleware(StructuredLoggingMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # ── Exception Handlers ────────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ───────────────────────────────────────────────────────────────
    from app.api_v2_routers.auth import router as auth_router
    from app.api_v2_routers.consent import router as consent_router
    from app.api_v2_routers.lessons import router as lessons_router

    API_PREFIX = "/v2"
    app.include_router(auth_router, prefix=API_PREFIX)
    app.include_router(consent_router, prefix=API_PREFIX)
    app.include_router(lessons_router, prefix=API_PREFIX)

    # ── Health & Metrics ──────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health() -> dict:
        return {"status": "ok", "version": cfg.app_version, "env": cfg.app_env}

    @app.get("/ready", tags=["Health"], include_in_schema=False)
    async def readiness() -> dict:
        """Kubernetes / ACA readiness probe — checks DB connectivity."""
        try:
            from sqlalchemy import text
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                await db.execute(text("SELECT 1"))
            return {"status": "ready"}
        except Exception as exc:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail=f"DB unavailable: {exc}")

    # Mount Prometheus metrics endpoint
    app.mount(cfg.prometheus_metrics_path, make_metrics_app())

    return app


app = create_app()
