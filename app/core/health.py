"""Deep runtime health checks for the V2 application."""
from __future__ import annotations

from typing import Any

import httpx
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.redis import get_redis


def _google_model_name() -> str:
    return settings.GOOGLE_MODEL.removeprefix("models/")


async def check_postgres() -> dict[str, Any]:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))

        # Update metrics
        from app.core.database import engine
        from app.core.metrics import db_pool_checkedout, db_pool_overflow, db_pool_size
        if hasattr(engine.pool, "checkedout"):
            db_pool_size.set(getattr(engine.pool, "size", lambda: 0)())
            db_pool_checkedout.set(engine.pool.checkedout())
            db_pool_overflow.set(engine.pool.overflow())

        return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": _safe_error(exc)}


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
        return {"status": "error", "detail": _safe_error(exc)}


async def check_llm_provider() -> dict[str, Any]:
    if not settings.GOOGLE_API_KEY and not settings.GROQ_API_KEY and not settings.ANTHROPIC_API_KEY:
        return {"status": "skipped", "detail": "No LLM provider credentials configured"}

    if settings.GOOGLE_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{_google_model_name()}",
                    headers={"x-goog-api-key": settings.GOOGLE_API_KEY},
                )
            response.raise_for_status()
            return {"status": "ok", "provider": "google", "model": _google_model_name()}
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "provider": "google", "detail": _safe_error(exc)}

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
            return {"status": "error", "provider": "groq", "detail": _safe_error(exc)}

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
        return {"status": "error", "provider": "anthropic", "detail": _safe_error(exc)}


async def check_required_secrets() -> dict[str, Any]:
    """Verify that essential runtime secrets/configuration are present."""
    missing: list[str] = []
    # Accept both legacy `JWT_SECRET` and `JWT_SECRET_KEY` names
    # If a JWT_SECRET_KEY attribute exists (legacy/compat), require it explicitly
    if hasattr(settings, "JWT_SECRET_KEY"):
        if not getattr(settings, "JWT_SECRET_KEY", None):
            missing.append("JWT_SECRET_KEY")
    else:
        if not getattr(settings, "JWT_SECRET", None):
            missing.append("JWT_SECRET")
    for name in ("DATABASE_URL", "REDIS_URL"):
        if not getattr(settings, name, None):
            missing.append(name)
    if missing:
        return {"status": "error", "detail": f"Missing: {', '.join(missing)}"}
    return {"status": "ok"}


async def check_migrations() -> dict[str, Any]:
    """Verify that alembic migrations have been applied (best-effort).

    Queries ``alembic_version`` and returns the active head revision.
    The sentinel value ``'base'`` is excluded because it is not a real
    migration revision — it is a placeholder that Alembic inserts when a
    database is stamped without running migrations.  When multiple rows
    exist (split-head state) a warning is included in the response so
    operators can investigate, but the check does not fail provided at
    least one real revision is present.
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text(
                    "SELECT version_num FROM alembic_version"
                    " WHERE version_num != 'base'"
                    " ORDER BY version_num DESC"
                    " LIMIT 10"
                )
            )
            rows = result.fetchall()
            if not rows:
                return {"status": "error", "detail": "alembic_version table empty or contains only sentinel 'base' row"}
            revisions = [r[0] for r in rows]
            result_dict: dict[str, Any] = {"status": "ok", "revision": revisions[0]}
            if len(revisions) > 1:
                result_dict["warning"] = f"Multiple revisions in alembic_version: {revisions}"
            return result_dict
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": _safe_error(exc)}


async def check_audit_repository() -> dict[str, Any]:
    """Verify audit repository accessibility (best-effort).

    If the audit table is missing or inaccessible, return an error detail
    rather than raising so readiness endpoints remain resilient.
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1 FROM audit_events LIMIT 1"))
        return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": _safe_error(exc)}


async def check_judiciary() -> dict[str, Any]:
    try:
        from app.core.judiciary import JudiciaryService

        service = JudiciaryService()
        service._assert_no_violations("safe classroom content")  # noqa: SLF001 - intentional health probe
        return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": _safe_error(exc)}


def _safe_error(exc: Exception) -> str:
    """Return a non-sensitive diagnostic string for health endpoints."""
    return exc.__class__.__name__


def _record_readiness_metrics(critical: dict[str, Any], optional: dict[str, Any]) -> None:
    from app.core.metrics import readiness_component_status

    for name, component in critical.items():
        readiness_component_status.labels(component=name, criticality="critical").set(
            1 if component.get("status") == "ok" else 0
        )
    for name, component in optional.items():
        readiness_component_status.labels(component=name, criticality="optional").set(
            1 if component.get("status") in {"ok", "skipped"} else 0
        )


async def gather_deep_health() -> dict[str, Any]:
    # Core critical checks that must be healthy for readiness
    critical_checks = {
        "secrets": await check_required_secrets(),
        "postgres": await check_postgres(),
        "redis": await check_redis(),
        "migrations": await check_migrations(),
        "audit_repository": await check_audit_repository(),
    }

    # Optional components that may degrade functionality but shouldn't block readiness
    optional_checks = {
        "llm_provider": await check_llm_provider(),
        "judiciary": await check_judiciary(),
    }

    overall = "ok"
    for component in critical_checks.values():
        if component.get("status") == "error":
            overall = "error"
            break

    if overall == "ok":
        for component in optional_checks.values():
            if component["status"] == "error":
                overall = "degraded"
                break

    _record_readiness_metrics(critical_checks, optional_checks)

    return {
        "status": overall,
        "critical": critical_checks,
        "optional": optional_checks,
        "message": (
            "System is operational"
            if overall == "ok"
            else "System is operational but in degraded mode"
            if overall == "degraded"
            else "System is unavailable"
        ),
    }
