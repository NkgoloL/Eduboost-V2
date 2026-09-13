from unittest.mock import AsyncMock, MagicMock
import os
import uuid
import pytest

from app.domain.content_coverage import (
    CapsRefCoverageReport,
    ContentLayer,
    CoverageLayerCounts,
    CoverageLayerStatus,
    ScopeCoverageReport,
)
from app.models.content_factory import ContentArtifactStatus
from app.services.content_coverage_service import (
    ContentCoverageService,
    CoverageGateLayerReport,
    _status,
    build_content_coverage_service,
)
from app.services.content_factory_orchestrator import (
    ContentFactoryOrchestrator,
    OrchestratorPlan,
)


@pytest.mark.asyncio
async def test_content_factory_orchestrator_plans():
    mock_run_service = AsyncMock()
    run_obj = MagicMock()
    run_obj.run_id = uuid.uuid4()
    mock_run_service.create_run.return_value = run_obj
    mock_run_service.get_run.return_value = run_obj
    mock_run_service.create_tasks_for_run.return_value = [MagicMock(), MagicMock()]
    mock_run_service.get_run_tasks.return_value = [MagicMock(), MagicMock()]

    orchestrator = ContentFactoryOrchestrator(run_service=mock_run_service)

    # 1. create_dry_run_plan with generation disabled (default)
    session = AsyncMock()
    plan_dry = await orchestrator.create_dry_run_plan(
        session,
        scope_id="scope_math_g4",
        layers=[ContentLayer.DIAGNOSTIC_ITEMS],
        requested_by="admin",
    )
    assert isinstance(plan_dry, OrchestratorPlan)
    assert plan_dry.run_id == run_obj.run_id
    assert plan_dry.task_count == 2
    assert plan_dry.dry_run is True

    # 2. execute_noop
    noop_plan = await orchestrator.execute_noop(session, run_obj.run_id)
    assert noop_plan.run_id == run_obj.run_id
    assert noop_plan.task_count == 2
    assert noop_plan.generation_enabled is False


@pytest.mark.asyncio
async def test_content_coverage_service_complete():
    scope_registry = MagicMock()
    mock_scope = MagicMock(
        scope_id="scope_math_g4",
        grade=4,
        subject_code="MATH",
        language="en",
        caps_refs=["4.M.1.1", "4.M.1.2"],
    )
    scope_registry.get_scope.return_value = mock_scope
    scope_registry.get_scope_caps_refs.return_value = ["4.M.1.1", "4.M.1.2"]
    scope_registry.get_coverage_target.return_value = 5

    mock_item_repo = AsyncMock()
    mock_item_repo.get_coverage_summary.return_value = {
        "4.M.1.1": {"approved": 5, "ai_generated": 2, "human_reviewed": 1, "rejected": 0},
        "4.M.1.2": {"approved": 0, "ai_generated": 0, "human_reviewed": 0, "rejected": 1},
    }

    mock_lesson_repo = AsyncMock()
    lesson1 = MagicMock(review_status="approved")
    lesson2 = MagicMock(review_status=MagicMock(value="ai_generated"))
    lesson3 = MagicMock(review_status="rejected")
    mock_lesson_repo.list_by_caps_ref.return_value = [lesson1, lesson2, lesson3]

    service = ContentCoverageService(
        scope_registry=scope_registry,
        item_repo=mock_item_repo,
        lesson_repo=mock_lesson_repo,
    )

    # 1. get_scope_coverage
    report = await service.get_scope_coverage("scope_math_g4")
    assert isinstance(report, ScopeCoverageReport)
    assert report.scope_id == "scope_math_g4"
    assert len(report.per_caps_ref) == 2
    assert report.summary.total_caps_refs == 2

    # 2. get_caps_ref_coverage invalid caps_ref
    with pytest.raises(LookupError, match="is outside content scope"):
        await service.get_caps_ref_coverage("scope_math_g4", "invalid_ref")

    # 3. get_coverage for promotion gate
    session = AsyncMock()
    session.execute = AsyncMock()
    count_mock = MagicMock()
    count_mock.scalar_one_or_none.return_value = 4
    session.execute.return_value = count_mock

    # DIAGNOSTIC_ITEMS layer
    gate_diag = await service.get_coverage(session, "scope_math_g4", ContentLayer.DIAGNOSTIC_ITEMS)
    assert isinstance(gate_diag, CoverageGateLayerReport)
    assert gate_diag.target_total == 10

    # ASSESSMENT_BLUEPRINTS layer (queries session)
    gate_blue = await service.get_coverage(session, "scope_math_g4", ContentLayer.ASSESSMENT_BLUEPRINTS)
    assert gate_blue.approved_total == 4

    # 4. None repos fallback
    bare_service = ContentCoverageService(scope_registry=scope_registry, item_repo=None, lesson_repo=None)
    bare_report = await bare_service.get_caps_ref_coverage("scope_math_g4", "4.M.1.1")
    assert bare_report.layers[ContentLayer.DIAGNOSTIC_ITEMS].approved == 0
    assert bare_report.layers[ContentLayer.LESSONS].approved == 0

    # 5. Helpers
    assert _status(lesson1) == "approved"
    assert _status(lesson2) == "ai_generated"
    svc_from_builder = build_content_coverage_service(mock_item_repo, mock_lesson_repo)
    assert svc_from_builder.item_repo == mock_item_repo
