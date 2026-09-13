"""Comprehensive unit tests covering content reviewer assignment, queue, and orchestrator services."""
from datetime import datetime, timedelta, timezone
import os
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest

from app.domain.content_coverage import ContentLayer
from app.models.content_factory import (
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentReviewAssignment,
    ContentValidationReport,
)
from app.services.content_factory_orchestrator import (
    ContentFactoryOrchestrator,
    OrchestratorPlan,
    PIPELINE_STATES,
)
from app.services.content_review_queue import (
    ArtifactReviewBundle,
    ContentReviewQueueService,
    ReviewQueueItem,
    ReviewQueuePage,
    ReviewSummary,
    _artifact_dict,
    _review_dict,
    _validation_dict,
    _value,
)
from app.services.content_review_risk import ReviewRisk
from app.services.content_reviewer_assignment import (
    ContentReviewerAssignmentService,
    ReviewerWorkload,
)


# ============================================================================
# ContentFactoryOrchestrator Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_factory_orchestrator():
    run_service = AsyncMock()
    orchestrator = ContentFactoryOrchestrator(run_service=run_service)
    session = AsyncMock()

    run_id = uuid.uuid4()
    mock_run = MagicMock(run_id=run_id)
    mock_tasks = [MagicMock(task_id=uuid.uuid4()) for _ in range(3)]
    run_service.create_run.return_value = mock_run
    run_service.create_tasks_for_run.return_value = mock_tasks
    run_service.get_run.return_value = mock_run
    run_service.get_run_tasks.return_value = mock_tasks

    # 1. create_dry_run_plan with generation_enabled=False
    with patch.dict(os.environ, {"CONTENT_FACTORY_GENERATION_ENABLED": "false"}):
        assert orchestrator.generation_enabled is False
        plan = await orchestrator.create_dry_run_plan(
            session,
            scope_id="scope_math_g4",
            layers=[ContentLayer.DIAGNOSTIC_ITEMS],
            requested_by="admin_user",
        )
        assert isinstance(plan, OrchestratorPlan)
        assert plan.dry_run is True
        assert plan.generation_enabled is False
        assert plan.task_count == 3
        assert plan.planned_states == PIPELINE_STATES

    # 2. create_dry_run_plan with generation_enabled=True
    with patch.dict(os.environ, {"CONTENT_FACTORY_GENERATION_ENABLED": "true"}):
        assert orchestrator.generation_enabled is True
        plan_enabled = await orchestrator.create_dry_run_plan(
            session,
            scope_id="scope_math_g4",
            layers=[ContentLayer.DIAGNOSTIC_ITEMS],
            requested_by="admin_user",
        )
        assert plan_enabled.dry_run is False
        assert plan_enabled.generation_enabled is True

    # 3. execute_noop
    noop_plan = await orchestrator.execute_noop(session, run_id)
    assert noop_plan.run_id == run_id
    assert noop_plan.generation_enabled is False
    assert noop_plan.dry_run is True
    assert noop_plan.task_count == 3


# ============================================================================
# ContentReviewerAssignmentService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_reviewer_assignment_service():
    service = ContentReviewerAssignmentService()
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()

    art_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    artifact = ContentGenerationArtifact(
        artifact_id=art_id,
        version_number=1,
    )

    # 1. assign_artifact - artifact not found
    session.get.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await service.assign_artifact(session, art_id, "rev1", "lead1")

    # 2. assign_artifact - existing resolved assignment
    session.get.return_value = artifact
    resolved_assignment = ContentReviewAssignment(
        id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        assigned_to="rev1",
        status="approved",
    )
    service._reviewer_assignment = AsyncMock(return_value=resolved_assignment)
    with pytest.raises(ValueError, match="Reviewer already completed or closed"):
        await service.assign_artifact(session, art_id, "rev1", "lead1")

    # 3. assign_artifact - existing open assignment (updates details)
    open_assignment = ContentReviewAssignment(
        id=uuid.uuid4(),
        artifact_id=art_id,
        artifact_version=1,
        assigned_to="rev1",
        status="assigned",
        reviewer_competencies=["math"],
    )
    service._reviewer_assignment = AsyncMock(return_value=open_assignment)
    updated = await service.assign_artifact(
        session,
        art_id,
        "rev1",
        "lead2",
        priority="high",
        due_by=now + timedelta(days=2),
        competencies=["math", "caps"],
    )
    assert updated.assigned_by == "lead2"
    assert updated.priority == "high"
    assert updated.reviewer_competencies == ["math", "caps"]

    # 4. assign_artifact - new assignment
    service._reviewer_assignment = AsyncMock(return_value=None)
    new_assign = await service.assign_artifact(
        session,
        art_id,
        "rev2",
        "lead1",
        priority="urgent",
        idempotency_key="key123",
    )
    assert new_assign.assigned_to == "rev2"
    assert new_assign.priority == "urgent"
    assert new_assign.status == "assigned"
    session.add.assert_called_once()

    # 5. assign_batch
    batch = await service.assign_batch(session, [art_id], "rev2", "lead1")
    assert len(batch) == 1

    # 6. unassign_artifact - not found & success
    service._open_assignment = AsyncMock(return_value=None)
    with pytest.raises(LookupError, match="Open assignment for artifact"):
        await service.unassign_artifact(session, art_id, "lead1")

    service._open_assignment = AsyncMock(return_value=open_assignment)
    unassigned = await service.unassign_artifact(session, art_id, "lead1", reviewer_id="rev1")
    assert unassigned.status == "cancelled"
    assert unassigned.resolved_at is not None

    # 7. get_reviewer_workload
    item1 = ContentReviewAssignment(id=uuid.uuid4(), status="assigned", due_by=now - timedelta(days=1), assigned_at=now, created_at=now)  # overdue
    item2 = ContentReviewAssignment(id=uuid.uuid4(), status="in_review", due_by=now + timedelta(days=1), assigned_at=now, created_at=now) # not overdue
    item3 = ContentReviewAssignment(id=uuid.uuid4(), status="assigned", due_by=None, assigned_at=now - timedelta(days=5), created_at=now - timedelta(days=5)) # overdue via cutoff
    session.execute.return_value = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[item1, item2, item3]))))

    workload = await service.get_reviewer_workload(session, "rev1")
    assert isinstance(workload, ReviewerWorkload)
    assert workload.assigned == 2
    assert workload.in_review == 1
    assert workload.overdue == 2
    assert workload.total_open == 3

    # 8. list_assignments
    session.execute.return_value = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[item1]))))
    listed = await service.list_assignments(session, reviewer_id="rev1", status="assigned", limit=10)
    assert len(listed) == 1

    # 9. Real query helper paths (_reviewer_assignment, _open_assignment)
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=item1))
    real_service = ContentReviewerAssignmentService()
    res1 = await real_service._reviewer_assignment(session, art_id, 1, "rev1")
    assert res1 == item1
    res2 = await real_service._open_assignment(session, art_id, reviewer_id="rev1")
    assert res2 == item1


# ============================================================================
# ContentReviewQueueService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_review_queue_service():
    factory_service = AsyncMock()
    risk_service = MagicMock()
    service = ContentReviewQueueService(
        factory_service=factory_service,
        risk_service=risk_service,
    )
    session = AsyncMock()

    art_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    artifact = ContentGenerationArtifact(
        artifact_id=art_id,
        scope_id="scope_math_g4",
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        artifact_type=ContentArtifactType.DIAGNOSTIC_ITEM,
        status=ContentArtifactStatus.PENDING_REVIEW,
        artifact_json={"q": "sample"},
        provider="anthropic",
        model="claude",
        prompt_version="1.0",
        run_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        created_at=now,
        sources=[],
        reviews=[],
    )

    assignment = ContentReviewAssignment(
        id=uuid.uuid4(),
        artifact_id=art_id,
        assigned_to="rev1",
        status="assigned",
    )

    val_report = ContentValidationReport(
        validation_report_id=uuid.uuid4(),
        artifact_id=art_id,
        passed=True,
        checks={},
        errors=[],
    )
    prov_report = MagicMock(passed=True, errors=[], source_snapshot_hash="hash", sources=[])

    factory_service.get_artifact.return_value = artifact
    factory_service.get_artifact_provenance.return_value = prov_report
    risk_service.score_artifact.return_value = ReviewRisk(level="low", score=10, reasons=[])

    # 1. list_queue
    arts_mock = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[artifact]))))
    count_mock = MagicMock(scalar_one=MagicMock(return_value=1))
    session.execute.side_effect = [arts_mock, count_mock]

    service._load_assignments = AsyncMock(return_value={art_id: assignment})
    service._latest_validation_reports = AsyncMock(return_value={art_id: val_report})

    page = await service.list_queue(
        session,
        scope_id="scope_math_g4",
        layer="diagnostic_items",
        caps_ref="4.M.1.1",
        artifact_type="diagnostic_item",
        risk_level="low",
        reviewer_id="rev1",
        limit=10,
        offset=0,
    )
    assert isinstance(page, ReviewQueuePage)
    assert page.total == 1
    assert len(page.items) == 1
    assert page.items[0].reviewer_id == "rev1"
    assert page.items[0].risk_level == "low"

    # 2. get_review_summary
    service.list_queue = AsyncMock(return_value=page)
    summary = await service.get_review_summary(session, scope_id="scope_math_g4")
    assert isinstance(summary, ReviewSummary)
    assert summary.pending_review == 1
    assert summary.low_risk == 1
    assert summary.assigned == 1

    # 3. get_artifact_review_bundle
    review_mock = MagicMock(review_id=uuid.uuid4(), review_action="comment", review_reason="ok", reviewer_id="rev1")
    artifact.reviews = [review_mock]
    bundle = await service.get_artifact_review_bundle(session, art_id)
    assert isinstance(bundle, ArtifactReviewBundle)
    assert bundle.artifact["artifact_id"] == str(art_id)
    assert bundle.validation_report["passed"] is True
    assert len(bundle.prior_review_events) == 1

    # 4. Helpers and loaders
    real_queue = ContentReviewQueueService()
    assert await real_queue._load_assignments(session, []) == {}
    assert await real_queue._latest_validation_reports(session, []) == {}

    session.execute.side_effect = None
    session.execute.return_value = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[assignment]))))
    assign_map = await real_queue._load_assignments(session, [art_id])
    assert assign_map[art_id] == assignment

    session.execute.return_value = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[val_report]))))
    val_map = await real_queue._latest_validation_reports(session, [art_id])
    assert val_map[art_id] == val_report

    assert _artifact_dict(artifact)["scope_id"] == "scope_math_g4"
    assert _validation_dict(val_report)["passed"] is True
    assert _review_dict(review_mock)["reviewer_id"] == "rev1"
    assert _value("test") == "test"
