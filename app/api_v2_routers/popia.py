"""
EduBoost V2 — POPIA Compliance Router
Right-to-access (data export) and right-to-erasure (deletion request) endpoints.
South African Protection of Personal Information Act compliance.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from io import BytesIO

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.database import AsyncSessionLocal
from app.core.jobs import enqueue_job
from app.core.security import get_current_user, require_parent_or_admin
from app.domain.api_v2_models import JobAcceptedResponse, RLHFExportRequest
from app.models import (
    Guardian,
    LearnerProfile,
    ParentalConsent,
    DiagnosticSession,
    Lesson,
    AuditLog,
    KnowledgeGap,
)
from app.repositories.repositories import LearnerRepository
from app.services.consent import ConsentService
from app.services.fourth_estate import FourthEstateService
from app.services.rlhf_service import RLHFService

router = APIRouter(prefix="/popia", tags=["compliance"])


# ──────────────────────────────────────────────────────────────────────────────
# Right-to-Access: Data Export
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/data-export/{learner_id}")
async def export_learner_data(
    learner_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    POPIA Right-to-Access: Export all personal data for a specific learner.
    Only guardians of that learner (or admins) can request this.
    Returns: JSON file with all learner data.
    """
    # Verify the requester is the guardian or an admin
    requester_id = current_user.get("sub")
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_by_id(learner_id)
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found",
        )
    
    # Check guardian relationship
    if learner.guardian_id != requester_id and str(current_user.get("role", "")).lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access data for your own learners",
        )
    await ConsentService(db).require_active_consent(learner_id, actor_id=requester_id)
    
    # Collect all learner data
    stmt = select(DiagnosticSession).where(DiagnosticSession.learner_id == learner_id)
    diag_sessions = await db.scalars(stmt)
    
    stmt = select(Lesson).where(Lesson.learner_id == learner_id)
    lessons = await db.scalars(stmt)
    
    stmt = select(KnowledgeGap).where(KnowledgeGap.learner_id == learner_id)
    gaps = await db.scalars(stmt)
    
    stmt = select(ParentalConsent).where(ParentalConsent.learner_id == learner_id)
    consents = await db.scalars(stmt)
    
    # Compile export payload
    export_data = {
        "export_date": datetime.now(UTC).isoformat(),
        "learner": {
            "id": learner.id,
            "pseudonym_id": learner.pseudonym_id,
            "display_name": learner.display_name,
            "grade": learner.grade,
            "language": learner.language,
            "archetype": learner.archetype,
            "theta": learner.theta,
            "xp": learner.xp,
            "streak_days": learner.streak_days,
            "created_at": learner.created_at.isoformat() if learner.created_at else None,
            "last_active": learner.last_active.isoformat() if learner.last_active else None,
        },
        "diagnostic_sessions": [
            {
                "id": s.id,
                "theta_before": s.theta_before,
                "theta_after": s.theta_after,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in diag_sessions
        ],
        "lessons": [
            {
                "id": l.id,
                "grade": l.grade,
                "subject": l.subject,
                "topic": l.topic,
                "language": l.language,
                "archetype": l.archetype,
                "feedback_score": l.feedback_score,
                "served_from_cache": l.served_from_cache,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in lessons
        ],
        "knowledge_gaps": [
            {
                "id": g.id,
                "grade": g.grade,
                "subject": g.subject,
                "topic": g.topic,
                "severity": g.severity,
                "resolved": g.resolved,
                "created_at": g.created_at.isoformat() if g.created_at else None,
            }
            for g in gaps
        ],
        "parental_consents": [
            {
                "id": c.id,
                "policy_version": c.policy_version,
                "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
                "is_active": c.is_active,
            }
            for c in consents
        ],
    }
    
    # Audit the export
    audit = FourthEstateService(db)
    await audit.record(
        event_type="data_export.requested",
        learner_pseudonym=learner.pseudonym_id,
        actor_id=requester_id,
        resource_id=learner_id,
        payload={"learner_id": learner_id},
    )
    
    return {
        "filename": f"eduboost_data_export_{learner_id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json",
        "data": export_data,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Right-to-Erasure: Deletion Request
# ──────────────────────────────────────────────────────────────────────────────


@router.post("/deletion-request/{learner_id}")
async def request_learner_deletion(
    learner_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    POPIA Right-to-Erasure: Request permanent deletion of learner data.
    
    Deletion is staged with a 30-day grace period to allow for withdrawal.
    After 30 days, data is permanently erased.
    
    Only guardians of that learner can request this.
    """
    requester_id = current_user.get("sub")
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_by_id(learner_id)
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found",
        )
    
    # Verify guardian relationship
    if learner.guardian_id != requester_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the learner's guardian can request deletion",
        )
    await ConsentService(db).require_active_consent(learner_id, actor_id=requester_id)
    
    # Check if deletion is already requested
    if learner.deletion_requested_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Deletion already requested for this learner",
        )
    
    # Mark learner as soft-deleted and set deletion request timestamp
    learner.is_deleted = True
    learner.deletion_requested_at = datetime.now(UTC)
    await db.commit()
    
    # Audit the deletion request
    audit = FourthEstateService(db)
    await audit.record(
        event_type="deletion.requested",
        learner_pseudonym=learner.pseudonym_id,
        actor_id=requester_id,
        resource_id=learner_id,
        constitutional_outcome="APPROVED",
        payload={
            "learner_id": learner_id,
            "grace_period_days": 30,
            "requested_at": datetime.now(UTC).isoformat(),
        },
    )
    
    return {
        "detail": "Deletion request submitted. Data will be permanently erased in 30 days.",
        "grace_period_days": 30,
        "learner_id": learner_id,
        "requested_at": datetime.now(UTC).isoformat(),
    }


@router.post("/deletion-cancel/{learner_id}")
async def cancel_learner_deletion(
    learner_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a pending deletion request within the 30-day grace period.
    Restores the learner profile to active status.
    """
    requester_id = current_user.get("sub")
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_by_id(learner_id)
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found",
        )
    
    # Verify guardian relationship
    if learner.guardian_id != requester_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the learner's guardian can cancel deletion",
        )
    await ConsentService(db).require_active_consent(learner_id, actor_id=requester_id)
    
    # Check if deletion was requested
    if learner.deletion_requested_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No deletion request exists for this learner",
        )
    
    # Cancel deletion
    learner.is_deleted = False
    learner.deletion_requested_at = None
    await db.commit()
    
    # Audit the cancellation
    audit = FourthEstateService(db)
    await audit.record(
        event_type="deletion.cancelled",
        learner_pseudonym=learner.pseudonym_id,
        actor_id=requester_id,
        resource_id=learner_id,
        payload={"learner_id": learner_id},
    )
    
    return {
        "detail": "Deletion request cancelled. Learner profile restored.",
        "learner_id": learner_id,
    }


@router.post("/deletion-execute/{learner_id}", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def execute_learner_deletion(
    learner_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_parent_or_admin),
):
    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            learner = await db.get(LearnerProfile, learner_id)
            if learner is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
            role = str(current_user.get("role", "")).lower()
            if learner.guardian_id != current_user.get("sub") and role != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to purge this learner")
            await LearnerRepository(db).purge_personal_data(learner_id)
            await FourthEstateService(db).record(
                event_type="deletion.executed",
                learner_pseudonym=learner.pseudonym_id,
                actor_id=current_user.get("sub"),
                resource_id=learner_id,
                constitutional_outcome="APPROVED",
                payload={"learner_id": learner_id},
            )
            await db.commit()
            return {"learner_id": learner_id, "purged": True}

    job = await enqueue_job(
        background_tasks,
        operation="popia_data_purge",
        payload={"learner_id": learner_id},
        handler=_run,
    )
    return JobAcceptedResponse(job_id=job["job_id"], operation=job["operation"], status=job["status"])


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


@router.get("/deletion-status/{learner_id}")
async def get_deletion_status(
    learner_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if a learner has a pending deletion request.
    """
    requester_id = current_user.get("sub")
    learner_repo = LearnerRepository(db)
    learner = await learner_repo.get_by_id(learner_id)
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found",
        )
    
    # Verify guardian relationship (or admin)
    if learner.guardian_id != requester_id and str(current_user.get("role", "")).lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only check status for your own learners",
        )
    
    if learner.deletion_requested_at is None:
        return {
            "learner_id": learner_id,
            "deletion_pending": False,
            "is_deleted": False,
        }
    
    # Calculate remaining grace period
    grace_period_end = learner.deletion_requested_at + timedelta(days=30)
    days_remaining = max((grace_period_end - datetime.now(UTC)).days, 0)
    
    return {
        "learner_id": learner_id,
        "deletion_pending": True,
        "is_deleted": learner.is_deleted,
        "requested_at": learner.deletion_requested_at.isoformat() if learner.deletion_requested_at else None,
        "days_remaining": days_remaining,
    }
