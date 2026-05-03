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
    consent = await ConsentService(db).grant(
        str(guardian_id),
        str(body.learner_id),
        body.consent_version,
        ip_hash=_get_ip(request),
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
    await ConsentService(db).revoke(str(body.learner_id))
    return {"revoked": 1, "message": "Consent revoked. Learner data access has been suspended."}


@router.get("/status/{learner_id}")
async def consent_status(
    learner_id: UUID,
    guardian_id: UUID = Depends(get_current_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    consent = await ConsentService(db).get_status(str(learner_id))
    if consent is None:
        return {"active": False, "learner_id": str(learner_id)}
    return {
        "active": True,
        "learner_id": str(learner_id),
        "granted_at": consent.granted_at.isoformat(),
        "expires_at": consent.expires_at.isoformat(),
        "days_remaining": (consent.expires_at - consent.granted_at).days,
    }


def _get_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
