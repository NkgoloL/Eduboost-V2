"""
EduBoost SA — Consent Router (V2)
POPIA parental consent lifecycle endpoints.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_guardian_id
from app.modules.consent.service import ConsentService

router = APIRouter(prefix="/consent", tags=["POPIA Consent"])
_consent_service = ConsentService()


class ConsentGrantRequest(BaseModel):
    learner_id: UUID
    consent_version: str = "1.0"


class ConsentRevokeRequest(BaseModel):
    learner_id: UUID
    reason: str = "guardian_request"


@router.post("/grant", status_code=status.HTTP_201_CREATED)
async def grant_consent(
    body: ConsentGrantRequest,
    request: Request,
    guardian_id: UUID = Depends(get_current_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    consent = await _consent_service.grant_consent(
        body.learner_id, guardian_id, db,
        request=request,
        consent_version=body.consent_version,
    )
    return {
        "id": str(consent.id),
        "learner_id": str(consent.learner_id),
        "granted_at": consent.granted_at.isoformat(),
        "expires_at": consent.expires_at.isoformat(),
        "message": "Parental consent granted successfully.",
    }


@router.post("/revoke", status_code=status.HTTP_200_OK)
async def revoke_consent(
    body: ConsentRevokeRequest,
    request: Request,
    guardian_id: UUID = Depends(get_current_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    count = await _consent_service.revoke_consent(
        body.learner_id, guardian_id, db,
        reason=body.reason, request=request,
    )
    return {"revoked": count, "message": "Consent revoked. Learner data access has been suspended."}


@router.get("/status/{learner_id}")
async def consent_status(
    learner_id: UUID,
    guardian_id: UUID = Depends(get_current_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.repositories import ConsentRepository
    repo = ConsentRepository()
    consent = await repo.get_active(learner_id, db)
    if consent is None:
        return {"active": False, "learner_id": str(learner_id)}
    return {
        "active": True,
        "learner_id": str(learner_id),
        "granted_at": consent.granted_at.isoformat(),
        "expires_at": consent.expires_at.isoformat(),
        "days_remaining": (consent.expires_at - consent.granted_at).days,
    }
