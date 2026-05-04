"""
EduBoost SA — ARQ Background Jobs
Async Redis Queue replacing Celery + Flower.
Integrates natively with asyncio and FastAPI.
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
    """
    Cron job: find consents expiring in ≤30 days and send guardian email reminders.
    Runs daily at 08:00 SAST.
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
    """
    Process a batch of RLHF lesson feedback for model improvement pipeline.
    Queued after feedback volume threshold is reached.
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
    """
    Cron job: mark incomplete diagnostic sessions older than 24h as abandoned.
    Runs hourly.
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
    """Send a consent renewal reminder via SendGrid."""
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
    logger.info("ARQ worker starting up")


async def shutdown(ctx: dict[str, Any]) -> None:
    logger.info("ARQ worker shutting down")


class WorkerSettings:
    """ARQ worker configuration — replace Celery/Flower."""
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
        cfg = get_settings()
        # Parse redis://host:port/db
        import urllib.parse
        parsed = urllib.parse.urlparse(cfg.redis_url)
        return RedisSettings(
            host=parsed.hostname or "localhost",
            port=parsed.port or 6379,
            database=int(parsed.path.lstrip("/") or "0"),
        )
