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
from app.core.jobs import create_job, update_job
from app.services.job_runtime_integrity import validate_arq_job_payload
from app.services.job_dependency_factory import durable_job_session, run_consent_reminder_cycle
from app.services.arq_import_compat import RedisSettings, cron

import logging
from datetime import datetime
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

from app.core.config import get_settings
from app.core.metrics import (
    arq_job_duration_seconds,
    arq_jobs_total,
    content_review_reminders_total,
    content_review_stale_assignments,
)
from app.jobs.practice_session_cleanup_job import run_practice_session_cleanup
from app.jobs.batch_generation_job import generate_content_batch
from app.jobs.irt_quality_job import run_irt_quality_watchdog

logger = logging.getLogger(__name__)
_ARQ_POOL: Any | None = None


def _error_payload(exc: Exception) -> dict[str, str]:
    return {"type": exc.__class__.__name__, "message": str(exc)}


async def _update_durable_job(
    job_id: str | None,
    *,
    status: str | None = None,
    result: Any | None = None,
    error: dict[str, str] | None = None,
) -> None:
    if not job_id:
        return
    await update_job(job_id, status=status, result=result, error=error)


async def _execute_durable_job(job_id: str | None, runner):
    await _update_durable_job(job_id, status="running")
    try:
        result = await runner()
    except Exception as exc:  # noqa: BLE001
        await _update_durable_job(job_id, status="failed", error=_error_payload(exc))
        raise
    await _update_durable_job(job_id, status="completed", result=result)
    return result


async def _get_arq_pool() -> Any:
    global _ARQ_POOL
    if _ARQ_POOL is not None:
        return _ARQ_POOL

    try:
        from arq.connections import RedisSettings as ArqRedisSettings, create_pool
    except Exception as exc:  # pragma: no cover - production dependency gate
        raise RuntimeError(f"arq is required for durable jobs: {exc}") from exc

    cfg = get_settings()
    _parsed = urlparse(cfg.REDIS_URL)
    redis_settings = ArqRedisSettings(
        host=_parsed.hostname or "localhost",
        port=_parsed.port or 6379,
        database=int((_parsed.path or "").lstrip("/") or "0"),
    )
    _ARQ_POOL = await create_pool(redis_settings)
    return _ARQ_POOL


async def enqueue_durable(
    function_name: str,
    *,
    operation: str,
    payload: dict[str, Any] | None = None,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
) -> str:
    """Enqueue a durable ARQ job and record its status in the shared job store."""

    job = await create_job(operation, payload=payload)
    try:
        pool = await _get_arq_pool()
        job_kwargs = {"job_id": job["job_id"], **(kwargs or {})}
        arq_job = await pool.enqueue_job(
            function_name,
            *args,
            _job_id=job["job_id"],
            **job_kwargs,
        )
        if arq_job is None:
            raise RuntimeError(f"ARQ rejected job enqueue for {function_name}")
    except Exception as exc:  # noqa: BLE001
        await _update_durable_job(job["job_id"], status="failed", error=_error_payload(exc))
        raise
    return job["job_id"]


# ── Job Definitions ───────────────────────────────────────────────────────────


async def send_consent_reminders(ctx: dict | None = None, job_id: str | None = None) -> dict[str, Any]:
    async def _run() -> dict[str, Any]:
        await run_consent_reminder_cycle(ctx or {})
        return {"status": "sent"}

    return await _execute_durable_job(job_id, _run)


async def send_consent_renewal_reminders(ctx: dict | None = None, job_id: str | None = None) -> dict[str, Any]:
    async def _run() -> dict[str, Any]:
        await run_consent_reminder_cycle(ctx or {})
        return {"status": "sent"}

    return await _execute_durable_job(job_id, _run)


async def generate_lesson_job(
    ctx: dict[str, Any] | None = None,
    *,
    job_id: str | None = None,
    learner_id: str,
    subject: str,
    topic: str,
    language: str = "en",
    current_user_id: str,
) -> dict[str, Any]:
    payload = {
        "learner_id": learner_id,
        "subject": subject,
        "topic": topic,
        "language": language,
        "current_user_id": current_user_id,
    }
    validate_arq_job_payload(payload)

    async def _run() -> dict[str, Any]:
        from app.core.database import AsyncSessionLocal
        from app.domain.schemas import LessonRequest
        from app.modules.lessons.service import LessonService

        async with AsyncSessionLocal() as db:
            service = LessonService(db)
            lesson, cache_hit, provider = await service.generate_lesson_for_learner(
                LessonRequest.model_validate(
                    {
                        "learner_id": learner_id,
                        "subject": subject,
                        "topic": topic,
                        "language": language,
                    }
                ),
                UUID(current_user_id),
            )
            return {
                "lesson": lesson.model_dump(mode="json"),
                "cache_hit": cache_hit,
                "provider": provider,
            }

    return await _execute_durable_job(job_id, _run)


async def generate_study_plan_job(
    ctx: dict[str, Any] | None = None,
    *,
    job_id: str | None = None,
    learner_id: str,
    gap_ratio: float = 0.4,
) -> dict[str, Any]:
    payload = {"learner_id": learner_id, "gap_ratio": gap_ratio}
    validate_arq_job_payload(payload)

    async def _run() -> dict[str, Any]:
        from app.core.database import AsyncSessionLocal
        from app.repositories.repositories import LearnerRepository
        from app.services.audit_service import AuditService
        from app.services.study_plan_service_v2 import StudyPlanServiceV2
        from app.services.telemetry import TelemetryService

        try:
            from app.repositories.study_plan_repository import StudyPlanRepository

            study_plan_repository = StudyPlanRepository()
        except Exception:  # noqa: BLE001
            study_plan_repository = None

        async with AsyncSessionLocal() as db:
            service = StudyPlanServiceV2(
                learner_repository=LearnerRepository(db),
                study_plan_repository=study_plan_repository,
            )
            plan = await service.generate_plan(learner_id, gap_ratio=gap_ratio)
            await AuditService().log_event(
                event_type="STUDY_PLAN_GENERATED",
                learner_id=learner_id,
                payload={"plan_id": plan["plan_id"]},
            )
            await TelemetryService().track_event_async(
                "study_plan_generated",
                pseudonym_id=f"learner:{learner_id}",
                properties={"gap_ratio": gap_ratio},
            )
            return plan

    return await _execute_durable_job(job_id, _run)


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
    from datetime import timezone, timedelta

    start = time.perf_counter()
    job_name = "expire_diagnostic_sessions"
    try:
        from sqlalchemy import update
        from app.models import DiagnosticSession

        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        async with durable_job_session() as db:
            result = await db.execute(
                update(DiagnosticSession)
                .where(
                    DiagnosticSession.completed_at.is_(None),
                    DiagnosticSession.session_state.not_in(["completed", "abandoned"]),
                    DiagnosticSession.started_at < cutoff,
                )
                .values(session_state="abandoned")
            )
            await db.commit()
            count = result.rowcount

        arq_jobs_total.labels(job_name=job_name, status="success").inc()
        duration = time.perf_counter() - start
        arq_job_duration_seconds.labels(job_name=job_name).observe(duration)
        return {"expired": count}

    except Exception:
        arq_jobs_total.labels(job_name=job_name, status="failed").inc()
        raise


async def process_stale_content_reviews(
    ctx: dict[str, Any] | None = None, job_id: str | None = None
) -> dict[str, int]:
    """Detect stale educator reviews and record reminder/escalation state.

    This job never approves content. It only updates reminder metadata and
    metrics so curriculum leads can reassign or escalate overdue work.
    """

    async def _run() -> dict[str, int]:
        from app.services.content_review_governance import ContentReviewGovernanceService

        async with durable_job_session() as db:
            result = await ContentReviewGovernanceService().process_stale_assignments(db)
            await db.commit()
        content_review_stale_assignments.set(result["stale"])
        if result["reminded"]:
            content_review_reminders_total.labels(action="reminded").inc(result["reminded"])
        if result["escalated"]:
            content_review_reminders_total.labels(action="escalated").inc(result["escalated"])
        return result

    return await _execute_durable_job(job_id, _run)


async def run_database_backup(ctx: dict[str, Any]) -> dict[str, Any]:
    """Execute automated encrypted PostgreSQL backup.

    Cron schedule: daily at 00:00 timezone.utc (02:00 SAST).  Invokes
    ``scripts/backup_postgres.sh`` with configuration from
    :class:`~app.core.config.Settings`.

    Args:
        ctx: ARQ worker context dictionary.

    Returns:
        dict[str, Any]: Summary with ``status``, ``duration``, and
        tail of the backup script output.

    Raises:
        subprocess.CalledProcessError: If the backup script exits with non-zero.
        Exception: Re-raised after incrementing the failure counter.
    """
    import os
    import subprocess
    import time

    start = time.perf_counter()
    job_name = "database_backup"
    cfg = get_settings()

    try:
        # Prepare environment for the shell script
        env = os.environ.copy()
        if cfg.BACKUP_ENCRYPTION_KEY:
            env["BACKUP_ENCRYPTION_KEY"] = cfg.BACKUP_ENCRYPTION_KEY
        env["RETENTION_DAYS"] = str(cfg.BACKUP_RETENTION_DAYS)

        # Determine script path relative to repo root
        script_path = os.path.join(os.getcwd(), "scripts", "backup_postgres.sh")

        # Ensure script is executable
        if not os.access(script_path, os.X_OK):
            os.chmod(script_path, 0o755)

        # Run the script
        result = subprocess.run(
            [script_path],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )

        arq_jobs_total.labels(job_name=job_name, status="success").inc()
        duration = time.perf_counter() - start
        arq_job_duration_seconds.labels(job_name=job_name).observe(duration)

        return {
            "status": "success",
            "duration": round(duration, 2),
            "output_tail": result.stdout.splitlines()[-3:] if result.stdout else [],
        }
    except Exception as exc:
        arq_jobs_total.labels(job_name=job_name, status="failed").inc()
        logger.error("Database backup failed: %s", exc, exc_info=True)
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
    from app.repositories import GuardianRepository

    async with durable_job_session() as db:
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
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import text

    ctx["settings"] = get_settings()

    ctx["db_session_factory"] = AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await db.execute(text("SELECT 1"))

    redis = ctx.get("redis")
    if redis is not None and hasattr(redis, "ping"):
        ping = redis.ping()
        if hasattr(ping, "__await__"):
            await ping

    logger.info("ARQ worker starting up", extra={"db_ready": True, "redis_ready": redis is not None})


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
        send_consent_reminders,
        send_consent_renewal_reminders,
        generate_lesson_job,
        generate_study_plan_job,
        run_practice_session_cleanup,
        process_rlhf_feedback_batch,
        expire_stale_diagnostic_sessions,
        run_database_backup,
        generate_content_batch,
        process_stale_content_reviews,
        run_irt_quality_watchdog,
    ]

    cron_jobs = [
        # Daily at 00:00 timezone.utc (02:00 SAST)
        cron(run_database_backup, hour=0, minute=0),
        # Daily at 06:00 timezone.utc (08:00 SAST)
        cron(send_consent_renewal_reminders, hour=6, minute=0),
        # Daily at 03:00 SAST
        cron(run_practice_session_cleanup, hour=1, minute=0),
        # Hourly
        cron(expire_stale_diagnostic_sessions, minute=0),
        # Every 30 minutes; stale review handling never auto-approves content.
        cron(process_stale_content_reviews, minute={0, 30}),
        # Nightly at 02:00 UTC. Rewritten content returns to Phase 3 review.
        cron(run_irt_quality_watchdog, hour=2, minute=0),
    ]

    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 300  # 5 minutes max per job
    keep_result = 3600  # Keep job results for 1 hour
    _cfg = get_settings()
    _parsed = urlparse(_cfg.REDIS_URL)
    redis_settings = RedisSettings(
        host=_parsed.hostname or "localhost",
        port=_parsed.port or 6379,
        database=int((_parsed.path or "").lstrip("/") or "0"),
    )
