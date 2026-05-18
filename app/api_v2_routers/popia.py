"""
app/api_v2_routers/popia.py
POPIA endpoints: consent lifecycle (§4.1) and data-subject rights (§4.3).
All learner-data routes use the require_active_consent dependency (§4.2).
"""
from __future__ import annotations

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.api_v2_deps.consent_lifecycle import (
    authenticated_actor_id as _authenticated_actor_id,
    enforce_popia_learner_write as _enforce_popia_learner_write,
    get_canonical_consent_service,
    get_canonical_data_rights_service,
)
from app.core.envelope_route import EnvelopedRoute
from app.core.security import get_current_user
from app.domain.consent import ConsentRecord
from app.modules.consent.service import ConsentService
from app.services.popia_service import POPIADataRightsService

router = APIRouter(route_class=EnvelopedRoute, prefix="/popia", tags=["popia"])


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
    dsr_svc: POPIADataRightsService = Depends(get_canonical_data_rights_service),
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
    dsr_svc: POPIADataRightsService = Depends(get_canonical_data_rights_service),
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
    dsr_svc: POPIADataRightsService = Depends(get_canonical_data_rights_service),
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
    dsr_svc: POPIADataRightsService = Depends(get_canonical_data_rights_service),
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
    dsr_svc: POPIADataRightsService = Depends(get_canonical_data_rights_service),
    current_user: Any = Depends(get_current_user),
) -> Any:
    """Creates a processing restriction request (§4.3)."""
    return await dsr_svc.restrict_processing(
        learner_id=str(body.learner_id),
        current_user=current_user,
        reason=body.reason,
    )
