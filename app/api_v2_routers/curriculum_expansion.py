"""Phase 7 curriculum coverage and training-data governance routes."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2_deps.auth import AuthContext, require_admin
from app.core.database import get_db
from app.core.envelope_route import EnvelopedRoute
from app.domain.curriculum_expansion_schemas import (
    CoverageSnapshotRequest,
    DatasetExportRequest,
    ExpansionPlanRequest,
    ExpansionPlanResponse,
    TrainingManifestApproveRequest,
    TrainingManifestCreateRequest,
    TrainingManifestResponse,
)
from app.models.curriculum_expansion import CurriculumCoverageSnapshot, TrainingDatasetManifest
from app.services.curriculum_expansion import CurriculumExpansionService, TrainingDatasetGovernanceService

router = APIRouter(
    route_class=EnvelopedRoute,
    prefix="/admin/curriculum-expansion",
    tags=["admin-curriculum-expansion"],
    dependencies=[Depends(require_admin)],
)


@router.get("/coverage/{scope_id}")
async def get_scope_coverage(scope_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    return await CurriculumExpansionService(db).coverage_for_scope(scope_id)


@router.post("/coverage/snapshots")
async def capture_snapshots(
    body: CoverageSnapshotRequest,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    service = CurriculumExpansionService(db)
    snapshots = [
        await service.capture_snapshot(scope_id, body.source_commit_sha)
        for scope_id in sorted(body.scope_ids)
    ]
    await db.commit()
    return [
        {
            "snapshot_id": str(row.snapshot_id),
            "scope_id": row.scope_id,
            "language": row.language,
            "target_total": row.target_total,
            "approved_total": row.approved_total,
            "published_total": row.published_total,
            "gap_count": row.gap_count,
            "status": row.status,
            "captured_at": row.captured_at,
        }
        for row in snapshots
    ]


@router.post("/plans", response_model=ExpansionPlanResponse)
async def create_expansion_plan(
    body: ExpansionPlanRequest,
    auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> ExpansionPlanResponse:
    run = await CurriculumExpansionService(db).build_expansion_plan(
        requested_by=str(auth.user_id),
        scope_ids=body.scope_ids,
        languages=body.languages,
        layers=body.layers,
        dry_run=body.dry_run,
    )
    await db.commit()
    await db.refresh(run)
    return ExpansionPlanResponse(
        run_id=run.run_id,
        status=run.status,
        dry_run=run.dry_run,
        plan=run.plan_json,
    )


@router.post("/training-manifests", response_model=TrainingManifestResponse)
async def create_training_manifest(
    body: TrainingManifestCreateRequest,
    auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> TrainingManifestResponse:
    manifest = await TrainingDatasetGovernanceService(db).create_manifest(
        dataset_version=body.dataset_version,
        scope_ids=body.scope_ids,
        languages=body.languages,
        created_by=str(auth.user_id),
        require_published=body.require_published,
        min_quality_score=body.min_quality_score,
        min_caps_alignment_score=body.min_caps_alignment_score,
        policy_version=body.policy_version,
        rubric_version=body.rubric_version,
    )
    await db.commit()
    await db.refresh(manifest)
    return TrainingManifestResponse.model_validate(manifest)


@router.get("/training-manifests/{manifest_id}", response_model=TrainingManifestResponse)
async def get_training_manifest(
    manifest_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TrainingManifestResponse:
    manifest = await db.get(TrainingDatasetManifest, manifest_id)
    if manifest is None:
        raise HTTPException(status_code=404, detail="Training dataset manifest not found")
    return TrainingManifestResponse.model_validate(manifest)


@router.post("/training-manifests/{manifest_id}/decision", response_model=TrainingManifestResponse)
async def decide_training_manifest(
    manifest_id: UUID,
    body: TrainingManifestApproveRequest,
    auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> TrainingManifestResponse:
    try:
        manifest = await TrainingDatasetGovernanceService(db).approve_manifest(
            manifest_id, str(auth.user_id), body.decision
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    await db.commit()
    await db.refresh(manifest)
    return TrainingManifestResponse.model_validate(manifest)


@router.post("/training-manifests/{manifest_id}/export", response_model=TrainingManifestResponse)
async def export_training_manifest(
    manifest_id: UUID,
    body: DatasetExportRequest,
    db: AsyncSession = Depends(get_db),
) -> TrainingManifestResponse:
    try:
        manifest, _ = await TrainingDatasetGovernanceService(db).export_manifest(
            manifest_id, body.output_name
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await db.commit()
    await db.refresh(manifest)
    return TrainingManifestResponse.model_validate(manifest)
