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
from app.services.content_generation_runs import (
    ContentGenerationRunService,
    _value,
)


@pytest.mark.asyncio
async def test_content_generation_run_service_lifecycle():
    scope_registry = MagicMock()
    scope_registry.validate_scope_exists.return_value = None
    scope_registry.get_scope_caps_refs.return_value = ["4.M.1.1", "4.M.1.2"]

    service = ContentGenerationRunService(scope_registry=scope_registry)
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()

    # 1. create_run dry run
    run = await service.create_run(
        session,
        scope_id="scope_math_g4",
        layers=[ContentLayer.DIAGNOSTIC_ITEMS],
        requested_by="admin_user",
        dry_run=True,
    )
    assert run.status == "planned"
    assert run.scope_id == "scope_math_g4"

    # create_run live
    run_live = await service.create_run(
        session,
        scope_id="scope_math_g4",
        layers=[ContentLayer.DIAGNOSTIC_ITEMS],
        requested_by="admin_user",
        dry_run=False,
    )
    assert run_live.status == "created"

    # 2. get_run found and not found
    session.get.return_value = run
    found = await service.get_run(session, run.run_id)
    assert found == run

    session.get.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await service.get_run(session, uuid.uuid4())

    # 3. list_runs
    list_res = MagicMock()
    list_res.scalars.return_value.all.return_value = [run]
    session.execute.return_value = list_res
    runs = await service.list_runs(session, scope_id="scope_math_g4")
    assert len(runs) == 1

    # 4. create_tasks_for_run (empty existing vs existing)
    session.get.return_value = run
    task_res_empty = MagicMock()
    task_res_empty.scalars.return_value.all.return_value = []
    session.execute.return_value = task_res_empty

    tasks = await service.create_tasks_for_run(session, run.run_id)
    assert len(tasks) == 2  # 2 caps_refs * 1 layer

    # If existing tasks present, returns existing
    task_res_existing = MagicMock()
    task_res_existing.scalars.return_value.all.return_value = tasks
    session.execute.return_value = task_res_existing
    existing_tasks = await service.create_tasks_for_run(session, run.run_id)
    assert existing_tasks == tasks

    # 5. Task state transitions
    sample_task = tasks[0]
    session.get.return_value = sample_task

    q_task = await service.mark_task_queued(session, sample_task.task_id)
    assert q_task.status == "queued"

    r_task = await service.mark_task_running(session, sample_task.task_id)
    assert r_task.status == "running"
    assert r_task.started_at is not None

    s_task = await service.mark_task_succeeded(session, sample_task.task_id, ["art_1"])
    assert s_task.status == "succeeded"
    assert s_task.output_artifact_ids == ["art_1"]

    f_task = await service.mark_task_failed(session, sample_task.task_id, "Failure reason")
    assert f_task.status == "failed"
    assert f_task.validation_failures == ["Failure reason"]

    # Invalid status
    with pytest.raises(ValueError, match="Unsupported task status"):
        await service._mark_task(session, sample_task.task_id, "invalid_status")

    # Task lookup failure
    session.get.return_value = None
    with pytest.raises(LookupError, match="Generation task"):
        await service._mark_task(session, sample_task.task_id, "queued")

    # 6. cancel_run
    session.get.return_value = run
    sample_task.status = "running"
    session.execute.return_value = task_res_existing
    cancelled_run = await service.cancel_run(session, run.run_id, actor_id="admin_2")
    assert cancelled_run.status == "cancelled"
    assert sample_task.status == "cancelled"

    # 7. retry_failed_tasks
    sample_task.status = "failed"
    sample_task.attempt_number = 1
    sample_task.max_attempts = 3
    retries = await service.retry_failed_tasks(session, run.run_id, actor_id="admin_3")
    assert len(retries) >= 1
    assert retries[0].attempt_number == 2

    # Helper _value
    assert _value(ContentLayer.LESSONS) == "lessons"
    assert _value("lessons") == "lessons"


@pytest.mark.asyncio
async def test_content_generation_planner_workflow():
    scope_registry = MagicMock()
    mock_topic = MagicMock(caps_ref="4.M.1.1", title="Addition")
    mock_scope = MagicMock(
        scope_id="scope_math_g4",
        grade=4,
        subject_code="MATH",
        language="en",
        topic_map=[mock_topic],
    )
    scope_registry.get_scope.return_value = mock_scope
    scope_registry.list_scopes.return_value = [mock_scope]

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
    session.execute = AsyncMock()

    run_id = uuid.uuid4()
    run = ContentGenerationRun(
        run_id=run_id,
        scope_id="scope_math_g4",
        requested_by="admin",
        status="created",
        run_metadata={},
    )

    # 1. Run not found
    session.get.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await planner.plan_missing_for_run(session, run_id)

    # 2. Plan missing tasks with various layer states
    session.get.return_value = run

    # Layer 1: non-plannable layer (ignored)
    # Layer 2: target <= approved (skipped: coverage_green)
    # Layer 3: context failed (skipped: missing_source_context)
    # Layer 4: existing duplicate task (skipped: duplicate_task)
    # Layer 5: clean missing layer (task created)
    layer_ignored = MagicMock(layer="unknown_layer", target=5, approved=0, caps_ref="4.M.1.1")
    layer_green = MagicMock(layer="diagnostic_items", target=5, approved=5, caps_ref="4.M.1.1")
    layer_no_context = MagicMock(layer="lessons", target=5, approved=0, caps_ref="4.M.1.1")
    layer_duplicate = MagicMock(layer="assessment_blueprints", target=5, approved=0, caps_ref="4.M.1.1")
    layer_valid = MagicMock(layer="study_plan_templates", target=5, approved=0, caps_ref="4.M.1.1")

    report = MagicMock()
    report.layers = [layer_ignored, layer_green, layer_no_context, layer_duplicate, layer_valid]
    readiness_service.verify_scope.return_value = report

    # Context mocks: 1st call fails, 2nd & 3rd succeed
    context_bad = MagicMock(passed=False, errors=["No docs"])
    context_good = MagicMock(passed=True, errors=[])
    source_context_service.build_context.side_effect = [context_bad, context_good, context_good]

    # Task duplicate query mocks:
    # 1st query returns existing task, 2nd query returns None
    dup_res = MagicMock()
    dup_res.scalar_one_or_none.return_value = MagicMock()
    none_res = MagicMock()
    none_res.scalar_one_or_none.return_value = None
    session.execute.side_effect = [dup_res, none_res]

    result = await planner.plan_missing_for_run(session, run_id, actor_id="planner_actor")
    assert isinstance(result, GenerationPlanResult)
    assert len(result.created_task_ids) == 1
    assert len(result.skipped) == 3
    assert run.status == "planned"

    # 3. Test _topic_title fallback
    assert _topic_title(mock_scope, "4.M.1.1") == "Addition"
    assert _topic_title(mock_scope, "4.M.9.9") == "4.M.9.9"
