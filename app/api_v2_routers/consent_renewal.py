"""
V2 Router — Consent Renewal Admin Endpoint  (Task #24)
======================================================
Exposes an Admin-only endpoint to trigger the consent renewal
reminder job on-demand (in addition to the daily arq schedule).
"""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.jobs import enqueue_job
from app.core.security import require_admin
from app.domain.api_v2_models import JobAcceptedResponse
from app.services.consent_renewal_service import ConsentRenewalService, SendGridEmailGateway

router = APIRouter(prefix="/admin/consent", tags=["V2 Admin – Consent"])


@router.post(
    "/trigger-renewal-reminders",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger POPIA consent renewal reminder emails (Admin only)",
)
async def trigger_renewal_reminders(
    background_tasks: BackgroundTasks,
    _: dict = Depends(require_admin),
) -> JobAcceptedResponse:
    """
    Queues the consent renewal reminder job as a FastAPI BackgroundTask.
    Returns 202 immediately; emails are dispatched asynchronously.

    Access: Admin role required (RBAC enforced via ``require_role("Admin")``
    dependency — wire once Task #15 RBAC is complete).
    """
    async def _run_job() -> dict:
        async with AsyncSessionLocal() as db:
            email_gateway = SendGridEmailGateway(settings)
            service = ConsentRenewalService(db, email_gateway, settings)
            return await service.run()

    job = await enqueue_job(
        background_tasks,
        operation="consent_renewal_reminders",
        handler=_run_job,
    )
    return JobAcceptedResponse(job_id=job["job_id"], operation=job["operation"], status=job["status"])
