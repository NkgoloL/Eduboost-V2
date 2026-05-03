"""
V2 Router — Consent Renewal Admin Endpoint  (Task #24)
======================================================
Exposes an Admin-only endpoint to trigger the consent renewal
reminder job on-demand (in addition to the daily arq schedule).
"""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import require_admin

router = APIRouter(prefix="/admin/consent", tags=["V2 Admin – Consent"])


class ConsentRenewalResponse(BaseModel):
    message: str
    job: str = "consent_renewal_reminder"


@router.post(
    "/trigger-renewal-reminders",
    response_model=ConsentRenewalResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger POPIA consent renewal reminder emails (Admin only)",
)
async def trigger_renewal_reminders(
    background_tasks: BackgroundTasks,
    _: dict = Depends(require_admin),
) -> ConsentRenewalResponse:
    """
    Queues the consent renewal reminder job as a FastAPI BackgroundTask.
    Returns 202 immediately; emails are dispatched asynchronously.

    Access: Admin role required (RBAC enforced via ``require_role("Admin")``
    dependency — wire once Task #15 RBAC is complete).
    """
    from app.services.consent_renewal_service import (
        ConsentRenewalService,
        SendGridEmailGateway,
    )

    email_gateway = SendGridEmailGateway(settings)

    async def _run_job() -> None:
        async with AsyncSessionLocal() as db:
            service = ConsentRenewalService(db, email_gateway, settings)
            await service.run()

    background_tasks.add_task(_run_job)

    return ConsentRenewalResponse(
        message="Consent renewal reminder job queued. Emails will be dispatched shortly."
    )
