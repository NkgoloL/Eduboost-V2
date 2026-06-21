"""
V2 Router — Consent Renewal Admin Endpoint  (Task #24)
======================================================
Exposes an Admin-only endpoint to trigger the consent renewal
reminder job on-demand (in addition to the daily arq schedule).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api_v2_deps.auth import AuthContext, require_admin
from app.core.envelope_route import EnvelopedRoute

from app.domain.api_v2_models import JobAcceptedResponse
from app.modules.jobs import enqueue_durable

router = APIRouter(route_class=EnvelopedRoute, prefix="/admin/consent", tags=["V2 Admin – Consent"])


@router.post(
    "/trigger-renewal-reminders",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger POPIA consent renewal reminder emails (Admin only)",
)
async def trigger_renewal_reminders(
    _: AuthContext = Depends(require_admin),
) -> JobAcceptedResponse:
    """
    Queues the consent renewal reminder job on the durable ARQ worker.
    Returns 202 immediately; emails are dispatched asynchronously.

    Access: Admin role required (RBAC enforced via ``require_role("Admin")``
    dependency — wire once Task #15 RBAC is complete).
    """
    job_id = await enqueue_durable(
        "send_consent_renewal_reminders",
        operation="consent_renewal_reminders",
        payload={},
    )
    return JobAcceptedResponse(job_id=job_id, operation="consent_renewal_reminders", status="queued")
