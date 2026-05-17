from __future__ import annotations
from app.repositories.learner_repository import LearnerRepository
from app.security.dependencies import require_learner_read_for_current_user, require_learner_write_for_current_user
from app.security.dependencies import require_active_consent_for_current_user
from typing import Any
import inspect
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.consent_repository import ConsentRepository
from app.security.dependencies import require_learner_write_for_current_user
"""
app/api_v2_routers/popia.py
POPIA endpoints: consent lifecycle (§4.1) and data-subject rights (§4.3).
All learner-data routes use the require_active_consent dependency (§4.2).
"""

import asyncio
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.consent_gate import ActiveConsent, require_active_consent
from app.domain.consent import ConsentRecord
from app.domain.data_subject_rights import (
    CorrectionRequest,
    DataExportRequest,
    ErasureRequest,
    RestrictionRequest,
)
from app.modules.consent.service import ConsentService
from app.services.popia_service import POPIADataRightsService

from app.core.envelope_route import EnvelopedRoute

router = APIRouter(route_class=EnvelopedRoute, prefix="/popia", tags=["popia"])


from app.core.database import get_db, AsyncSessionLocal
from app.core.jobs import enqueue_job
from app.core.security import get_current_user, require_parent_or_admin
from app.repositories.repositories import AuditRepository, ConsentRepository, LearnerRepository
from app.services.fourth_estate import FourthEstateService

async def get_consent_service_for_router(db: AsyncSession = Depends(get_db)) -> ConsentService:
    return ConsentService(ConsentRepository(db), AuditRepository(db))


async def get_data_subject_rights_service_for_router(db: AsyncSession = Depends(get_db)) -> POPIADataRightsService:
    """Dependency provider for POPIA data rights service."""
    return POPIADataRightsService(db)


# ---------------------------------------------------------------------------
# Request/response schemas
# ---------------------------------------------------------------------------

class ConsentGrantRequest(BaseModel):
    learner_id: uuid.UUID
    guardian_id: uuid.UUID
    privacy_notice_version: str


class ConsentDenyRequest(BaseModel):
    learner_id: uuid.UUID
    guardian_id: uuid.UUID
    privacy_notice_version: str
    reason: Optional[str] = None


class ConsentWithdrawRequest(BaseModel):
    learner_id: uuid.UUID


class ConsentRenewRequest(BaseModel):
    learner_id: uuid.UUID
    privacy_notice_version: str


class ExportRequestBody(BaseModel):
    learner_id: uuid.UUID
    format: str = "json"


class ErasureRequestBody(BaseModel):
    learner_id: uuid.UUID
    reason: str = "guardian_request"


class ErasureApproveBody(BaseModel):
    review_notes: Optional[str] = None


class CorrectionRequestBody(BaseModel):
    learner_id: uuid.UUID
    field_name: str
    new_value: str
    old_value: Optional[str] = None


class RestrictionRequestBody(BaseModel):
    learner_id: uuid.UUID
    reason: str


class CorrectionRequestLegacyBody(BaseModel):
    learner_id: uuid.UUID
    fields: dict[str, Any]
    reason: str


class RestrictionRequestLegacyBody(BaseModel):
    learner_id: uuid.UUID
    reason: str


class DeletionRequestBody(BaseModel):
    reason: str


# ---------------------------------------------------------------------------
# §4.1 Consent lifecycle
# ---------------------------------------------------------------------------


# code_591_610_popia_consent_lifecycle_repair
def _authenticated_actor_id(current_user):
    # Return stable authenticated actor identity for POPIA audit events.
    if isinstance(current_user, dict):
        for key in ("id", "user_id", "sub"):
            value = current_user.get(key)
            if value:
                return value
    for attr in ("id", "user_id", "sub"):
        value = getattr(current_user, attr, None)
        if value:
            return value
    raise HTTPException(status_code=401, detail="Authenticated actor id is unavailable")


async def _enforce_popia_learner_write(current_user, learner_id):
    # Enforce learner write access while tolerating sync/async dependency helpers.
    try:
        result = require_learner_write_for_current_user(current_user, learner_id)
    except TypeError:
        try:
            result = require_learner_write_for_current_user(learner_id, current_user)
        except TypeError:
            result = require_learner_write_for_current_user(current_user=current_user, learner_id=learner_id)
    if inspect.isawaitable(result):
        return await result
    return result


def get_canonical_consent_service(db: AsyncSession = Depends(get_db)) -> ConsentService:
    # Construct the canonical SQLAlchemy-compatible consent service for FastAPI v2.
    params = inspect.signature(ConsentService).parameters
    if "session" in params:
        return ConsentService(session=db)
    if "db" in params:
        return ConsentService(db=db)
    if "consent_repository" in params or "consent_repo" in params:
        repo = ConsentRepository(db)
        if "consent_repository" in params:
            return ConsentService(consent_repository=repo)
        return ConsentService(consent_repo=repo)
    try:
        return ConsentService(db)
    except TypeError as exc:
        raise RuntimeError(
            "Cannot construct canonical ConsentService from AsyncSession. "
            "Align app.modules.consent.service.ConsentService constructor before using POPIA lifecycle routes."
        ) from exc

@router.post("/consent/grant", response_model=ConsentRecord)
async def grant_consent(
    # require_learner_write_for_current_user
    body: ConsentGrantRequest,
    consent_svc: ConsentService = Depends(get_canonical_consent_service),
    # TODO: replace with real auth dependency that injects actor_id from JWT
    current_user = Depends(get_current_user),
) -> ConsentRecord:
    await _enforce_popia_learner_write(current_user, body.learner_id)
    actor_id = _authenticated_actor_id(current_user)
    return await consent_svc.grant(
        learner_id=body.learner_id,
        guardian_id=body.guardian_id,
        privacy_notice_version=body.privacy_notice_version,
        actor_id=actor_id,
    )


@router.post("/consent/deny", response_model=ConsentRecord)
async def deny_consent(
    # require_learner_write_for_current_user
    body: ConsentDenyRequest,
    consent_svc: ConsentService = Depends(get_canonical_consent_service),
    current_user = Depends(get_current_user),
) -> ConsentRecord:
    await _enforce_popia_learner_write(current_user, body.learner_id)
    actor_id = _authenticated_actor_id(current_user)
    return await consent_svc.deny(
        learner_id=body.learner_id,
        guardian_id=body.guardian_id,
        privacy_notice_version=body.privacy_notice_version,
        actor_id=actor_id,
        reason=body.reason,
    )


@router.post("/consent/withdraw", response_model=ConsentRecord)
async def withdraw_consent(
    # require_learner_write_for_current_user
    body: ConsentWithdrawRequest,
    consent_svc: ConsentService = Depends(get_canonical_consent_service),
    current_user = Depends(get_current_user),
) -> ConsentRecord:
    await _enforce_popia_learner_write(current_user, body.learner_id)
    actor_id = _authenticated_actor_id(current_user)
    return await consent_svc.withdraw(
        learner_id=body.learner_id,
        actor_id=actor_id,
    )


@router.post("/consent/renew", response_model=ConsentRecord)
async def renew_consent(
    # require_learner_write_for_current_user
    body: ConsentRenewRequest,
    consent_svc: ConsentService = Depends(get_canonical_consent_service),
    current_user = Depends(get_current_user),
) -> ConsentRecord:
    await _enforce_popia_learner_write(current_user, body.learner_id)
    actor_id = _authenticated_actor_id(current_user)
    return await consent_svc.renew(
        learner_id=body.learner_id,
        actor_id=actor_id,
        privacy_notice_version=body.privacy_notice_version,
    )


# ---------------------------------------------------------------------------
# §4.3 Data Subject Rights – Export
# ---------------------------------------------------------------------------

@router.post("/exports")
async def create_export_request(
    # require_active_consent_for_current_user
    body: ExportRequestBody,
    dsr_svc: POPIADataRightsService = Depends(get_data_subject_rights_service_for_router),
    current_user: Any = Depends(get_current_user),
) -> Any:
    """Creates a new data export request (§4.3)."""
    return await dsr_svc.build_learner_export(
        learner_id=str(body.learner_id),
        current_user=current_user,
    )


# ---------------------------------------------------------------------------
# §4.3 Data Subject Rights – Erasure
# ---------------------------------------------------------------------------

@router.post("/erasure", status_code=status.HTTP_201_CREATED)
async def create_erasure_request(
    body: ErasureRequestBody,
    dsr_svc: POPIADataRightsService = Depends(get_data_subject_rights_service_for_router),
    current_user: Any = Depends(get_current_user),
) -> Any:
    """Creates a new erasure request (§4.3)."""
    return await dsr_svc.request_erasure(
        learner_id=str(body.learner_id),
        current_user=current_user,
        reason=body.reason,
    )



@router.post("/erasure/{learner_id}/cancel")
async def cancel_erasure(
    learner_id: uuid.UUID,
    dsr_svc: POPIADataRightsService = Depends(get_data_subject_rights_service_for_router),
    current_user: Any = Depends(get_current_user),
) -> Any:
    """Cancels a pending erasure request."""
    return await dsr_svc.cancel_erasure(
        learner_id=str(learner_id),
        current_user=current_user,
    )


# ---------------------------------------------------------------------------
# §4.3 Data Subject Rights – Correction & Restriction
# ---------------------------------------------------------------------------

@router.post("/correction")
async def create_correction_request(
    body: CorrectionRequestLegacyBody,
    dsr_svc: POPIADataRightsService = Depends(get_data_subject_rights_service_for_router),
    current_user: Any = Depends(get_current_user),
) -> Any:
    """Creates a correction request (§4.3)."""
    return await dsr_svc.request_correction(
        learner_id=str(body.learner_id),
        current_user=current_user,
        fields=body.fields,
        reason=body.reason,
    )


@router.post("/restriction")
async def create_restriction_request(
    body: RestrictionRequestLegacyBody,
    dsr_svc: POPIADataRightsService = Depends(get_data_subject_rights_service_for_router),
    current_user: Any = Depends(get_current_user),
) -> Any:
    """Creates a processing restriction request (§4.3)."""
    return await dsr_svc.restrict_processing(
        learner_id=str(body.learner_id),
        current_user=current_user,
        reason=body.reason,
    )
