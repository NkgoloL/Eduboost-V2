"""Batch 235 — app/api_v2_routers/curriculum_expansion.py comprehensive branch coverage expansion.

Tests:
- get_scope_coverage
- capture_snapshots
- create_expansion_plan
- create_training_manifest
- get_training_manifest: 404 not found vs valid return
- decide_training_manifest: 404 (LookupError), 409 (ValueError), success
- export_training_manifest: 404 (LookupError), 409 (PermissionError), 422 (ValueError/RuntimeError), success
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api_v2_deps.auth import AuthContext
from app.api_v2_routers.curriculum_expansion import (
    capture_snapshots,
    create_expansion_plan,
    create_training_manifest,
    decide_training_manifest,
    export_training_manifest,
    get_scope_coverage,
    get_training_manifest,
)
from app.domain.curriculum_expansion_schemas import (
    CoverageSnapshotRequest,
    DatasetExportRequest,
    ExpansionPlanRequest,
    TrainingManifestApproveRequest,
    TrainingManifestCreateRequest,
)
from app.models import UserRole
from app.models.curriculum_expansion import TrainingDatasetManifest


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def admin_user():
    return AuthContext(
        user_id=str(uuid.uuid4()),
        roles=[UserRole.ADMIN],
        token_type="access",
        raw_claims={},
        jti=str(uuid.uuid4()),
    )


# ---------------------------------------------------------------------------
# Coverage & Snapshots
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_scope_coverage_and_capture_snapshots(mock_db):
    # 1. get_scope_coverage
    with patch("app.api_v2_routers.curriculum_expansion.CurriculumExpansionService") as mock_svc_cls:
        mock_svc_cls.return_value.coverage_for_scope = AsyncMock(return_value={"scope_id": "scope-1", "coverage": 0.9})
        res_cov = await get_scope_coverage("scope-1", mock_db)
        assert res_cov["coverage"] == 0.9

    # 2. capture_snapshots
    with patch("app.api_v2_routers.curriculum_expansion.CurriculumExpansionService") as mock_svc_cls:
        mock_snapshot = MagicMock(
            snapshot_id=uuid.uuid4(),
            scope_id="scope-1",
            language="en",
            target_total=100,
            approved_total=90,
            published_total=85,
            gap_count=10,
            status="active",
            captured_at=datetime.now(timezone.utc),
        )
        mock_svc_cls.return_value.capture_snapshot = AsyncMock(return_value=mock_snapshot)
        body = CoverageSnapshotRequest(scope_ids=["scope-1"], source_commit_sha="abcdef0123")
        snapshots_res = await capture_snapshots(body, mock_db)
        assert len(snapshots_res) == 1
        assert snapshots_res[0]["scope_id"] == "scope-1"
        mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# Expansion Plans & Training Manifests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_expansion_plan_and_manifest(mock_db, admin_user):
    # 1. create_expansion_plan
    with patch("app.api_v2_routers.curriculum_expansion.CurriculumExpansionService") as mock_svc_cls:
        mock_run = MagicMock(
            run_id=uuid.uuid4(),
            status="created",
            dry_run=False,
            plan_json={"tasks": []},
        )
        mock_svc_cls.return_value.build_expansion_plan = AsyncMock(return_value=mock_run)
        body_plan = ExpansionPlanRequest(
            scope_ids=["scope-1"],
            languages=["en"],
            layers=["diagnostic_items", "lessons"],
            dry_run=False,
        )
        plan_res = await create_expansion_plan(body_plan, admin_user, mock_db)
        assert plan_res.status == "created"
        mock_db.commit.assert_called_once()

    # 2. create_training_manifest
    with patch("app.api_v2_routers.curriculum_expansion.TrainingDatasetGovernanceService") as mock_gov_cls:
        mock_manifest_dict = {
            "manifest_id": uuid.uuid4(),
            "dataset_version": "v1.0.0",
            "status": "draft",
            "artifact_count": 50,
            "language_counts": {"en": 50},
            "scope_counts": {"scope-1": 50},
            "dataset_sha256": None,
            "output_path": None,
        }
        mock_gov_cls.return_value.create_manifest = AsyncMock(return_value=mock_manifest_dict)
        body_create = TrainingManifestCreateRequest(
            dataset_version="v1.0.0",
            scope_ids=["scope-1"],
            languages=["en"],
            require_published=True,
            min_quality_score=0.8,
            min_caps_alignment_score=0.8,
            policy_version="v1",
            rubric_version="v1",
        )
        manifest_res = await create_training_manifest(body_create, admin_user, mock_db)
        assert manifest_res.dataset_version == "v1.0.0"


# ---------------------------------------------------------------------------
# Manifest Decision & Export
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_manifest_get_decision_and_export_branches(mock_db, admin_user):
    manifest_id = uuid.uuid4()
    mock_manifest_dict = {
        "manifest_id": manifest_id,
        "dataset_version": "v1.0.0",
        "status": "approved",
        "artifact_count": 50,
        "language_counts": {"en": 50},
        "scope_counts": {"scope-1": 50},
        "dataset_sha256": "hash_xyz",
        "output_path": "/path/to/export.jsonl",
    }

    # 1. get_training_manifest 404 vs Found
    mock_db.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        await get_training_manifest(manifest_id, mock_db)
    assert exc.value.status_code == 404

    mock_db.get.return_value = mock_manifest_dict
    get_res = await get_training_manifest(manifest_id, mock_db)
    assert get_res.manifest_id == manifest_id

    # 2. decide_training_manifest LookupError (404), ValueError (409), Success
    with patch("app.api_v2_routers.curriculum_expansion.TrainingDatasetGovernanceService") as mock_gov_cls:
        mock_gov_cls.return_value.approve_manifest = AsyncMock(side_effect=LookupError("Manifest missing"))
        body_dec = TrainingManifestApproveRequest(decision="approve", reason="Approved for training")
        with pytest.raises(HTTPException) as exc:
            await decide_training_manifest(manifest_id, body_dec, admin_user, mock_db)
        assert exc.value.status_code == 404

        mock_gov_cls.return_value.approve_manifest = AsyncMock(side_effect=ValueError("Already decided"))
        with pytest.raises(HTTPException) as exc:
            await decide_training_manifest(manifest_id, body_dec, admin_user, mock_db)
        assert exc.value.status_code == 409

        mock_gov_cls.return_value.approve_manifest = AsyncMock(return_value=mock_manifest_dict)
        dec_res = await decide_training_manifest(manifest_id, body_dec, admin_user, mock_db)
        assert dec_res.status == "approved"

    # 3. export_training_manifest LookupError (404), PermissionError (409), ValueError (422), Success
    with patch("app.api_v2_routers.curriculum_expansion.TrainingDatasetGovernanceService") as mock_gov_cls:
        body_exp = DatasetExportRequest(output_name="dataset_export_2026.jsonl")

        mock_gov_cls.return_value.export_manifest = AsyncMock(side_effect=LookupError("Not found"))
        with pytest.raises(HTTPException) as exc:
            await export_training_manifest(manifest_id, body_exp, mock_db)
        assert exc.value.status_code == 404

        mock_gov_cls.return_value.export_manifest = AsyncMock(side_effect=PermissionError("Not approved"))
        with pytest.raises(HTTPException) as exc:
            await export_training_manifest(manifest_id, body_exp, mock_db)
        assert exc.value.status_code == 409

        mock_gov_cls.return_value.export_manifest = AsyncMock(side_effect=ValueError("Invalid export config"))
        with pytest.raises(HTTPException) as exc:
            await export_training_manifest(manifest_id, body_exp, mock_db)
        assert exc.value.status_code == 422

        mock_gov_cls.return_value.export_manifest = AsyncMock(return_value=(mock_manifest_dict, "/path/to/archive"))
        exp_res = await export_training_manifest(manifest_id, body_exp, mock_db)
        assert exp_res.manifest_id == manifest_id
