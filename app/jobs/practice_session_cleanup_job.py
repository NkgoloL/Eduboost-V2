"""
arq Worker Job — Practice Session Cleanup (Phase 2.2)
======================================================
Periodically deletes expired practice sessions to maintain database hygiene.

Register this module in your arq WorkerSettings.functions list:

Example WorkerSettings (app/modules/jobs.py):
    from app.jobs.practice_session_cleanup_job import run_practice_session_cleanup

    class WorkerSettings:
        functions = [run_practice_session_cleanup]
        cron_jobs = [
            cron(run_practice_session_cleanup, hour=3, minute=0)  # 3 AM daily
        ]
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.core.database import AsyncSessionLocal
from app.core.jobs import update_job

if TYPE_CHECKING:
    pass  # type: ignore[import]

logger = logging.getLogger(__name__)


def _error_payload(exc: Exception) -> dict[str, str]:
    return {"type": exc.__class__.__name__, "message": str(exc)}


async def run_practice_session_cleanup(ctx: dict | None = None, job_id: str | None = None) -> dict:
    """
    arq-compatible daily job for deleting expired practice sessions.

    ``ctx`` is populated by arq with the worker context dict.
    We expect ``ctx["db_session_factory"]`` to be injected at worker startup.
    """
    from app.repositories.practice_session_repository import PracticeSessionRepository

    ctx = ctx or {}
    session_factory = ctx.get("db_session_factory") or AsyncSessionLocal

    async def _run() -> dict:
        async with session_factory() as db:
            repo = PracticeSessionRepository(db)
            deleted_count = await repo.delete_expired()
            logger.info(
                "practice_session_cleanup_completed",
                extra={"deleted_count": deleted_count},
            )
            return {"deleted_count": deleted_count}

    if job_id:
        await update_job(job_id, status="running")
    try:
        result = await _run()
    except Exception as exc:  # noqa: BLE001
        if job_id:
            await update_job(job_id, status="failed", error=_error_payload(exc))
        raise
    if job_id:
        await update_job(job_id, status="completed", result=result)
    return result
