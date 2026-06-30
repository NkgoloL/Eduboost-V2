"""
arq Worker Job — Daily Consent Renewal Reminder  (Task #24)
============================================================
Register this module in your arq WorkerSettings.functions list.

Example WorkerSettings (app/modules/jobs.py):
    from app.jobs.consent_renewal_job import run_consent_renewal_reminders

    class WorkerSettings:
        functions = [run_consent_renewal_reminders]
        cron_jobs = [
            cron(run_consent_renewal_reminders, hour=8, minute=0)
        ]
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.core.config import settings as app_settings
from app.core.database import AsyncSessionLocal
from app.core.jobs import update_job

if TYPE_CHECKING:
    pass  # type: ignore[import]

logger = logging.getLogger(__name__)


def _error_payload(exc: Exception) -> dict[str, str]:
    return {"type": exc.__class__.__name__, "message": str(exc)}


async def run_consent_renewal_reminders(ctx: dict | None = None, job_id: str | None = None) -> dict:
    """
    arq-compatible daily job.

    ``ctx`` is populated by arq with the worker context dict.
    We expect ``ctx["db_session_factory"]`` and ``ctx["settings"]``
    to be injected at worker startup (see arq WorkerSettings.on_startup).
    """
    from app.services.consent_renewal_service import (
        ConsentRenewalService,
        SendGridEmailGateway,
    )

    ctx = ctx or {}
    settings = ctx.get("settings") or app_settings
    session_factory = ctx.get("db_session_factory") or AsyncSessionLocal

    async def _run() -> dict:
        email_gateway = SendGridEmailGateway(settings)
        async with session_factory() as db:
            service = ConsentRenewalService(db, email_gateway, settings)
            stats = await service.run()
        logger.info("consent_renewal_job_finished", extra=stats)
        return stats

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
