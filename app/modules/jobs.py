"""ARQ background job definitions for EduBoost.

Async Redis Queue (ARQ) jobs replacing Celery + Flower.  All jobs
integrate natively with ``asyncio`` and FastAPI and are instrumented
with Prometheus counters via :mod:`app.core.metrics`.

Registered jobs:

* :func:`send_consent_renewal_reminders` — daily cron at 08:00 SAST.
* :func:`process_rlhf_feedback_batch` — queued on-demand.
* :func:`expire_stale_diagnostic_sessions` — hourly cron.

Example:
    Enqueue an RLHF batch manually::

        from arq.connections import ArqRedis

        redis = ArqRedis(...)
        await redis.enqueue_job(
            "process_rlhf_feedback_batch", "batch-42",
        )
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from arq import cron  # type: ignore[import-untyped]
from arq.connections import RedisSettings  # type: ignore[import-untyped]

from app.core.config import get_settings
from app.core.metrics import arq_job_duration_seconds, arq_jobs_total

logger = logging.getLogger(__name__)


# ── Job Definitions ───────────────────────────────────────────────────────────

async def send_consent_renewal_reminders(ctx: dict[str, Any]) -> dict[str, Any]:
    """Send email reminders for consents expiring within 30 days.

    Cron schedule: daily at 06:00 UTC (08:00 SAST).  Queries
    :meth:`~app.modules.consent.service.ConsentService.get_expiring_consents`
    and sends a renewal email to each guardian via SendGrid.

    Args:
        ctx: ARQ worker context dictionary.

    Returns:
        dict[str, Any]: Summary with keys ``sent`` (emails dispatched)
        and ``total_expiring`` (consents found).

    Raises:
        Exception: Re-raised after incrementing the failure counter.
    """
    import time
    start = time.perf_counter()
    job_name = "consent_renewal_reminders"

    try:
        from app.core.database import AsyncSessionLocal
        from app.modules.consent.service import ConsentService

        consent_service = ConsentService()
        async with AsyncSessionLocal() as db:
            expiring = await consent_service.get_expiring_consents(db, days=30)

        sent = 0
        for consent in expiring:
            try:
                await _send_renewal_email(consent)
                sent += 1
            except Exception as e:
                logger.warning("Failed to send renewal email for consent %s: %s", consent.id, e)

        arq_jobs_total.labels(job_name=job_name, status="success").inc()
        duration = time.perf_counter() - start
        arq_job_duration_seconds.labels(job_name=job_name).observe(duration)
        return {"sent": sent, "total_expiring": len(expiring)}

    except Exception as exc:
        arq_jobs_total.labels(job_name=job_name, status="failed").inc()
        logger.error("Job %s failed: %s", job_name, exc, exc_info=True)
        raise


async def process_rlhf_feedback_batch(ctx: dict[str, Any], batch_id: str) -> dict[str, Any]:
    """Process a batch of RLHF lesson feedback for model improvement.

    Queued on-demand after the feedback volume threshold is reached.
    Exports the batch to Azure Blob Storage for offline training.

    Args:
        ctx: ARQ worker context dictionary.
        batch_id: Unique identifier for the feedback batch to process.

    Returns:
        dict[str, Any]: Summary with keys ``batch_id`` and ``status``.

    Raises:
        Exception: Re-raised after incrementing the failure counter.
    """
    import time
    start = time.perf_counter()
    job_name = "rlhf_feedback_batch"

    try:
        logger.info("Processing RLHF feedback batch %s", batch_id)
        # Placeholder: export feedback to Azure Blob Storage for offline training
        arq_jobs_total.labels(job_name=job_name, status="success").inc()
        duration = time.perf_counter() - start
        arq_job_duration_seconds.labels(job_name=job_name).observe(duration)
        return {"batch_id": batch_id, "status": "exported"}

    except Exception as exc:
        arq_jobs_total.labels(job_name=job_name, status="failed").inc()
        logger.error("Job %s failed: %s", job_name, exc, exc_info=True)
        raise


async def expire_stale_diagnostic_sessions(ctx: dict[str, Any]) -> dict[str, Any]:
    """Mark incomplete diagnostic sessions older than 24 h as abandoned.

    Cron schedule: hourly at minute 0.  Updates
    :class:`~app.models.DiagnosticSession` records whose
    ``started_at`` timestamp is more than 24 hours in the past.

    Args:
        ctx: ARQ worker context dictionary.

    Returns:
        dict[str, Any]: Summary with key ``expired`` (number of
        sessions marked complete).

    Raises:
        Exception: Re-raised after incrementing the failure counter.
    """
    import time
    from datetime import UTC, timedelta

    start = time.perf_counter()
    job_name = "expire_diagnostic_sessions"
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import update
        from app.models import DiagnosticSession

        cutoff = datetime.now(UTC) - timedelta(hours=24)
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                update(DiagnosticSession)
                .where(
                    DiagnosticSession.is_complete == False,  # noqa: E712
                    DiagnosticSession.started_at < cutoff,
                )
                .values(is_complete=True)
            )
            await db.commit()
            count = result.rowcount

        arq_jobs_total.labels(job_name=job_name, status="success").inc()
        duration = time.perf_counter() - start
        arq_job_duration_seconds.labels(job_name=job_name).observe(duration)
        return {"expired": count}

    except Exception as exc:
        arq_jobs_total.labels(job_name=job_name, status="failed").inc()
        raise


async def _send_renewal_email(consent: Any) -> None:
    """Send a consent renewal reminder email via SendGrid.

    Decrypts the guardian's email using
    :func:`~app.core.security.decrypt_pii` before sending.  Silently
    returns if SendGrid is not configured.

    Args:
        consent: A :class:`~app.models.ParentalConsent` record with
            ``guardian_id`` and ``expires_at`` attributes.
    """
    cfg = get_settings()
    if not cfg.sendgrid_api_key:
        logger.warning("SendGrid not configured — skipping renewal email")
        return

    from sendgrid import SendGridAPIClient  # type: ignore[import-untyped]
    from sendgrid.helpers.mail import Mail  # type: ignore[import-untyped]

    # Guardian email is encrypted — must decrypt before sending
    from app.core.security import decrypt_pii
    from app.core.database import AsyncSessionLocal
    from app.repositories import GuardianRepository

    async with AsyncSessionLocal() as db:
        guardian_repo = GuardianRepository()
        guardian = await guardian_repo.get(consent.guardian_id, db)
        if not guardian:
            return
        email = decrypt_pii(guardian.email_encrypted)

    message = Mail(
        from_email=(cfg.sendgrid_from_email, cfg.sendgrid_from_name),
        to_emails=email,
        subject="EduBoost: Your child's consent is expiring soon",
        html_content=(
            f"<p>Your consent for your child's EduBoost account expires on "
            f"{consent.expires_at.strftime('%d %B %Y')}.</p>"
            f"<p>Please log in to the <a href='https://eduboost.co.za/parent-portal'>Parent Portal</a> "
            f"to renew consent and ensure uninterrupted access.</p>"
        ),
    )
    sg = SendGridAPIClient(cfg.sendgrid_api_key)
    sg.send(message)


# ── Worker Settings ───────────────────────────────────────────────────────────

async def startup(ctx: dict[str, Any]) -> None:
    """Log worker startup events.

    Args:
        ctx: ARQ worker context dictionary.
    """
    logger.info("ARQ worker starting up")


async def shutdown(ctx: dict[str, Any]) -> None:
    """Log worker shutdown events.

    Args:
        ctx: ARQ worker context dictionary.
    """
    logger.info("ARQ worker shutting down")


class WorkerSettings:
    """ARQ worker configuration — replaces Celery + Flower.

    Registers all background job functions, cron schedules, and
    connection settings for the Redis-backed async worker.

    Attributes:
        functions: List of registered async job callables.
        cron_jobs: Scheduled cron job definitions.
        on_startup: Coroutine called when the worker starts.
        on_shutdown: Coroutine called when the worker stops.
        max_jobs: Maximum concurrent jobs (default ``10``).
        job_timeout: Per-job timeout in seconds (default ``300``).
        keep_result: Seconds to retain job results (default ``3600``).
    """
    functions = [
        send_consent_renewal_reminders,
        process_rlhf_feedback_batch,
        expire_stale_diagnostic_sessions,
    ]

    cron_jobs = [
        # Daily at 06:00 UTC (08:00 SAST)
        cron(send_consent_renewal_reminders, hour=6, minute=0),
        # Hourly
        cron(expire_stale_diagnostic_sessions, minute=0),
    ]

    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 300  # 5 minutes max per job
    keep_result = 3600  # Keep job results for 1 hour

    @classmethod
    def redis_settings(cls) -> RedisSettings:
        """Build Redis connection settings from application configuration.

        Returns:
            RedisSettings instance configured from the project's redis URL.
        """
        cfg = get_settings()
        # Parse redis://host:port/db
        import urllib.parse
        parsed = urllib.parse.urlparse(cfg.redis_url)
        return RedisSettings(
            host=parsed.hostname or "localhost",
            port=parsed.port or 6379,
            database=int(parsed.path.lstrip("/") or "0"),
        )
