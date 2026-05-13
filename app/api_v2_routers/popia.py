"""EduBoost V2 — POPIA Compliance Router."""
from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from app.core.envelope_route import EnvelopedRoute
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.core.jobs import enqueue_job
from app.core.security import get_current_user, require_parent_or_admin
from app.domain.api_v2_models import JobAcceptedResponse, RLHFExportRequest
from app.models import LearnerProfile
from app.repositories.repositories import LearnerRepository
from app.security.dependencies import require_active_consent_for_current_user, require_learner_read_for_current_user
from app.security.dependencies import require_learner_write_for_current_user
from app.services.fourth_estate import FourthEstateService
from app.services.popia_service import POPIA_ERASURE_GRACE_DAYS, POPIADataRightsService
from app.services.rlhf_service import RLHFService

router = APIRouter(route_class=EnvelopedRoute, prefix="/popia", tags=["compliance"])


class ErasureRequest(BaseModel):
    reason: str = Field(default="guardian_request", min_length=3, max_length=200)


class CorrectionRequest(BaseModel):
    fields: dict[str, Any] = Field(default_factory=dict)
    reason: str = Field(min_length=3, max_length=300)


class RestrictionRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=300)


@router.get("/data-export/{learner_id}")
async def export_learner_data(
    learner_id: str,
    export_format: Literal["json", "csv"] = "json",
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """POPIA right-to-access export for an authorised learner."""
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
    await require_active_consent_for_current_user(db, current_user, learner_id)
    return await POPIADataRightsService(db).build_learner_export(
        learner_id,
        current_user,
        export_format=export_format,
    )


@router.post("/deletion-request/{learner_id}")
async def request_learner_deletion(
    learner_id: str,
    body: ErasureRequest | None = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Request POPIA erasure with audit-retention exceptions preserved."""
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_write_for_current_user(current_user, learner_id)
    result = await POPIADataRightsService(db).request_erasure(
        learner_id,
        current_user,
        reason=(body.reason if body else "guardian_request"),
    )
    await db.commit()
    return {
        "detail": "Erasure request submitted. Learner data processing is restricted immediately.",
        "grace_period_days": POPIA_ERASURE_GRACE_DAYS,
        **result,
    }


@router.post("/deletion-cancel/{learner_id}")
async def cancel_learner_deletion(
    learner_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a pending POPIA erasure request."""
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_write_for_current_user(current_user, learner_id)
    result = await POPIADataRightsService(db).cancel_erasure(learner_id, current_user)
    await db.commit()
    return {"detail": "Erasure request cancelled. Learner profile restored.", **result}


@router.post("/correction-request/{learner_id}")
async def request_correction(
    learner_id: str,
    body: CorrectionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Correct inaccurate learner personal information."""
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_write_for_current_user(current_user, learner_id)
    result = await POPIADataRightsService(db).request_correction(
        learner_id,
        current_user,
        body.fields,
        reason=body.reason,
    )
    await db.commit()
    return {"detail": "Correction request completed for supported fields.", **result}


@router.post("/restriction-request/{learner_id}")
async def request_processing_restriction(
    learner_id: str,
    body: RestrictionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Restrict learner processing by withdrawing active consent."""
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_write_for_current_user(current_user, learner_id)
    result = await POPIADataRightsService(db).restrict_processing(
        learner_id,
        current_user,
        reason=body.reason,
    )
    await db.commit()
    return {"detail": "Processing restriction accepted. Active consent was withdrawn.", **result}


@router.post("/deletion-execute/{learner_id}", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def execute_learner_deletion(
    learner_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_parent_or_admin),
):
    require_learner_write_for_current_user(current_user, learner_id)

    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            learner = await db.get(LearnerProfile, learner_id)
            if learner is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
            role = str(current_user.get("role", "")).lower()
            if learner.guardian_id != current_user.get("sub") and role != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to purge this learner")
            learner_pseudonym = learner.pseudonym_id
            await LearnerRepository(db).purge_personal_data(learner_id)
            await FourthEstateService(db).record(
                event_type="erasure.executed",
                learner_pseudonym=learner_pseudonym,
                actor_id=current_user.get("sub"),
                resource_id=learner_id,
                constitutional_outcome="APPROVED",
                payload={"learner_id": learner_id, "preserve_audit_records": True},
            )
            await db.commit()
            return {"learner_id": learner_id, "purged": True, "audit_records_preserved": True}

    job = await enqueue_job(
        background_tasks,
        operation="popia_data_purge",
        payload={"learner_id": learner_id},
        handler=_run,
    )
    return JobAcceptedResponse(job_id=job["job_id"], operation=job["operation"], status=job["status"])


@router.get("/deletion-status/{learner_id}")
async def get_deletion_status(
    learner_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
    if learner.deletion_requested_at is None:
        return {"learner_id": learner_id, "deletion_pending": False, "is_deleted": False}
    from datetime import UTC, datetime, timedelta

    grace_period_end = learner.deletion_requested_at + timedelta(days=POPIA_ERASURE_GRACE_DAYS)
    days_remaining = max((grace_period_end - datetime.now(UTC)).days, 0)
    return {
        "learner_id": learner_id,
        "deletion_pending": True,
        "is_deleted": learner.is_deleted,
        "requested_at": learner.deletion_requested_at.isoformat(),
        "days_remaining": days_remaining,
    }


@router.post("/rlhf-export/{export_format}", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def export_rlhf_dataset(
    export_format: str,
    body: RLHFExportRequest,
    background_tasks: BackgroundTasks,
    _: dict = Depends(require_parent_or_admin),
):
    export_format = export_format.lower()
    if export_format not in {"openai", "anthropic"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported export format")

    async def _run() -> dict:
        service = RLHFService()
        if export_format == "openai":
            return service.export_openai_format(body.records)
        return service.export_anthropic_format(body.records)

    job = await enqueue_job(
        background_tasks,
        operation="rlhf_export",
        payload={"format": export_format, "record_count": len(body.records)},
        handler=_run,
    )
    return JobAcceptedResponse(job_id=job["job_id"], operation=job["operation"], status=job["status"])
