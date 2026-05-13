"""
app/core/consent_gate.py
§4.2 – Declarative consent enforcement via FastAPI Depends.

Usage on any route that touches learner data:

    @router.get("/learners/{learner_id}/profile")
    async def get_profile(
        learner_id: UUID,
        _: ConsentRecord = Depends(require_active_consent),
        ...
    ):
        ...

The dependency resolves the current learner from the request and raises
HTTP 403 if consent is not active.
"""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.domain.consent import ConsentRecord
from app.services.consent_service import ConsentService


async def _get_learner_id_from_request(request: Request) -> uuid.UUID:
    """
    Extract learner_id from path params or JWT claims.
    Falls back to path param 'learner_id'; override per-router as needed.
    """
    raw = request.path_params.get("learner_id")
    if raw is None:
        # Try JWT claim injected by auth middleware
        raw = getattr(request.state, "learner_id", None)
    if raw is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="learner_id could not be determined for consent check.",
        )
    try:
        return uuid.UUID(str(raw))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid learner_id: {raw!r}",
        )


async def require_active_consent(
    request: Request,
    consent_service: ConsentService = Depends(),
) -> ConsentRecord:
    """
    FastAPI dependency – resolves to the active ConsentRecord or raises
    HTTP 403 Forbidden.  Attach to every learner-data route.
    """
    learner_id = await _get_learner_id_from_request(request)
    try:
        return await consent_service.assert_active_consent(learner_id)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


# Convenience alias for injection sites
ActiveConsent = Annotated[ConsentRecord, Depends(require_active_consent)]
