"""Comprehensive unit tests covering content generation runs, planner, run lock, and reporter services."""
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.domain.content_coverage import ContentLayer
from app.models.content_factory import ContentGenerationRun, ContentGenerationTask
from app.services.content_generation_planner import (
    ContentGenerationPlanner,
    GenerationPlanResult,
    _topic_title,
)
from app.services.content_generation_reporter import (
    ContentGenerationReporter,
    GenerationReportData,
)
from app.services.content_generation_run_lock import (
    ContentGenerationRunLock,
    LockAcquisitionResult,
)
from app.services.content_generation_runs import (
    ContentGenerationRunService,
    _value,
)


# ============================================================================
# ContentGenerationRunLock Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_generation_run_lock():
    lock = ContentGenerationRunLock(ttl_minutes=60)
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    # 1. Acquire - active lock already held and not stale
    mock_run_with_lock = ContentGenerationRun(
        run_id=uuid.uuid4(),
        scope_id="all_scopes",
        run_metadata={
            "full_generation_lock": {
                "holder": "worker-1",
                "lock_holder": "worker-1",
                "lock_acquired_at": 10000000000.0,  # far future
                "lock_expires_at": 10000003600.0,
            }
        },

    )
    session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=mock_run_with_lock)
    )

    res_blocked = await lock.acquire(session, holder="worker-2")
    assert isinstance(res_blocked, LockAcquisitionResult)
    assert res_blocked.acquired is False
    assert res_blocked.error == "Lock already held"
    assert res_blocked.lock_holder == "worker-1"

    # 2. Acquire - stale lock released, and latest_run updated
    mock_run_stale = ContentGenerationRun(
        run_id=uuid.uuid4(),
        scope_id="all_scopes",
        run_metadata={
            "full_generation_lock": {
                "holder": "worker-1",
                "lock_acquired_at": 100.0,  # ancient past
                "lock_expires_at": 200.0,
            }
        },
    )
    session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=mock_run_stale)
    )
    res_acquired_update = await lock.acquire(session, holder="worker-2")
    assert res_acquired_update.acquired is True
    assert res_acquired_update.lock_holder == "worker-2"
    assert mock_run_stale.run_metadata["full_generation_lock"]["holder"] == "worker-2"

    # 3. Acquire - no run exists, placeholder created
    session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=None)
    )
    res_acquired_placeholder = await lock.acquire(session, holder="worker-3")
    assert res_acquired_placeholder.acquired is True
    assert res_acquired_placeholder.lock_holder == "worker-3"
    session.add.assert_called()

    # 4. Release - lock holder matches
    mock_run_held = ContentGenerationRun(
        run_id=uuid.uuid4(),
        scope_id="all_scopes",
        run_metadata={
            "full_generation_lock": {
                "holder": "worker-2",
                "lock_acquired_at": 500.0,
            }
        },
    )
    session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=mock_run_held)
    )
    assert await lock.release(session, holder="worker-2") is True
    assert mock_run_held.run_metadata["full_generation_lock"]["holder"] is None

    # 5. Release - lock holder mismatch or no run
    session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=mock_run_held)
    )
    assert await lock.release(session, holder="wrong-worker") is False

    session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=None)
    )
    assert await lock.release(session, holder="worker-2") is False


# ============================================================================
# ContentGenerationReporter Tests
# ============================================================================
def test_content_generation_reporter(tmp_path: Path):
    reporter = ContentGenerationReporter(base_dir=str(tmp_path / "reports"))

    data = GenerationReportData(
        run_id="run-123",
        scope_id="scope-456",
        status="succeeded",
        planned_tasks=5,
        executed_tasks=5,
        generated_artifacts=10,
        pending_review=2,
        validation_failed=1,
        source_blockers=0,
        staging_seed_results=10,
        staging_verification_passed=True,
        errors=["err1", "err2"],
        scope_readiness_before={"status": "partial"},
        scope_readiness_after={"status": "ready"},
        planned_tasks_list=[{"task_id": "t1", "layer": "diagnostic_items"}],
        executed_tasks_list=[{"task_id": "t1", "status": "succeeded"}],
        generated_artifacts_list=[{"art_id": "a1"}],
        pending_review_list=[{"art_id": "a1"}],
        validation_failed_list=[{"art_id": "a2"}],
        source_blockers_list=[],
        staging_seed_results_list=[{"art_id": "a1", "status": "seeded"}],
    )

    out_dir = reporter.write_report(data)
    assert out_dir.exists()
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "summary.json").exists()
    assert (out_dir / "errors.log").exists()
    assert (out_dir / "planned_tasks.csv").exists()
    assert (out_dir / "staging_verification.json").exists()

    # Empty list writes early return
    reporter._write_csv(out_dir / "empty.csv", [])
    reporter._write_csv(out_dir / "empty_row.csv", [{}])


# ============================================================================
# ContentGenerationPlanner Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_generation_planner():
    scope_registry = MagicMock()
    readiness_service = AsyncMock()
    source_context_service = AsyncMock()

    planner = ContentGenerationPlanner(
        scope_registry=scope_registry,
        readiness_service=readiness_service,
        source_context_service=source_context_service,
    )
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    run_id = uuid.uuid4()

    # 1. plan_missing_for_run - run not found
    session.get.return_value = None
    with pytest.raises(LookupError, match="Generation run .* not found"):
        await planner.plan_missing_for_run(session, run_id)

    # 2. plan_missing_for_run - full planning flow with skip & duplicate & create
    mock_run = ContentGenerationRun(
        run_id=run_id,
        scope_id="all_scopes",
        run_metadata={},
    )
    session.get.return_value = mock_run

    mock_topic = MagicMock(caps_ref="4.M.1", title="Numbers")
    mock_scope = MagicMock(
        scope_id="scope_math",
        grade=4,
        subject_code="MATH",
        language="en",
        topic_map=[mock_topic],
    )
    scope_registry.list_scopes.return_value = [mock_scope]
    scope_registry.get_scope.return_value = mock_scope

    # Readiness layers:
    # layer1: unplannable layer or target 0 -> ignored
    # layer2: missing_count <= 0 -> skipped coverage_green
    # layer3: source context failed -> skipped missing_source_context
    # layer4: existing task -> skipped duplicate_task
    # layer5: clean -> task created
    layer_ignored = MagicMock(layer="unplannable", target=0)
    layer_green = MagicMock(layer="diagnostic_items", target=5, approved=5, caps_ref="4.M.1")
    layer_ctx_fail = MagicMock(layer="lessons", target=5, approved=2, caps_ref="4.M.1")
    layer_dup = MagicMock(layer="assessment_blueprints", target=5, approved=2, caps_ref="4.M.1")
    layer_ok = MagicMock(layer="study_plan_templates", target=5, approved=2, caps_ref="4.M.1")

    readiness_report = MagicMock(
        layers=[layer_ignored, layer_green, layer_ctx_fail, layer_dup, layer_ok]
    )
    readiness_service.verify_scope.return_value = readiness_report

    # Context returns failed for layer3, ok for layer4 & layer5
    ctx_fail = MagicMock(passed=False, errors=["missing pdf"])
    ctx_ok = MagicMock(passed=True)
    source_context_service.build_context.side_effect = [ctx_fail, ctx_ok, ctx_ok]

    # Existing task returns existing for layer4, None for layer5
    existing_task = ContentGenerationTask(task_id=uuid.uuid4())
    session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=existing_task)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
    ]

    res_plan = await planner.plan_missing_for_run(session, run_id, actor_id="admin")
    assert isinstance(res_plan, GenerationPlanResult)
    assert len(res_plan.created_task_ids) == 1
    assert len(res_plan.missing) == 1
    assert any(s["reason"] == "coverage_green" for s in res_plan.skipped)
    assert any(s["reason"] == "missing_source_context" for s in res_plan.skipped)
    assert any(s["reason"] == "duplicate_task" for s in res_plan.skipped)
    assert mock_run.status == "planned"

    assert _topic_title(mock_scope, "4.M.1") == "Numbers"
    assert _topic_title(mock_scope, "4.M.2") == "4.M.2"


# ============================================================================
# ContentGenerationRunService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_generation_run_service():
    scope_registry = MagicMock()
    service = ContentGenerationRunService(scope_registry=scope_registry)
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    run_id = uuid.uuid4()
    task_id = uuid.uuid4()
    scope_id = "scope_math_g4"

    # 1. create_run
    run = await service.create_run(
        session,
        scope_id=scope_id,
        layers=[ContentLayer.DIAGNOSTIC_ITEMS],
        requested_by="admin",
        dry_run=True,
    )
    assert isinstance(run, ContentGenerationRun)
    assert run.status == "planned"
    scope_registry.validate_scope_exists.assert_called_with(scope_id)

    # 2. get_run & list_runs
    session.get.return_value = None
    with pytest.raises(LookupError, match="Generation run .* not found"):
        await service.get_run(session, run_id)

    session.get.return_value = run
    assert await service.get_run(session, run_id) == run

    session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[run])))
    )
    runs = await service.list_runs(session, scope_id=scope_id)
    assert len(runs) == 1

    # 3. create_tasks_for_run (when existing vs empty)
    mock_task = ContentGenerationTask(
        task_id=task_id,
        run_id=run_id,
        scope_id=scope_id,
        caps_ref="4.M.1",
        content_layer="diagnostic_items",
        status="queued",
        attempt_number=1,
        max_attempts=3,
    )
    # If existing tasks found
    session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_task])))
    )
    existing_tasks = await service.create_tasks_for_run(session, run_id)
    assert len(existing_tasks) == 1

    # If no existing tasks found
    session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    )
    scope_registry.get_scope_caps_refs.return_value = ["4.M.1"]
    new_tasks = await service.create_tasks_for_run(session, run_id)
    assert len(new_tasks) == 1
    assert new_tasks[0].caps_ref == "4.M.1"

    # 4. Task status state transitions: queued -> running -> succeeded -> failed
    session.get.return_value = mock_task
    assert (await service.mark_task_queued(session, task_id)).status == "queued"
    assert (await service.mark_task_running(session, task_id)).status == "running"
    succ = await service.mark_task_succeeded(session, task_id, ["art-1"])
    assert succ.status == "succeeded"
    assert succ.output_artifact_ids == ["art-1"]
    fail = await service.mark_task_failed(session, task_id, "error details")
    assert fail.status == "failed"
    assert fail.validation_failures == ["error details"]

    # Unsupported status / not found task
    with pytest.raises(ValueError, match="Unsupported task status"):
        await service._mark_task(session, task_id, "invalid_status")
    session.get.return_value = None
    with pytest.raises(LookupError, match="Generation task .* not found"):
        await service._mark_task(session, task_id, "queued")

    # 5. cancel_run
    session.get.return_value = run
    session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_task])))
    )
    mock_task.status = "running"
    cancelled_run = await service.cancel_run(session, run_id, actor_id="admin")
    assert cancelled_run.status == "cancelled"
    assert mock_task.status == "cancelled"

    # 6. retry_failed_tasks
    mock_task.status = "failed"
    mock_task.attempt_number = 1
    mock_task.max_attempts = 3
    retry_list = await service.retry_failed_tasks(session, run_id, actor_id="admin")
    assert len(retry_list) == 1
    assert retry_list[0].attempt_number == 2
    assert retry_list[0].status == "queued"

    assert _value(ContentLayer.DIAGNOSTIC_ITEMS) == "diagnostic_items"
    assert _value("lessons") == "lessons"
