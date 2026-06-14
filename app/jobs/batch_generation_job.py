"""Durable ARQ entrypoint for Phase 1 batch generation."""
from __future__ import annotations

import uuid
from typing import Any

import structlog

from app.core.config import get_settings
from app.core.database import AsyncSessionFactory
from app.services.batch_generation import BatchGenerationEngine
from app.services.llm_provider import build_provider_router

log = structlog.get_logger(__name__)


async def generate_content_batch(
    ctx: dict[str, Any],
    run_id: str,
    *,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Process a persisted run using server-resolved source records.

    Source text is intentionally not accepted in the queue payload. Each task
    stores approved source chunk identifiers, and the worker resolves them from
    the database before generation.
    """
    worker_id = f"arq-worker:{ctx.get('job_id', str(uuid.uuid4()))}"
    log.info(
        "generate_content_batch_started",
        run_id=run_id,
        job_id=job_id,
        worker_id=worker_id,
    )
    router = build_provider_router(get_settings())
    engine = BatchGenerationEngine(provider_router=router)
    async with AsyncSessionFactory() as db:
        result = await engine.process_run(
            uuid.UUID(run_id),
            None,
            db,
            worker_id=worker_id,
        )
    outcome = {
        "run_id": run_id,
        "succeeded": result.succeeded,
        "failed": result.failed,
        "safety_blocked": result.safety_blocked,
        "skipped": result.skipped,
        "total_tasks": result.total_tasks,
    }
    log.info("generate_content_batch_completed", **outcome)
    return outcome
