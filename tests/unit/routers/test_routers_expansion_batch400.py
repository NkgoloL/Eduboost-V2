from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest
from fastapi import HTTPException

from app.api_v2_deps.auth import AuthContext, TokenType, UserRole
from app.api_v2_routers import (
    ai_operations,
    gamification,
    irt_quality,
    curriculum_expansion,
)
from app.domain.ai_operations_schemas import ReservationCancelRequest
from app.domain.irt_quality_schemas import (
    IRTCalibrationRunRequest,
    IRTManualOverrideRequest,
)
from app.domain.curriculum_expansion_schemas import (
    CoverageSnapshotRequest,
    ExpansionPlanRequest,
    TrainingManifestCreateRequest,
    TrainingManifestApproveRequest,
    DatasetExportRequest,
)


@pytest.fixture
def mock_admin_context() -> AuthContext:
    return AuthContext(
        user_id="admin_123",
        roles=[UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={},
        jti="jti_admin",
    )


# ── AI OPERATIONS ROUTER ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ai_operations_budgets_and_health(monkeypatch):
    mock_svc = MagicMock()
    mock_svc.counter_view = AsyncMock(
        return_value={
            "scope_type": "user",
            "scope_id": "u1",
            "period_key": "2026-09",
            "used_tokens": 100,
            "reserved_tokens": 50,
            "token_limit": 1000,
            "remaining_tokens": 850,
            "used_cost_usd": 0.05,
            "alert_threshold_reached": False,
            "updated_at": datetime.now(timezone.utc),
        }
    )
    mock_svc.provider_health = AsyncMock(
        return_value=[
            {
                "provider": "openai",
                "calls_24h": 100,
                "errors_24h": 1,
                "fallback_24h": 0,
                "error_rate": 0.01,
                "status": "healthy",
            }
        ]
    )
    monkeypatch.setattr(ai_operations, "AIOperationsService", lambda db: mock_svc)

    db = AsyncMock()
    # 1. user budget
    res_u = await ai_operations.get_user_budget("u1", db)
    assert res_u.scope_id == "u1"

    # 2. tenant budget
    mock_svc.counter_view = AsyncMock(
        return_value={
            "scope_type": "tenant",
            "scope_id": "t1",
            "period_key": "2026-09",
            "used_tokens": 200,
            "reserved_tokens": 100,
            "token_limit": 5000,
            "remaining_tokens": 4700,
            "used_cost_usd": 0.10,
            "alert_threshold_reached": False,
            "updated_at": datetime.now(timezone.utc),
        }
    )
    res_t = await ai_operations.get_tenant_budget("t1", db)
    assert res_t.scope_id == "t1"

    # 3. provider health
    health_list = await ai_operations.provider_health(db)
    assert len(health_list) == 1
    assert health_list[0].provider == "openai"


@pytest.mark.asyncio
async def test_ai_operations_usage_and_reservations(monkeypatch, mock_admin_context):
    db = AsyncMock()
    # Mock scalars result
    mock_event = MagicMock()
    mock_event.event_id = uuid4()
    mock_event.operation_id = "op_test_1"
    mock_event.user_id = "u1"
    mock_event.tenant_id = "t1"
    mock_event.purpose = "tutor"
    mock_event.provider = "anthropic"
    mock_event.model = "claude-3"
    mock_event.prompt_tokens = 50
    mock_event.completion_tokens = 100
    mock_event.total_tokens = 150
    mock_event.estimated_cost_usd = 0.02
    mock_event.outcome = "success"
    mock_event.created_at = datetime.now(timezone.utc)

    mock_scalars_res = MagicMock()
    mock_scalars_res.all.return_value = [mock_event]
    db.scalars = AsyncMock(return_value=mock_scalars_res)

    # 1. list_usage with filters
    usage = await ai_operations.list_usage(
        tenant_id="t1",
        provider="anthropic",
        purpose="tutor",
        hours=24,
        limit=10,
        db=db,
    )
    assert len(usage) == 1
    assert usage[0].provider == "anthropic"

    # 2. list_reservations
    mock_res = MagicMock()
    mock_res.reservation_id = uuid4()
    mock_res.operation_id = "op_1"
    mock_res.user_id = "u1"
    mock_res.tenant_id = "t1"
    mock_res.purpose = "tutor"
    mock_res.estimated_tokens = 200
    mock_res.status = "active"
    mock_res.failure_reason = None
    mock_res.reserved_at = datetime.now(timezone.utc)
    mock_res.expires_at = datetime.now(timezone.utc)
    mock_res.finalized_at = None
    mock_scalars_res.all.return_value = [mock_res]

    reservations = await ai_operations.list_reservations(status="active", limit=10, db=db)
    assert len(reservations) == 1
    assert reservations[0].operation_id == "op_1"

    # 3. cancel_reservation: not found
    mock_svc = MagicMock()
    mock_svc.cancel = AsyncMock(return_value=None)
    monkeypatch.setattr(ai_operations, "AIOperationsService", lambda d: mock_svc)
    with pytest.raises(HTTPException) as exc:
        await ai_operations.cancel_reservation("op_missing", ReservationCancelRequest(reason="test"), mock_admin_context, db)
    assert exc.value.status_code == 404

    # 4. cancel_reservation: success
    mock_res.status = "cancelled"
    mock_res.metadata_json = {}
    mock_svc.cancel = AsyncMock(return_value=mock_res)
    cancelled = await ai_operations.cancel_reservation("op_1", ReservationCancelRequest(reason="test"), mock_admin_context, db)
    assert cancelled.operation_id == "op_1"


# ── GAMIFICATION ROUTER ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_gamification_router(monkeypatch, mock_admin_context):
    db = AsyncMock()

    # 1. get_profile learner not found
    mock_learner_svc = MagicMock()
    mock_learner_svc.get_learner_summary = AsyncMock(return_value=None)
    monkeypatch.setattr(gamification, "LearnerService", lambda d: mock_learner_svc)

    with pytest.raises(HTTPException) as exc:
        await gamification.get_profile("unknown", db, mock_admin_context)
    assert exc.value.status_code == 404

    # 2. get_profile success
    mock_learner_svc.get_learner_summary = AsyncMock(return_value=MagicMock(pseudonym_id="pseudo_1"))
    monkeypatch.setattr(gamification, "require_learner_read_for_current_user", MagicMock())
    monkeypatch.setattr(gamification, "require_active_consent_for_current_user", AsyncMock())

    mock_gamify_svc = MagicMock()
    mock_gamify_svc.get_profile = AsyncMock(return_value={"learner_id": "l1", "xp": 100, "level": 2})
    mock_gamify_svc.award_xp = AsyncMock()
    mock_gamify_svc.leaderboard = AsyncMock(return_value=[{"learner_id": "l1", "xp": 100}])
    monkeypatch.setattr(gamification.GamificationServiceV2, "from_session", lambda d: mock_gamify_svc)

    prof = await gamification.get_profile("l1", db, mock_admin_context)
    assert prof["learner_id"] == "l1"

    # 3. get_profile ValueError -> 404
    mock_gamify_svc.get_profile = AsyncMock(side_effect=ValueError("Profile missing"))
    with pytest.raises(HTTPException) as exc_v:
        await gamification.get_profile("l1", db, mock_admin_context)
    assert exc_v.value.status_code == 404

    # 4. award_xp learner not found
    mock_learner_svc.get_learner_summary = AsyncMock(return_value=None)
    req_xp = gamification.AwardXPRequest(learner_id="unknown", xp_amount=50, lesson_id="less_1")
    with pytest.raises(HTTPException) as exc_xp:
        await gamification.award_xp(req_xp, db, mock_admin_context)
    assert exc_xp.value.status_code == 404

    # 5. award_xp success
    mock_learner_svc.get_learner_summary = AsyncMock(return_value=MagicMock(pseudonym_id="pseudo_1"))
    monkeypatch.setattr(gamification, "require_learner_write_for_current_user", MagicMock())
    mock_fourth_estate = MagicMock()
    mock_fourth_estate.record = AsyncMock()
    monkeypatch.setattr(gamification, "FourthEstateService", lambda d: mock_fourth_estate)
    mock_gamify_svc.get_profile = AsyncMock(return_value={"learner_id": "l1", "xp": 150})

    req_ok = gamification.AwardXPRequest(learner_id="l1", xp_amount=50, lesson_id="less_1")
    res_xp = await gamification.award_xp(req_ok, db, mock_admin_context)
    assert res_xp["awarded"] is True
    assert res_xp["xp_amount"] == 50
    assert res_xp["lesson_completed"] is True

    # 6. leaderboard
    lb = await gamification.get_leaderboard(limit=5, db=db)
    assert len(lb) == 1


# ── IRT QUALITY ROUTER ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_irt_quality_router(monkeypatch, mock_admin_context):
    # 1. create_calibration_run
    monkeypatch.setattr(irt_quality, "enqueue_durable", AsyncMock(return_value="job_irt_001"))
    req = IRTCalibrationRunRequest(item_ids=[uuid4()], dry_run=True)
    res_run = await irt_quality.create_calibration_run(req, mock_admin_context)
    assert res_run.job_id == "job_irt_001"

    db = AsyncMock()
    # 2. get_calibration_run not found
    db.get = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc:
        await irt_quality.get_calibration_run(uuid4(), db, mock_admin_context)
    assert exc.value.status_code == 404

    # 3. get_calibration_run found
    mock_run = MagicMock()
    mock_run.run_id = uuid4()
    mock_run.status = "completed"
    mock_run.dry_run = True
    mock_run.model_version = "v1"
    mock_run.policy_version = "v1"
    mock_run.summary = {}
    mock_run.started_at = datetime.now(timezone.utc)
    mock_run.finished_at = datetime.now(timezone.utc)
    db.get = AsyncMock(return_value=mock_run)

    run_view = await irt_quality.get_calibration_run(mock_run.run_id, db, mock_admin_context)
    assert run_view.status == "completed"

    # 4. get_item_quality not found
    db.get = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_item:
        await irt_quality.get_item_quality(uuid4(), db, mock_admin_context)
    assert exc_item.value.status_code == 404

    # 5. get_item_quality found
    mock_diag_item = MagicMock()
    mock_diag_item.item_id = uuid4()
    mock_diag_item.irt_quality_state = "healthy"
    mock_diag_item.irt_strike_count = 0
    mock_diag_item.irt_response_count = 50
    mock_diag_item.irt_unique_learners = 20
    mock_diag_item.irt_model_version = "v1"
    mock_diag_item.irt_last_calibrated_at = datetime.now(timezone.utc)
    mock_diag_item.irt_last_run_id = uuid4()
    mock_diag_item.irt_intervention_reason = None
    mock_diag_item.irt_manual_override_until = None
    mock_diag_item.irt_rewrite_artifact_id = None
    db.get = AsyncMock(return_value=mock_diag_item)

    item_view = await irt_quality.get_item_quality(mock_diag_item.item_id, db, mock_admin_context)
    assert item_view.state == "healthy"

    # 6. set_manual_override: LookupError -> 404
    mock_irt_svc = MagicMock()
    mock_irt_svc.manual_override = AsyncMock(side_effect=LookupError("Item not found"))
    monkeypatch.setattr(irt_quality, "IRTQualityService", lambda: mock_irt_svc)

    req_override = IRTManualOverrideRequest(state="quarantined", reason="audit quality check")
    with pytest.raises(HTTPException) as exc_ov:
        await irt_quality.set_manual_override(uuid4(), req_override, db, mock_admin_context)
    assert exc_ov.value.status_code == 404

    # 7. set_manual_override: success
    mock_diag_item.irt_quality_state = "quarantined"
    mock_irt_svc.manual_override = AsyncMock(return_value=mock_diag_item)
    res_ov = await irt_quality.set_manual_override(mock_diag_item.item_id, req_override, db, mock_admin_context)
    assert res_ov.state == "quarantined"

    # 8. clear_manual_override: LookupError -> 404
    mock_irt_svc.clear_override = AsyncMock(side_effect=LookupError("Item not found"))
    with pytest.raises(HTTPException) as exc_cl:
        await irt_quality.clear_manual_override(uuid4(), db, mock_admin_context)
    assert exc_cl.value.status_code == 404

    # 9. clear_manual_override: success
    mock_diag_item.irt_quality_state = "healthy"
    mock_irt_svc.clear_override = AsyncMock(return_value=mock_diag_item)
    res_cl = await irt_quality.clear_manual_override(mock_diag_item.item_id, db, mock_admin_context)
    assert res_cl.state == "healthy"


# ── CURRICULUM EXPANSION ROUTER ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_curriculum_expansion_router(monkeypatch, mock_admin_context):
    db = AsyncMock()

    # 1. get_scope_coverage
    mock_cur_svc = MagicMock()
    mock_cur_svc.coverage_for_scope = AsyncMock(return_value={"scope_id": "scope_1", "coverage": 0.95})
    monkeypatch.setattr(curriculum_expansion, "CurriculumExpansionService", lambda d: mock_cur_svc)

    cov = await curriculum_expansion.get_scope_coverage("scope_1", db)
    assert cov["coverage"] == 0.95

    # 2. capture_snapshots
    mock_snap = MagicMock()
    mock_snap.snapshot_id = uuid4()
    mock_snap.scope_id = "scope_1"
    mock_snap.language = "en"
    mock_snap.target_total = 100
    mock_snap.approved_total = 95
    mock_snap.published_total = 90
    mock_snap.gap_count = 5
    mock_snap.status = "active"
    mock_snap.captured_at = datetime.now(timezone.utc)
    mock_cur_svc.capture_snapshot = AsyncMock(return_value=mock_snap)

    body_snap = CoverageSnapshotRequest(scope_ids=["scope_1"], source_commit_sha="abc1234")
    snaps = await curriculum_expansion.capture_snapshots(body_snap, db)
    assert len(snaps) == 1
    assert snaps[0]["scope_id"] == "scope_1"

    # 3. create_expansion_plan
    mock_plan_run = MagicMock()
    mock_plan_run.run_id = uuid4()
    mock_plan_run.status = "planned"
    mock_plan_run.dry_run = True
    mock_plan_run.plan_json = {"steps": []}
    mock_cur_svc.build_expansion_plan = AsyncMock(return_value=mock_plan_run)

    body_plan = ExpansionPlanRequest(scope_ids=["scope_1"], languages=["en"], layers=["content"], dry_run=True)
    res_plan = await curriculum_expansion.create_expansion_plan(body_plan, mock_admin_context, db)
    assert res_plan.status == "planned"

    # 4. create_training_manifest
    mock_train_svc = MagicMock()
    mock_manifest = MagicMock()
    mock_manifest.manifest_id = uuid4()
    mock_manifest.dataset_version = "v1.0"
    mock_manifest.status = "draft"
    mock_manifest.artifact_count = 10
    mock_manifest.language_counts = {"en": 10}
    mock_manifest.scope_counts = {"scope_1": 10}
    mock_manifest.dataset_sha256 = None
    mock_manifest.output_path = None
    mock_manifest.created_by = "admin_123"
    mock_manifest.created_at = datetime.now(timezone.utc)
    mock_manifest.approved_by = None
    mock_manifest.approved_at = None
    mock_manifest.metadata_json = {}
    mock_train_svc.create_manifest = AsyncMock(return_value=mock_manifest)
    monkeypatch.setattr(curriculum_expansion, "TrainingDatasetGovernanceService", lambda d: mock_train_svc)

    body_manifest = TrainingManifestCreateRequest(
        dataset_version="v1.0",
        scope_ids=["scope_1"],
        languages=["en"],
    )
    res_man = await curriculum_expansion.create_training_manifest(body_manifest, mock_admin_context, db)
    assert res_man.dataset_version == "v1.0"

    # 5. get_training_manifest: 404 and found
    db.get = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_man:
        await curriculum_expansion.get_training_manifest(uuid4(), db)
    assert exc_man.value.status_code == 404

    db.get = AsyncMock(return_value=mock_manifest)
    res_get_man = await curriculum_expansion.get_training_manifest(mock_manifest.manifest_id, db)
    assert res_get_man.dataset_version == "v1.0"

    # 6. decide_training_manifest: LookupError -> 404, ValueError -> 409, success
    mock_train_svc.approve_manifest = AsyncMock(side_effect=LookupError("Not found"))
    body_dec = TrainingManifestApproveRequest(decision="approve", reason="Validated")
    with pytest.raises(HTTPException) as exc_dec_404:
        await curriculum_expansion.decide_training_manifest(uuid4(), body_dec, mock_admin_context, db)
    assert exc_dec_404.value.status_code == 404

    mock_train_svc.approve_manifest = AsyncMock(side_effect=ValueError("Invalid state"))
    with pytest.raises(HTTPException) as exc_dec_409:
        await curriculum_expansion.decide_training_manifest(uuid4(), body_dec, mock_admin_context, db)
    assert exc_dec_409.value.status_code == 409

    mock_manifest.status = "approved"
    mock_train_svc.approve_manifest = AsyncMock(return_value=mock_manifest)
    res_dec = await curriculum_expansion.decide_training_manifest(mock_manifest.manifest_id, body_dec, mock_admin_context, db)
    assert res_dec.status == "approved"

    # 7. export_training_manifest: LookupError -> 404, PermissionError -> 409, ValueError -> 422, success
    body_exp = DatasetExportRequest(output_name="export_v1.jsonl")
    mock_train_svc.export_manifest = AsyncMock(side_effect=LookupError("Not found"))
    with pytest.raises(HTTPException) as exc_exp_404:
        await curriculum_expansion.export_training_manifest(uuid4(), body_exp, db)
    assert exc_exp_404.value.status_code == 404

    mock_train_svc.export_manifest = AsyncMock(side_effect=PermissionError("Unapproved"))
    with pytest.raises(HTTPException) as exc_exp_409:
        await curriculum_expansion.export_training_manifest(uuid4(), body_exp, db)
    assert exc_exp_409.value.status_code == 409

    mock_train_svc.export_manifest = AsyncMock(side_effect=ValueError("Invalid export"))
    with pytest.raises(HTTPException) as exc_exp_422:
        await curriculum_expansion.export_training_manifest(uuid4(), body_exp, db)
    assert exc_exp_422.value.status_code == 422

    mock_manifest.status = "exported"
    mock_train_svc.export_manifest = AsyncMock(return_value=(mock_manifest, "/tmp/export.json"))
    res_exp = await curriculum_expansion.export_training_manifest(mock_manifest.manifest_id, body_exp, db)
    assert res_exp.status == "exported"
