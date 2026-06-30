"""
EduBoost SA — Consent Router (V2)
POPIA parental consent lifecycle endpoints.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.envelope_route import EnvelopedRoute
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.security import get_current_user  # noqa: F401
from app.repositories.repositories import LearnerRepository
from app.modules.consent.service import ConsentService
from app.services.popia_service import POPIADataRightsService
from app.security.dependencies import require_learner_write_for_current_user
from app.security.dependencies import require_learner_read_for_current_user

router = APIRouter(route_class=EnvelopedRoute, prefix="/consent", tags=["POPIA Consent"])


class ConsentGrantRequest(BaseModel):
    learner_id: UUID
    consent_version: str = "1.0"


class ConsentRevokeRequest(BaseModel):
    learner_id: UUID
    reason: str = "guardian_request"
    request_export: bool = False
    request_erasure: bool = False


@router.post("/grant", status_code=status.HTTP_201_CREATED)
async def grant_consent(
    body: ConsentGrantRequest,
    request: Request,
    current_user: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
) -> dict:
    learner_id = str(body.learner_id)
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_write_for_current_user(current_user, learner_id)
    # AuditLog emission is handled inside ConsentService.grant().
    consent = await ConsentService(db).grant(
        current_user.user_id,
        str(body.learner_id),
        body.consent_version,
        ip_hash=_get_ip(request),
    )
    request.state.analytics = {
        "event": "consent_granted",
        "pseudonym_id": f"learner:{body.learner_id}",
        "properties": {"policy_version": body.consent_version},
    }
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
    current_user: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
) -> dict:
    learner_id = str(body.learner_id)
    learner = await LearnerRepository(db).get_by_id(learner_id)
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_write_for_current_user(current_user, learner_id)
    # AuditLog emission is handled inside ConsentService.revoke().
    await ConsentService(db).revoke(
        str(body.learner_id),
        guardian_id=current_user.user_id,
        reason=body.reason,
    )

    # Optional: create export/erasure requests if requested
    popia_service = POPIADataRightsService(db)
    export_request_id = None
    erasure_request_id = None

    if body.request_export:
        export_result = await popia_service.request_export(learner_id, current_user.raw_claims)
        export_request_id = export_result.get("request_id")

    if body.request_erasure:
        erasure_result = await popia_service.request_erasure(learner_id, current_user.raw_claims, reason="consent_withdrawal")
        erasure_request_id = erasure_result.get("request_id")

    request.state.analytics = {
        "event": "consent_revoked",
        "pseudonym_id": f"learner:{body.learner_id}",
        "properties": {
            "reason": body.reason,
            "request_export": body.request_export,
            "request_erasure": body.request_erasure,
        },
    }
    return {
        "revoked": 1,
        "message": "Consent revoked. Learner data access has been suspended.",
        "export_request_id": export_request_id,
        "erasure_request_id": erasure_request_id,
    }


@router.get("/status/{learner_id}")
async def consent_status(
    learner_id: UUID,
    current_user: AuthContext = Depends(require_auth_context),
    db: AsyncSession = Depends(get_db),
) -> dict:
    learner = await LearnerRepository(db).get_by_id(str(learner_id))
    if learner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found")
    require_learner_read_for_current_user(current_user, learner)
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
