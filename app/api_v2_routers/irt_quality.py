"""Admin API for Phase 4 IRT quality controls."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2_deps.auth import AuthContext, require_admin
from app.core.database import get_db
from app.core.envelope_route import EnvelopedRoute
from app.domain.irt_quality_schemas import (
    IRTCalibrationRunRequest,
    IRTCalibrationRunResponse,
    IRTItemQualityResponse,
    IRTManualOverrideRequest,
    IRTRunStatusResponse,
)
from app.models.diagnostic_item import DiagnosticItem
from app.models.irt_quality import IRTCalibrationRun
from app.modules.jobs import enqueue_durable
from app.services.irt_quality_service import IRTQualityService

router = APIRouter(
    route_class=EnvelopedRoute,
    prefix="/admin/irt-quality",
    tags=["admin-irt-quality"],
)


def _item_response(item: DiagnosticItem) -> IRTItemQualityResponse:
    return IRTItemQualityResponse(
        item_id=item.item_id,
        state=item.irt_quality_state,
        strike_count=item.irt_strike_count,
        response_count=item.irt_response_count,
        unique_learners=item.irt_unique_learners,
        model_version=item.irt_model_version,
        last_calibrated_at=item.irt_last_calibrated_at,
        last_run_id=item.irt_last_run_id,
        reason=item.irt_intervention_reason,
        manual_override_until=item.irt_manual_override_until,
        rewrite_artifact_id=item.irt_rewrite_artifact_id,
    )


@router.post("/runs", response_model=IRTCalibrationRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_calibration_run(
    request: IRTCalibrationRunRequest,
    actor: AuthContext = Depends(require_admin),
) -> IRTCalibrationRunResponse:
    key = request.idempotency_key or f"manual:{actor.user_id}:{','.join(map(str, request.item_ids or []))}:{request.dry_run}"
    job_id = await enqueue_durable(
        "run_irt_quality_watchdog",
        operation="irt_quality_calibration",
        payload={"dry_run": request.dry_run, "item_count": len(request.item_ids or [])},
        kwargs={
            "dry_run": request.dry_run,
            "item_ids": [str(value) for value in request.item_ids] if request.item_ids else None,
            "idempotency_key": key,
            "actor_id": str(actor.user_id),
        },
    )
    return IRTCalibrationRunResponse(job_id=job_id)


@router.get("/runs/{run_id}", response_model=IRTRunStatusResponse)
async def get_calibration_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    _actor: AuthContext = Depends(require_admin),
) -> IRTRunStatusResponse:
    run = await db.get(IRTCalibrationRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="IRT calibration run not found")
    return IRTRunStatusResponse(
        run_id=run.run_id,
        status=run.status,
        dry_run=run.dry_run,
        model_version=run.model_version,
        policy_version=run.policy_version,
        summary=run.summary or {},
        started_at=run.started_at,
        finished_at=run.finished_at,
    )


@router.get("/items/{item_id}", response_model=IRTItemQualityResponse)
async def get_item_quality(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    _actor: AuthContext = Depends(require_admin),
) -> IRTItemQualityResponse:
    item = await db.get(DiagnosticItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Diagnostic item not found")
    return _item_response(item)


@router.post("/items/{item_id}/override", response_model=IRTItemQualityResponse)
async def set_manual_override(
    item_id: UUID,
    request: IRTManualOverrideRequest,
    db: AsyncSession = Depends(get_db),
    actor: AuthContext = Depends(require_admin),
) -> IRTItemQualityResponse:
    try:
        item = await IRTQualityService().manual_override(
            db,
            item_id=item_id,
            state=request.state,
            reason=request.reason,
            expires_at=request.expires_at,
            actor_id=str(actor.user_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _item_response(item)


@router.post("/items/{item_id}/override/clear", response_model=IRTItemQualityResponse)
async def clear_manual_override(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    actor: AuthContext = Depends(require_admin),
) -> IRTItemQualityResponse:
    try:
        item = await IRTQualityService().clear_override(db, item_id=item_id, actor_id=str(actor.user_id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _item_response(item)
