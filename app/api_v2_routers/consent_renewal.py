"""
V2 Router — Consent Renewal Admin Endpoint  (Task #24)
======================================================
Exposes an Admin-only endpoint to trigger the consent renewal
reminder job on-demand (in addition to the daily arq schedule).
"""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v2/admin/consent", tags=["V2 Admin – Consent"])


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
    # Replace these stubs with real DI once the V2 dependency helpers are wired:
    # db: AsyncSession = Depends(get_async_db),
    # settings: V2Settings = Depends(get_v2_settings),
    # _: None = Depends(require_role("Admin")),
) -> ConsentRenewalResponse:
    """
    Queues the consent renewal reminder job as a FastAPI BackgroundTask.
    Returns 202 immediately; emails are dispatched asynchronously.

    Access: Admin role required (RBAC enforced via ``require_role("Admin")``
    dependency — wire once Task #15 RBAC is complete).
    """
    # Lazy import to avoid circular dependency at module load time.
    from app.core.config import get_v2_settings  # type: ignore[import]
    from app.core.database import get_async_db  # type: ignore[import]
    from app.services.consent_renewal_service import (
        ConsentRenewalService,
        SendGridEmailGateway,
    )

    settings = get_v2_settings()
    email_gateway = SendGridEmailGateway(settings)

    async def _run_job() -> None:
        # Each background task opens its own DB session to avoid
        # using a session that has already been closed by the request lifecycle.
        async for db in get_async_db():
            service = ConsentRenewalService(db, email_gateway, settings)
            await service.run()

    background_tasks.add_task(_run_job)

    return ConsentRenewalResponse(
        message="Consent renewal reminder job queued. Emails will be dispatched shortly."
    )
