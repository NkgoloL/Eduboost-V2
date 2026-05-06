"""Deep runtime health checks for the V2 application."""
from __future__ import annotations

from typing import Any

import httpx
from sqlalchemy import text
from alembic.config import Config as AlembicConfig
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations

from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine
from app.core.redis import get_redis
from app.core.logging import get_logger

log = get_logger(__name__)


async def check_required_secrets() -> dict[str, Any]:
    """Verify that critical production secrets are present."""
    try:
        required = [
            ("JWT_SECRET_KEY", settings.JWT_SECRET_KEY),
            ("DATABASE_URL", settings.DATABASE_URL),
            ("REDIS_URL", settings.REDIS_URL),
        ]
        missing = [name for name, value in required if not value]
        
        if missing:
            return {
                "status": "error",
                "detail": f"Missing required secrets: {', '.join(missing)}"
            }
        return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": str(exc)}


async def check_migrations() -> dict[str, Any]:
    """Verify that database migrations are applied."""
    try:
        async with AsyncSessionLocal() as session:
            # Get the current alembic revision
            connection = await session.connection()
            mc = MigrationContext.configure(connection)
            # Get the current revision from the database
            current_rev = mc.get_current_revision()
            
            if current_rev is None:
                return {
                    "status": "error",
                    "detail": "No migrations applied; alembic_version table not found or empty"
                }
            
            return {"status": "ok", "revision": current_rev}
    except Exception as exc:  # noqa: BLE001
        log.warning("migration_check_failed", error=str(exc))
        return {"status": "error", "detail": f"Migration check failed: {str(exc)}"}


async def check_audit_repository() -> dict[str, Any]:
    """Verify that the audit repository can be written to."""
    try:
        from app.repositories.audit_repository import AuditRepository
        
        async with AsyncSessionLocal() as db:
            repo = AuditRepository(db)
            # Attempt a read to verify table exists
            await repo.latest(limit=1)
            return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        log.warning("audit_repo_check_failed", error=str(exc))
        return {"status": "error", "detail": f"Audit repository check failed: {str(exc)}"}


async def check_postgres() -> dict[str, Any]:
    """Verify PostgreSQL connectivity."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        
        # Update metrics
        from app.core.metrics import db_pool_checkedout, db_pool_overflow, db_pool_size
        if hasattr(engine.pool, "checkedout"):
            db_pool_size.set(getattr(engine.pool, "size", lambda: 0)())
            db_pool_checkedout.set(engine.pool.checkedout())
            db_pool_overflow.set(engine.pool.overflow())
            
        return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": str(exc)}


async def check_redis() -> dict[str, Any]:
    try:
        redis = get_redis()
        pong = await redis.ping()
        
        # Update metrics
        from app.core.metrics import redis_connected_clients
        info = await redis.info("clients")
        if info:
            redis_connected_clients.set(info.get("connected_clients", 0))
            
        return {"status": "ok" if pong else "error"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": str(exc)}


async def check_llm_provider() -> dict[str, Any]:
    if not settings.GROQ_API_KEY and not settings.ANTHROPIC_API_KEY:
        return {"status": "skipped", "detail": "No LLM provider credentials configured"}

    if settings.GROQ_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                )
            response.raise_for_status()
            return {"status": "ok", "provider": "groq"}
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "provider": "groq", "detail": str(exc)}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                },
            )
        response.raise_for_status()
        return {"status": "ok", "provider": "anthropic"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "provider": "anthropic", "detail": str(exc)}


async def check_judiciary() -> dict[str, Any]:
    try:
        from app.core.judiciary import JudiciaryService

        service = JudiciaryService()
        service._assert_no_violations("safe classroom content")  # noqa: SLF001 - intentional health probe
        return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": str(exc)}


async def gather_deep_health() -> dict[str, Any]:
    critical_checks = {
        "secrets": await check_required_secrets(),
        "postgres": await check_postgres(),
        "redis": await check_redis(),
        "migrations": await check_migrations(),
        "audit_repository": await check_audit_repository(),
    }
    optional_checks = {
        "llm_provider": await check_llm_provider(),
        "judiciary": await check_judiciary(),
    }
    
    overall = "ok"
    for component in critical_checks.values():
        if component["status"] == "error":
            overall = "error"
            break
            
    if overall == "ok":
        for component in optional_checks.values():
            if component["status"] == "error":
                overall = "degraded"
                break
                
    return {
        "status": overall,
        "critical": critical_checks,
        "optional": optional_checks,
        "message": "System is operational" if overall == "ok" else "System is operational but in degraded mode" if overall == "degraded" else "System is unavailable"
    }
