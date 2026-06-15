"""Durable Phase 4 IRT calibration job."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.services.irt_quality_service import IRTQualityService


async def run_irt_quality_watchdog(
    ctx: dict[str, Any] | None = None,
    *,
    job_id: str | None = None,
    dry_run: bool = False,
    item_ids: list[str] | None = None,
    idempotency_key: str | None = None,
    actor_id: str = "irt-watchdog",
) -> dict[str, Any]:
    """Calibrate eligible diagnostic items; never auto-publish rewritten content."""
    from app.modules.jobs import _execute_durable_job

    async def _run() -> dict[str, Any]:
        parsed_ids = [UUID(value) for value in item_ids] if item_ids else None
        key = idempotency_key or f"scheduled:{datetime.now(UTC).date().isoformat()}:{actor_id}"
        async with AsyncSessionLocal() as db:
            return await IRTQualityService().run(
                db,
                dry_run=dry_run,
                item_ids=parsed_ids,
                idempotency_key=key,
                actor_id=actor_id,
            )

    return await _execute_durable_job(job_id, _run)
