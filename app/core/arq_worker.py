"""
arq Worker Settings — EduBoost V2
=================================
Configures the async worker for background jobs and cron schedules.
Run with: `arq app.core.arq_worker.WorkerSettings`
"""
from __future__ import annotations

import logging
from arq.connections import RedisSettings
from arq.cron import cron

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.jobs.consent_renewal_job import run_consent_renewal_reminders

logger = logging.getLogger(__name__)

async def on_startup(ctx: dict) -> None:
    """Initialize worker context."""
    logger.info("arq_worker_starting")
    ctx["settings"] = settings
    ctx["db_session_factory"] = AsyncSessionLocal
    logger.info("arq_worker_context_initialized")

async def on_shutdown(ctx: dict) -> None:
    """Cleanup worker context."""
    logger.info("arq_worker_shutting_down")

class WorkerSettings:
    """arq Worker configuration."""
    functions = [run_consent_renewal_reminders]
    cron_jobs = [
        # Daily consent renewal check at 08:00 SAST
        cron(run_consent_renewal_reminders, hour=8, minute=0, unique=True)
    ]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = on_startup
    on_shutdown = on_shutdown
    max_jobs = settings.ARQ_MAX_JOBS
    job_timeout = settings.ARQ_JOB_TIMEOUT
