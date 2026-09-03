"""Comprehensive endpoint unit tests for the Admin Content Factory Router."""
from __future__ import annotations

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_factory import (
    router,
    get_content_coverage_service,
    get_learner_read_service,
    get_content_factory_service,
    get_content_artifact_lifecycle_service,
    get_content_generation_run_service,
    get_content_generation_planner,
    get_content_generation_executor,
    get_staging_readiness_service,
    get_content_staging_seed_executor,
    get_content_staging_read_verification_service,
    get_production_promotion_gate,
    get_production_promotion_executor,
    get_production_read_verification_service,
    get_content_review_queue_service,
    get_content_reviewer_assignment_service,
    get_content_bulk_review_service,
)



from app.api_v2_deps.auth import require_admin, require_auth_context, AuthContext
from app.core.database import get_db


def _create_test_app(
    factory_service: Any | None = None,
    seed_executor: Any | None = None,
    promotion_executor: Any | None = None,
    review_queue_service: Any | None = None,
) -> FastAPI:
    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    async def override_db():
        return AsyncMock()

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = override_db

    if factory_service is not None:
        app.dependency_overrides[get_content_factory_service] = lambda: factory_service
    if seed_executor is not None:
        app.dependency_overrides[get_content_staging_seed_executor] = lambda: seed_executor
    if promotion_executor is not None:
        app.dependency_overrides[get_production_promotion_executor] = lambda: promotion_executor
    if review_queue_service is not None:
        app.dependency_overrides[get_content_review_queue_service] = lambda: review_queue_service

    return app


# ---------------------------------------------------------------------------
# Content Factory Health & Scopes Endpoints Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_content_factory_health():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["route_scope"] == "admin"


@pytest.mark.asyncio
async def test_content_factory_etl_status():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/etl/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "available"
        assert "pipeline_package" in data


@pytest.mark.asyncio
async def test_content_factory_list_scopes():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/scopes")
        assert resp.status_code == 200
        scopes = resp.json()
        assert isinstance(scopes, list)
        assert len(scopes) > 0


@pytest.mark.asyncio
async def test_content_factory_get_scope_not_found():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/scopes/non_existent_scope_123")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_get_scope_targets_not_found():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/scopes/non_existent_scope_123/targets")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_scope_coverage_not_found():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/scopes/non_existent_scope_123/coverage")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_validate_artifact_missing_fields():
    app = _create_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/admin/content-factory/validate-artifact",
            json={
                "artifact_json": {},
                "caps_ref": "4.M.1.1",
                "sources": [],
                "artifact_type": "lesson_content",
            },
        )
        assert resp.status_code in (200, 422)


# ---------------------------------------------------------------------------
# Artifacts, Staging & Production Endpoints Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_content_factory_get_artifact_not_found():
    mock_service = AsyncMock()
    mock_service.get_artifact.side_effect = LookupError("Artifact not found")
    app = _create_test_app(factory_service=mock_service)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/artifacts/{fake_id}")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_get_artifact_provenance_not_found():
    mock_service = AsyncMock()
    mock_service.get_artifact.side_effect = LookupError("Artifact not found")
    app = _create_test_app(factory_service=mock_service)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/artifacts/{fake_id}/provenance")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_get_review_bundle_not_found():
    mock_rq = AsyncMock()
    mock_rq.get_artifact_review_bundle.side_effect = LookupError("Review bundle not found")
    app = _create_test_app(review_queue_service=mock_rq)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/artifacts/{fake_id}/review-bundle")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_get_seed_run_not_found():
    mock_seed = AsyncMock()
    mock_seed.get_seed_run.side_effect = LookupError("Seed run not found")
    app = _create_test_app(seed_executor=mock_seed)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/seed-runs/{fake_id}")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_get_promotion_event_not_found():
    mock_promo = AsyncMock()
    mock_promo.get_promotion_event.side_effect = LookupError("Promotion event not found")
    app = _create_test_app(promotion_executor=mock_promo)
    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/promotion-events/{fake_id}")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_runs_endpoints():
    mock_run_service = AsyncMock()
    mock_run_service.get_run.side_effect = LookupError("Run not found")
    mock_run_service.cancel_run.side_effect = LookupError("Run not found")

    mock_planner = AsyncMock()
    mock_planner.plan_missing_for_run.side_effect = LookupError("Run not found")

    mock_executor = AsyncMock()
    mock_executor.execute_run.side_effect = LookupError("Run not found")

    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    app.dependency_overrides[get_content_generation_run_service] = lambda: mock_run_service
    app.dependency_overrides[get_content_generation_planner] = lambda: mock_planner
    app.dependency_overrides[get_content_generation_executor] = lambda: mock_executor

    fake_run_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/runs/{fake_run_id}")
        assert resp.status_code == 404

        resp = await client.post(f"/admin/content-factory/runs/{fake_run_id}/plan-missing")
        assert resp.status_code == 404

        resp = await client.post(f"/admin/content-factory/runs/{fake_run_id}/execute")
        assert resp.status_code == 404

        resp = await client.post(f"/admin/content-factory/runs/{fake_run_id}/cancel")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_tasks_endpoints():
    mock_db = AsyncMock()
    mock_db.get.return_value = None  # Task not found

    mock_executor = AsyncMock()
    mock_executor.execute_task.side_effect = LookupError("Task not found")

    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_content_generation_executor] = lambda: mock_executor

    fake_task_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/tasks/{fake_task_id}")
        assert resp.status_code == 404

        resp = await client.post(f"/admin/content-factory/tasks/{fake_task_id}/execute")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_content_factory_review_actions_endpoints():
    mock_lifecycle = AsyncMock()
    mock_lifecycle.submit_for_review.side_effect = LookupError("Artifact not found")

    mock_bulk = AsyncMock()
    mock_bulk.bulk_approve.side_effect = ValueError("No valid artifacts to approve")

    mock_queue = AsyncMock()
    page_mock = MagicMock()
    page_mock.items = []
    page_mock.total = 0
    page_mock.limit = 50
    page_mock.offset = 0
    mock_queue.list_queue.return_value = page_mock

    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    app.dependency_overrides[get_content_artifact_lifecycle_service] = lambda: mock_lifecycle
    app.dependency_overrides[get_content_bulk_review_service] = lambda: mock_bulk
    app.dependency_overrides[get_content_review_queue_service] = lambda: mock_queue

    fake_id = uuid.uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(f"/admin/content-factory/artifacts/{fake_id}/submit-review")
        assert resp.status_code == 409

        resp = await client.post(
            "/admin/content-factory/review/bulk-approve",
            json={"artifact_ids": [str(fake_id)], "notes": "LGTM"},
        )
        assert resp.status_code == 409

        resp = await client.get("/admin/content-factory/review-queue")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_content_factory_dependency_factories_coverage():
    from app.api_v2_routers import content_factory as cf_module
    mock_session = AsyncMock()
    cov_svc = cf_module.get_content_coverage_service(mock_session)
    assert cov_svc is not None
    assert cf_module.get_content_generation_run_service() is not None
    assert cf_module.get_content_factory_service() is not None
    assert cf_module.get_content_artifact_lifecycle_service() is not None
    assert cf_module.get_content_factory_orchestrator() is not None
    assert cf_module.get_content_generation_planner() is not None
    assert cf_module.get_content_generation_executor() is not None
    assert cf_module.get_seed_promotion_service(cov_svc) is not None
    assert cf_module.get_staging_readiness_service() is not None
    assert cf_module.get_content_review_queue_service() is not None
    assert cf_module.get_content_reviewer_assignment_service() is not None
    assert cf_module.get_content_bulk_review_service() is not None
    assert cf_module.get_content_staging_seed_executor() is not None
    assert cf_module.get_content_staging_read_verification_service() is not None
    gate = cf_module.get_production_promotion_gate(cov_svc)
    assert gate is not None
    assert cf_module.get_production_promotion_executor(gate) is not None
    assert cf_module.get_production_read_verification_service() is not None


from dataclasses import dataclass, field

@dataclass
class _TransitionDummy:
    artifact_id: Any = None
    previous_status: Any = None
    new_status: Any = None
    status: Any = "rejected"
    errors: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


@pytest.mark.asyncio
async def test_content_factory_review_actions_and_workload():
    fake_id = uuid.uuid4()
    mock_trans_rej = _TransitionDummy(artifact_id=fake_id, status="rejected")
    mock_trans_quar = _TransitionDummy(artifact_id=fake_id, status="quarantined")

    mock_lifecycle = AsyncMock()
    mock_lifecycle.reject_artifact.return_value = mock_trans_rej
    mock_lifecycle.quarantine_artifact.return_value = mock_trans_quar

    mock_bulk = AsyncMock()
    mock_bulk.bulk_reject.side_effect = ValueError("Bulk reject failed")
    mock_bulk.bulk_quarantine.side_effect = ValueError("Bulk quarantine failed")

    mock_queue = AsyncMock()
    from app.domain.content_factory_schemas import ReviewSummaryResponse
    mock_queue.get_review_summary.return_value = ReviewSummaryResponse(
        pending_review=5, low_risk=2, medium_risk=2, high_risk=1, critical_risk=0, assigned=3,
    )

    mock_assign = MagicMock()
    mock_assign.assign_artifact = AsyncMock(side_effect=LookupError("Artifact not found"))
    mock_assign.list_assignments = AsyncMock(return_value=[])
    from app.domain.content_factory_schemas import ReviewerWorkloadResponse
    mock_assign.get_reviewer_workload = AsyncMock(return_value=ReviewerWorkloadResponse(
        reviewer_id="rev-1", assigned=1, in_review=1, overdue=0, total_open=2,
    ))



    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    app.dependency_overrides[get_content_artifact_lifecycle_service] = lambda: mock_lifecycle
    app.dependency_overrides[get_content_bulk_review_service] = lambda: mock_bulk
    app.dependency_overrides[get_content_review_queue_service] = lambda: mock_queue
    app.dependency_overrides[get_content_reviewer_assignment_service] = lambda: mock_assign

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(f"/admin/content-factory/artifacts/{fake_id}/reject", json={"reason": "bad"})
        assert resp.status_code == 200

        resp = await client.post(f"/admin/content-factory/artifacts/{fake_id}/quarantine", json={"reason": "flagged"})
        assert resp.status_code == 200

        resp = await client.get("/admin/content-factory/review-summary")
        assert resp.status_code == 200

        resp = await client.post("/admin/content-factory/review/bulk-reject", json={"artifact_ids": [str(fake_id)], "reason": "bad"})
        assert resp.status_code == 409

        resp = await client.post("/admin/content-factory/review/bulk-quarantine", json={"artifact_ids": [str(fake_id)], "reason": "flag"})
        assert resp.status_code == 409

        resp = await client.post("/admin/content-factory/review-assignments", json={"artifact_id": str(fake_id), "reviewer_id": "rev-1"})
        assert resp.status_code == 404

        resp = await client.get("/admin/content-factory/review-assignments")
        assert resp.status_code == 200

        resp = await client.get("/admin/content-factory/reviewers/rev-1/workload")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_content_factory_staging_and_promotion_routes():
    fake_id = uuid.uuid4()
    from app.domain.content_factory_schemas import (
        StagingReadVerificationResponse,
        ProductionRollbackResultResponse,
        ProductionReadVerificationReportResponse,
    )

    mock_seed = AsyncMock()
    mock_seed.get_seed_run_items.return_value = []
    mock_seed.rollback_seed_run.side_effect = LookupError("Seed run not found")

    mock_staging_ver = AsyncMock()
    mock_staging_ver.verify_seed_run.return_value = StagingReadVerificationResponse(
        seed_run_id=fake_id,
        passed=True,
        verified_count=5,
    )

    mock_promo = AsyncMock()
    mock_promo.rollback_promotion.return_value = ProductionRollbackResultResponse(
        promotion_event_id=fake_id,
        status="rolled_back",
        rolled_back_count=1,
    )

    mock_prod_ver = AsyncMock()
    mock_prod_ver.verify_promotion_event.return_value = ProductionReadVerificationReportResponse(
        promotion_event_id=fake_id,
        passed=True,
        verified_count=5,
    )

    mock_db = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_db.scalars.return_value = mock_scalars

    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_content_staging_seed_executor] = lambda: mock_seed
    app.dependency_overrides[get_content_staging_read_verification_service] = lambda: mock_staging_ver
    app.dependency_overrides[get_production_promotion_executor] = lambda: mock_promo
    app.dependency_overrides[get_production_read_verification_service] = lambda: mock_prod_ver

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/admin/content-factory/seed-runs/{fake_id}/items")
        assert resp.status_code == 200

        resp = await client.post(f"/admin/content-factory/seed-runs/{fake_id}/verify")
        assert resp.status_code == 200

        resp = await client.post(f"/admin/content-factory/seed-runs/{fake_id}/rollback?reason=test")
        assert resp.status_code == 404

        resp = await client.post(f"/admin/content-factory/promotion-events/{fake_id}/verify")
        assert resp.status_code == 200

        resp = await client.post(f"/admin/content-factory/promotion-events/{fake_id}/rollback", json={"reason": "revert"})
        assert resp.status_code == 200


def test_content_factory_helper_functions():
    from datetime import datetime, timezone
    from app.api_v2_routers import content_factory as cf_module

    assert isinstance(cf_module._mcp_runtime_imported(), bool)
    assert isinstance(cf_module._generation_enabled(), bool)

    now = datetime.now(timezone.utc)


    # _run_response
    mock_run = MagicMock(run_id=uuid.uuid4(), scope_id="scope1", status="pending", requested_by="user1", run_metadata={"k": "v"})
    rr = cf_module._run_response(mock_run)
    assert rr.run_id == mock_run.run_id

    # _task_response
    mock_task = MagicMock(task_id=uuid.uuid4(), run_id=uuid.uuid4(), scope_id="scope1", caps_ref="4.M.1.1", content_layer="foundation", status="pending", attempt_number=1, max_attempts=3, output_artifact_ids=[], validation_failures=[])
    tr = cf_module._task_response(mock_task)
    assert tr.task_id == mock_task.task_id

    # _artifact_response
    mock_art = MagicMock(artifact_id=uuid.uuid4(), scope_id="scope1", content_layer="foundation", artifact_type="diagnostic_item", caps_ref="4.M.1.1", status="approved", artifact_hash="h1", source_snapshot_hash="s1")
    ar = cf_module._artifact_response(mock_art)
    assert ar.artifact_id == mock_art.artifact_id

    # _seed_run_response
    mock_sr = MagicMock(seed_run_id=uuid.uuid4(), scope_id="scope1", dry_run=False, status="completed", summary={"seeded": 5})
    srr = cf_module._seed_run_response(mock_sr)
    assert srr.seed_run_id == mock_sr.seed_run_id

    # _staging_verification_run_response
    mock_svr = MagicMock(run_id=uuid.uuid4(), status="passed", summary_json={"passed": True}, created_by="user1", created_at=now, completed_at=now)
    svrr = cf_module._staging_verification_run_response(mock_svr)
    assert svrr.run_id == mock_svr.run_id

    # _review_queue_item_response
    mock_rqi = MagicMock(
        artifact_id=uuid.uuid4(),
        scope_id="scope1",
        content_layer="foundation",
        artifact_type="diagnostic_item",
        caps_ref="4.M.1.1",
        status="pending",
        risk_level="low",
        risk_reasons=[],
        validation_status="passed",
        provenance_status="verified",
        reviewer_id="rev1",
        created_at=now,
    )
    rqir = cf_module._review_queue_item_response(mock_rqi)
    assert rqir.artifact_id == mock_rqi.artifact_id

    # _assignment_response
    mock_as = MagicMock(id=uuid.uuid4(), artifact_id=uuid.uuid4(), assigned_to="rev1", assigned_by="user1", priority="high", status="active", due_by=now)
    asr = cf_module._assignment_response(mock_as)
    assert asr.id == mock_as.id

    assert cf_module._value("test_str") == "test_str"
    enum_mock = MagicMock(value="val_str")
    assert cf_module._value(enum_mock) == "val_str"


@pytest.mark.asyncio
async def test_content_factory_all_staging_verification_and_previews():
    fake_run_id = uuid.uuid4()
    mock_db = AsyncMock()
    mock_exec_res = MagicMock()
    mock_exec_res.all.return_value = []
    mock_exec_res.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_exec_res
    mock_db.scalars.return_value.all.return_value = []


    from app.services.content_staging_readiness import (
        AllScopeStagingVerificationReport,
        ScopeStagingVerificationReport,
        StagingReadinessStatus,
    )
    from app.domain.content_factory_schemas import (
        StagingSeedPlanResponse,
        StagingSeedRunResultResponse,
        ContentFactoryReportResponse,
    )

    scope_report = ScopeStagingVerificationReport(
        scope_id="grade4_maths",
        status=StagingReadinessStatus.READY_FOR_STAGING,
        can_seed_staging=True,
        can_promote_production=True,
        blockers=[],
        layers=[],
        summary={},
    )

    mock_readiness = AsyncMock()
    mock_readiness.get_scope_readiness.return_value = scope_report
    mock_readiness.get_run_report.side_effect = LookupError("Run report not found")
    mock_readiness.verify_scope.return_value = scope_report
    mock_readiness.list_runs.return_value = []
    mock_readiness.verify_all_scopes.return_value = AllScopeStagingVerificationReport(
        run_id=fake_run_id,
        status=StagingReadinessStatus.READY_FOR_STAGING.value,
        can_seed_staging=True,
        can_promote_production=True,
        scopes=[scope_report],
    )

    mock_plan = MagicMock(scope_id="grade4_maths", layers=["foundation"], seedable=[], skipped=[])
    mock_seed = AsyncMock()
    mock_seed.dry_run_seed = AsyncMock(return_value=mock_plan)

    @dataclass
    class _SeedResultDummy:
        seed_run_id: uuid.UUID = fake_run_id
        scope_id: str = "grade4_maths"
        status: str = "completed"
        seeded_count: int = 5
        skipped_count: int = 0
        errors: list[str] = field(default_factory=list)

    mock_seed.seed_staging = AsyncMock(return_value=_SeedResultDummy())


    mock_factory = AsyncMock()
    mock_factory.get_content_factory_report.return_value = ContentFactoryReportResponse(
        scope_id="grade4_maths",
        generation_enabled=True,
        coverage={},
        run_count=1,
        review_queue_count=0,
    )
    mock_factory.get_staging_preview.return_value = {"scope_id": "grade4_maths", "items": []}
    mock_factory.get_staging_preview_by_caps.return_value = {"scope_id": "grade4_maths", "caps_ref": "4.M.1.1", "items": []}
    mock_factory.get_production_preview.return_value = {"scope_id": "grade4_maths", "items": []}
    mock_factory.get_production_preview_by_caps.return_value = {"scope_id": "grade4_maths", "caps_ref": "4.M.1.1", "items": []}

    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    mock_cov_model = MagicMock()
    mock_cov_model.model_dump.return_value = {"scope_id": "grade4_maths", "total": 10}
    mock_cov = AsyncMock()
    mock_cov.get_scope_coverage = AsyncMock(return_value=mock_cov_model)

    mock_learner_read = AsyncMock()
    mock_learner_read.get_scope_content_summary = AsyncMock(return_value={"scope_id": "grade4_maths", "items": []})
    mock_learner_read.get_diagnostic_items = AsyncMock(return_value=[])
    mock_learner_read.get_lessons = AsyncMock(return_value=[])

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_content_coverage_service] = lambda: mock_cov
    app.dependency_overrides[get_staging_readiness_service] = lambda: mock_readiness
    app.dependency_overrides[get_content_staging_seed_executor] = lambda: mock_seed
    app.dependency_overrides[get_content_factory_service] = lambda: mock_factory
    app.dependency_overrides[get_learner_read_service] = lambda: mock_learner_read




    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/admin/content-factory/staging-verification/all-scopes")
        assert resp.status_code == 200

        resp = await client.get("/admin/content-factory/staging-verification/runs")
        assert resp.status_code == 200

        resp = await client.get(f"/admin/content-factory/staging-verification/runs/{fake_run_id}")
        assert resp.status_code == 404

        resp = await client.post("/admin/content-factory/scopes/grade4_maths/staging-verification")
        assert resp.status_code == 200

        resp = await client.get("/admin/content-factory/scopes/grade4_maths/staging-readiness")
        assert resp.status_code == 200

        resp = await client.post("/admin/content-factory/scopes/grade4_maths/dry-run-seed")
        assert resp.status_code == 200

        resp = await client.post("/admin/content-factory/scopes/grade4_maths/seed-staging")
        assert resp.status_code == 200

        resp = await client.get("/admin/content-factory/reports/grade4_maths")
        assert resp.status_code == 200

        resp = await client.get("/admin/content-factory/staging-preview/scopes/grade4_maths")
        assert resp.status_code == 200

        resp = await client.get("/admin/content-factory/staging-preview/scopes/grade4_maths/caps/4.M.1.1")
        assert resp.status_code == 200

        resp = await client.get("/admin/content-factory/production-preview/scopes/grade4_maths")
        assert resp.status_code == 200

        resp = await client.get("/admin/content-factory/production-preview/scopes/grade4_maths/caps/4.M.1.1")
        assert resp.status_code == 200



@pytest.mark.asyncio
async def test_content_factory_full_generation_routes(monkeypatch):
    monkeypatch.setenv("CONTENT_FACTORY_GENERATION_ENABLED", "true")
    monkeypatch.setenv("CONTENT_FACTORY_PROVIDER", "deterministic")

    fake_run_id = uuid.uuid4()
    mock_run = MagicMock(run_id=fake_run_id, scope_id="all_scopes", status="queued", requested_by="user1", run_metadata={})

    mock_db = AsyncMock()
    mock_db.get.return_value = mock_run
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_run]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_list = await client.get("/admin/content-factory/full-generation/runs")
        assert resp_list.status_code == 200

        resp_get = await client.get(f"/admin/content-factory/full-generation/runs/{fake_run_id}")
        assert resp_get.status_code == 200

        resp_rep = await client.get(f"/admin/content-factory/full-generation/runs/{fake_run_id}/report")
        assert resp_rep.status_code == 200

        resp_start = await client.post("/admin/content-factory/full-generation/start", json={"run_id": str(fake_run_id)})
        assert resp_start.status_code == 200

        resp_cancel = await client.post(f"/admin/content-factory/full-generation/runs/{fake_run_id}/cancel")
        assert resp_cancel.status_code == 200

@pytest.mark.asyncio
async def test_content_factory_runs_and_tasks_success_flow(monkeypatch):
    monkeypatch.setenv("CONTENT_FACTORY_GENERATION_ENABLED", "true")
    fake_run_id = uuid.uuid4()
    fake_task_id = uuid.uuid4()
    fake_art_id = uuid.uuid4()

    mock_run = MagicMock(run_id=fake_run_id, scope_id="grade_4_mathematics", status="queued", requested_by="user1", run_metadata={})
    mock_task = MagicMock(task_id=fake_task_id, run_id=fake_run_id, scope_id="grade_4_mathematics", caps_ref="4.M.1.1", content_layer="foundation", status="queued", attempt_number=1, max_attempts=3, output_artifact_ids=[], validation_failures=[])
    mock_art = MagicMock(artifact_id=fake_art_id, scope_id="grade_4_mathematics", content_layer="foundation", artifact_type="diagnostic_item", caps_ref="4.M.1.1", status="approved", artifact_hash="h1", source_snapshot_hash="s1")

    mock_run_service = AsyncMock()
    mock_run_service.create_run.return_value = mock_run
    mock_run_service.get_run.return_value = mock_run
    mock_run_service.get_run_tasks.return_value = [mock_task]
    mock_run_service.cancel_run.return_value = mock_run
    mock_run_service.retry_failed_tasks.return_value = [mock_task]

    mock_plan = MagicMock(run_id=fake_run_id, created_task_ids=[fake_task_id], skipped=[], missing=[])
    mock_planner = AsyncMock()
    mock_planner.plan_missing_for_run.return_value = mock_plan

    mock_exec_res = MagicMock(run_id=fake_run_id, task_id=fake_task_id, status="succeeded", summary={"tasks": 1}, artifact_ids=[fake_art_id], errors=[], provider="deterministic", mode="test")
    mock_executor = AsyncMock()
    mock_executor.execute_run.return_value = mock_exec_res
    mock_executor.execute_task.return_value = mock_exec_res
    mock_executor.execution_report.return_value = {
        "run_id": str(fake_run_id), "status": "completed", "tasks": 1, "queued": 0, "succeeded": 1, "failed": 0, "skipped": 0, "artifacts": 1,
    }

    mock_db = AsyncMock()
    mock_db.get.return_value = mock_task
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_art]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_content_generation_run_service] = lambda: mock_run_service
    app.dependency_overrides[get_content_generation_planner] = lambda: mock_planner
    app.dependency_overrides[get_content_generation_executor] = lambda: mock_executor

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create run
        resp = await client.post(
            "/admin/content-factory/runs",
            json={"scope_id": "grade_4_mathematics", "layers": ["diagnostic_items"], "dry_run": True},
        )
        assert resp.status_code == 200

        # Get run tasks
        resp = await client.get(f"/admin/content-factory/runs/{fake_run_id}/tasks")
        assert resp.status_code == 200

        # Plan missing
        resp = await client.post(f"/admin/content-factory/runs/{fake_run_id}/plan-missing")
        assert resp.status_code == 200

        # Execute run
        resp = await client.post(f"/admin/content-factory/runs/{fake_run_id}/execute")
        assert resp.status_code == 200

        # Execute task
        resp = await client.post(f"/admin/content-factory/tasks/{fake_task_id}/execute")
        assert resp.status_code == 200

        # Get task
        resp = await client.get(f"/admin/content-factory/tasks/{fake_task_id}")
        assert resp.status_code == 200

        # Execution report
        resp = await client.get(f"/admin/content-factory/runs/{fake_run_id}/execution-report")
        assert resp.status_code == 200

        # Cancel run
        resp = await client.post(f"/admin/content-factory/runs/{fake_run_id}/cancel")
        assert resp.status_code == 200

        # Retry failed
        resp = await client.post(f"/admin/content-factory/runs/{fake_run_id}/retry-failed")
        assert resp.status_code == 200

        # List artifacts
        resp = await client.get("/admin/content-factory/artifacts?scope_id=grade_4_mathematics&status=approved")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_content_factory_reviews_and_full_generation_plan():
    fake_art_id = uuid.uuid4()
    fake_as_id = uuid.uuid4()

    from app.domain.content_factory_schemas import (
        ArtifactReviewBundleResponse,
        ReviewRiskResponse,
        ReviewAssignmentResponse,
        BulkReviewResponse,
    )

    mock_bundle = ArtifactReviewBundleResponse(
        artifact={"artifact_id": str(fake_art_id)},
        validation_report=None,
        provenance={"sources": []},
        sources=[],
        review_risk=ReviewRiskResponse(level="low", score=0, reasons=[]),
        generation_metadata={},
        prior_review_events=[],
        similar_artifacts=[],
    )

    mock_queue = MagicMock()
    mock_queue.get_artifact_review_bundle = AsyncMock(return_value=mock_bundle)


    from app.domain.content_factory_schemas import ReviewAssignmentResponse, BulkReviewResponse

    @dataclass
    class _BulkAssignDummy:
        status: str = "completed"
        artifact_ids: list[Any] = field(default_factory=list)
        errors: list[str] = field(default_factory=list)
        summary: dict[str, int] = field(default_factory=dict)

    mock_assign = MagicMock()
    mock_assign.assign_artifact = AsyncMock(return_value=MagicMock(
        id=fake_as_id, artifact_id=fake_art_id, assigned_to="rev1", assigned_by="user1", priority="high", status="active", due_by=None,
    ))
    mock_assign.bulk_assign = AsyncMock(return_value=_BulkAssignDummy(artifact_ids=[fake_art_id]))


    mock_bulk_res = _BulkAssignDummy(status="completed", artifact_ids=[fake_art_id], errors=[], summary={})
    mock_bulk = AsyncMock()
    mock_bulk.bulk_assign = AsyncMock(return_value=mock_bulk_res)
    mock_bulk.bulk_approve = AsyncMock(return_value=mock_bulk_res)
    mock_bulk.bulk_reject = AsyncMock(return_value=mock_bulk_res)
    mock_bulk.bulk_quarantine = AsyncMock(return_value=mock_bulk_res)



    mock_db = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_content_review_queue_service] = lambda: mock_queue
    app.dependency_overrides[get_content_reviewer_assignment_service] = lambda: mock_assign
    app.dependency_overrides[get_content_bulk_review_service] = lambda: mock_bulk

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Review bundle
        resp = await client.get(f"/admin/content-factory/artifacts/{fake_art_id}/review-bundle")
        assert resp.status_code == 200

        # Assign artifact
        resp = await client.post(
            "/admin/content-factory/review-assignments",
            json={"artifact_id": str(fake_art_id), "reviewer_id": "rev1", "priority": "high"},
        )
        assert resp.status_code == 200

        # Bulk assign
        resp = await client.post(
            "/admin/content-factory/review-assignments/bulk",
            json={"artifact_ids": [str(fake_art_id)], "reviewer_id": "rev1", "priority": "high"},
        )
        assert resp.status_code == 200

        # Bulk approve
        resp = await client.post(
            "/admin/content-factory/review/bulk-approve",
            json={"artifact_ids": [str(fake_art_id)], "notes": "LGTM"},
        )
        assert resp.status_code == 200

        # Bulk reject
        resp = await client.post(
            "/admin/content-factory/review/bulk-reject",
            json={"artifact_ids": [str(fake_art_id)], "reason": "Formatting issues"},
        )
        assert resp.status_code == 200

        # Bulk quarantine
        resp = await client.post(
            "/admin/content-factory/review/bulk-quarantine",
            json={"artifact_ids": [str(fake_art_id)], "reason": "Suspicious"},
        )
        assert resp.status_code == 200

        # Plan full generation
        with patch("app.services.content_generation_planner.ContentGenerationPlanner.plan_missing_for_run") as mock_plan_run:
            mock_plan_run.return_value = MagicMock(created_task_ids=[fake_art_id], skipped=[], missing=[])
            resp = await client.post("/admin/content-factory/full-generation/plan")
            assert resp.status_code == 200


@pytest.mark.asyncio
async def test_content_factory_additional_edge_cases_and_error_branches(monkeypatch):
    fake_id = uuid.uuid4()
    mock_db = AsyncMock()

    mock_cov = AsyncMock()
    mock_cov.get_caps_ref_coverage.side_effect = LookupError("CAPS ref not found")

    mock_run_service = AsyncMock()
    mock_run_service.create_run.return_value = MagicMock(run_id=fake_id, scope_id="s1", status="queued", requested_by="u1", run_metadata={})

    from app.services.content_generation_executor import GenerationDisabledError
    mock_executor = AsyncMock()
    mock_executor.execute_run.side_effect = GenerationDisabledError("Disabled")
    mock_executor.execute_task.side_effect = GenerationDisabledError("Disabled")
    mock_executor.execution_report.side_effect = LookupError("Report not found")

    mock_lifecycle = AsyncMock()
    from dataclasses import dataclass, field
    @dataclass
    class _Trans:
        artifact_id: Any = fake_id
        previous_status: Any = "draft"
        new_status: Any = "in_review"
        status: Any = "in_review"
        errors: list[Any] = field(default_factory=list)
        summary: dict[str, Any] = field(default_factory=dict)
    mock_lifecycle.submit_for_review.return_value = _Trans()


    @dataclass
    class _SeedRunGetDummy:
        seed_run_id: Any = fake_id
        scope_id: Any = "s1"
        status: Any = "completed"
        seeded_count: Any = 5
        skipped_count: Any = 0
        errors: list[Any] = field(default_factory=list)

    mock_seed = AsyncMock()
    mock_seed.get_seed_run.return_value = _SeedRunGetDummy()
    @dataclass
    class _RollbackSeed:
        seed_run_id: Any = fake_id
        status: Any = "rolled_back"
        rolled_back_count: Any = 5
    mock_seed.rollback_seed_run.return_value = _RollbackSeed()

    @dataclass
    class _PromoGetDummy:
        promotion_event_id: Any = fake_id
        scope_id: Any = "s1"
        status: Any = "promoted"
        promoted_count: Any = 1
        skipped_count: Any = 0
        errors: list[Any] = field(default_factory=list)

    mock_promo = AsyncMock()
    mock_promo.get_promotion_event.return_value = _PromoGetDummy()
    @dataclass
    class _RollbackPromo:
        promotion_event_id: Any = fake_id
        status: Any = "rolled_back"
        rolled_back_count: Any = 1
    mock_promo.rollback_promotion.return_value = _RollbackPromo()


    mock_staging_ver = MagicMock()
    from app.domain.content_factory_schemas import StagingReadVerificationResponse, ProductionReadVerificationReportResponse
    @dataclass
    class _ScopeVerReportDummy:
        scope_id: str = "grade4_maths"
        passed: bool = True
        staged_artifacts_count: int = 5
        errors: list[str] = field(default_factory=list)

    mock_staging_ver.verify_scope_staging = AsyncMock(return_value=_ScopeVerReportDummy())
    mock_staging_ver.verify_seed_run = AsyncMock(return_value=StagingReadVerificationResponse(seed_run_id=fake_id, passed=True, verified_count=5))




    mock_prod_ver = AsyncMock()
    mock_prod_ver.verify_promotion_event.return_value = ProductionReadVerificationReportResponse(promotion_event_id=fake_id, passed=True, verified_count=1)

    app = FastAPI()
    app.include_router(router)

    async def override_admin():
        return AuthContext(
            user_id=str(uuid.uuid4()),
            role="admin",
            email="admin@eduboost.co.za",
            token_type="access",
            raw_claims={"role": "admin", "permissions": ["admin:all"]},
            jti=str(uuid.uuid4()),
        )

    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[require_auth_context] = override_admin
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_content_coverage_service] = lambda: mock_cov
    app.dependency_overrides[get_content_generation_run_service] = lambda: mock_run_service
    app.dependency_overrides[get_content_generation_executor] = lambda: mock_executor
    app.dependency_overrides[get_content_artifact_lifecycle_service] = lambda: mock_lifecycle
    app.dependency_overrides[get_content_staging_seed_executor] = lambda: mock_seed
    app.dependency_overrides[get_production_promotion_executor] = lambda: mock_promo
    app.dependency_overrides[get_content_staging_read_verification_service] = lambda: mock_staging_ver
    app.dependency_overrides[get_production_read_verification_service] = lambda: mock_prod_ver

    # 1. Test when generation is disabled
    monkeypatch.setenv("CONTENT_FACTORY_GENERATION_ENABLED", "false")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Caps ref coverage not found
        resp = await client.get("/admin/content-factory/scopes/grade4_maths/caps/4.M.1.1/coverage")
        assert resp.status_code == 404


        # Validate artifact payload
        resp = await client.post(
            "/admin/content-factory/validate-artifact",
            json={
                "artifact_type": "diagnostic_item",
                "artifact_json": {
                    "question": "What is 2+2?",
                    "options": ["3", "4", "5"],
                    "correct_answer": "4",
                    "explanation": "2+2=4",
                    "distractor_rationales": {"3": "off by 1", "5": "off by 1"},
                },
                "caps_ref": "4.M.1.1",
                "min_sources": 0,
                "sources": [],
            },
        )
        assert resp.status_code == 200

        # Create generation run when disabled and dry_run=False
        resp = await client.post(
            "/admin/content-factory/runs",
            json={"scope_id": "s1", "layers": ["diagnostic_items"], "dry_run": False},
        )
        assert resp.status_code == 409

        # Execute run disabled
        resp = await client.post(f"/admin/content-factory/runs/{fake_id}/execute")
        assert resp.status_code == 409

        # Execute task disabled
        resp = await client.post(f"/admin/content-factory/tasks/{fake_id}/execute")
        assert resp.status_code == 409

        # Execution report not found
        resp = await client.get(f"/admin/content-factory/runs/{fake_id}/execution-report")
        assert resp.status_code == 404

        # Submit artifact for review success
        resp = await client.post(f"/admin/content-factory/artifacts/{fake_id}/submit-review")
        assert resp.status_code == 200

        # Get seed run success
        resp = await client.get(f"/admin/content-factory/seed-runs/{fake_id}")
        assert resp.status_code == 200

        # Rollback seed run success
        resp = await client.post(f"/admin/content-factory/seed-runs/{fake_id}/rollback?reason=test")
        assert resp.status_code == 200

        # Staging read verification scope
        resp = await client.get("/admin/content-factory/scopes/grade4_maths/staging-read-verification")
        assert resp.status_code == 200

        # Full generation start when disabled
        resp = await client.post("/admin/content-factory/full-generation/start", json={"run_id": str(fake_id)})
        assert resp.status_code == 403

        # Full generation error branches
        monkeypatch.setenv("CONTENT_FACTORY_GENERATION_ENABLED", "true")
        monkeypatch.setenv("CONTENT_FACTORY_PROVIDER", "llm")

        resp = await client.post("/admin/content-factory/full-generation/start", json={"run_id": str(fake_id), "confirmation": "WRONG"})
        assert resp.status_code == 400

        resp = await client.post(
            "/admin/content-factory/full-generation/start",
            json={"confirmation": "GENERATE OUTSTANDING CONTENT FOR ALL CONFIGURED SCOPES"},
        )
        assert resp.status_code == 400

        mock_db.get.return_value = None
        resp = await client.post(
            "/admin/content-factory/full-generation/start",
            json={"run_id": str(fake_id), "confirmation": "GENERATE OUTSTANDING CONTENT FOR ALL CONFIGURED SCOPES"},
        )
        assert resp.status_code == 404

        resp = await client.get(f"/admin/content-factory/full-generation/runs/{fake_id}")
        assert resp.status_code == 404

        resp = await client.get(f"/admin/content-factory/full-generation/runs/{fake_id}/report")
        assert resp.status_code == 404

        resp = await client.post(f"/admin/content-factory/full-generation/runs/{fake_id}/cancel")
        assert resp.status_code == 404

        resp = await client.post(f"/admin/content-factory/full-generation/runs/{fake_id}/resume")
        assert resp.status_code == 404












