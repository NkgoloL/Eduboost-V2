"""Deep runtime health checks for the V2 application."""
from __future__ import annotations

from typing import Any

import httpx
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.redis import get_redis


async def check_arq() -> dict[str, Any]:
    """Verify that the arq worker queue is responsive."""
    try:
        redis = get_redis()
        # arq stores queue metadata in redis. We check for connectivity.
        # A more robust check would involve checking the arq:health-check key if the worker is running.
        ping = await redis.ping()
        return {"status": "ok" if ping else "error", "queue": "default"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": str(exc)}


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
        "postgres": await check_postgres(),
        "redis": await check_redis(),
    }
    optional_checks = {
        "llm_provider": await check_llm_provider(),
        "judiciary": await check_judiciary(),
        "arq_worker": await check_arq(),
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
