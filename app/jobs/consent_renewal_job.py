"""
arq Worker Job — Daily Consent Renewal Reminder  (Task #24)
============================================================
Register this module in your arq WorkerSettings.functions list.

Example WorkerSettings (app/core/arq_worker.py):
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

if TYPE_CHECKING:
    from arq.connections import ArqRedis  # type: ignore[import]

logger = logging.getLogger(__name__)


async def run_consent_renewal_reminders(ctx: dict) -> dict:
    """
    arq-compatible daily job.

    ``ctx`` is populated by arq with the worker context dict.
    We expect ``ctx["db_session_factory"]`` and ``ctx["settings"]``
    to be injected at worker startup (see arq WorkerSettings.on_startup).
    """
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.services.consent_renewal_service import (
        ConsentRenewalService,
        SendGridEmailGateway,
    )

    settings = ctx.get("settings")
    session_factory = ctx.get("db_session_factory")

    if settings is None or session_factory is None:
        logger.error(
            "consent_renewal_job_misconfigured",
            extra={"missing": [k for k in ("settings", "db_session_factory") if ctx.get(k) is None]},
        )
        return {"error": "Worker context missing required keys"}

    email_gateway = SendGridEmailGateway(settings)

    async with session_factory() as db:
        service = ConsentRenewalService(db, email_gateway, settings)
        stats = await service.run()

    logger.info("consent_renewal_job_finished", extra=stats)
    return stats
