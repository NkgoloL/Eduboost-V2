import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.domain.content_coverage import ContentLayer
from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact
from app.services.content_artifact_lifecycle import (
    ContentArtifactLifecycleService,
    ArtifactStatusTransition,
    _value,
)
from app.services.content_factory_orchestrator import (
    ContentFactoryOrchestrator,
    PIPELINE_STATES,
)


@pytest.mark.asyncio
async def test_content_artifact_lifecycle_complete():
    factory_mock = MagicMock()
    gov_mock = MagicMock()
    service = ContentArtifactLifecycleService(
        factory_service=factory_mock,
        governance_service=gov_mock,
    )
    session = AsyncMock()
    aid = uuid.uuid4()

    # 1. create_artifact and validate_for_review delegation
    factory_mock.create_artifact = AsyncMock(return_value="mock_created")
    res_created = await service.create_artifact(session, payload={"sample": "data"})
    assert res_created == "mock_created"

    factory_mock.validate_existing_artifact = AsyncMock(return_value="mock_validated")
    res_val = await service.validate_for_review(session, aid)
    assert res_val == "mock_validated"

    # 2. submit_for_review invalid previous status
    art_invalid_status = MagicMock(spec=ContentGenerationArtifact, artifact_id=aid, status=ContentArtifactStatus.PUBLISHED)
    factory_mock.get_artifact = AsyncMock(return_value=art_invalid_status)
    with pytest.raises(ValueError, match="Only generated, validation_failed, or revision_required"):
        await service.submit_for_review(session, aid, "actor-1")

    # 3. submit_for_review with failed validation
    art_generated = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid,
        status=ContentArtifactStatus.GENERATED,
        row_version=1,
    )
    factory_mock.get_artifact = AsyncMock(return_value=art_generated)
    mock_failed_report = MagicMock(passed=False, errors=["Schema violation", "Missing field"])
    service.validate_for_review = AsyncMock(return_value=mock_failed_report)
    with pytest.raises(ValueError, match="Artifact validation failed: Schema violation; Missing field"):
        await service.submit_for_review(session, aid, "actor-1")
    assert art_generated.status == ContentArtifactStatus.VALIDATION_FAILED

    # 4. submit_for_review success
    mock_passed_report = MagicMock(passed=True, errors=[])
    service.validate_for_review = AsyncMock(return_value=mock_passed_report)
    gov_mock.record_external_transition = AsyncMock()

    t_submit = await service.submit_for_review(session, aid, "actor-1")
    assert t_submit.artifact_id == aid
    assert t_submit.previous_status == ContentArtifactStatus.VALIDATION_FAILED.value
    assert t_submit.new_status == ContentArtifactStatus.PENDING_REVIEW.value
    assert art_generated.status == ContentArtifactStatus.PENDING_REVIEW
    assert art_generated.approval_count == 0
    assert art_generated.publication_eligible is False
    assert art_generated.row_version == 2
    gov_mock.record_external_transition.assert_awaited()
    session.flush.assert_awaited()

    # 5. reject_artifact validation & execution
    with pytest.raises(ValueError, match="Rejecting an artifact requires a reason."):
        await service.reject_artifact(session, aid, "actor-1", "   ")

    art_pending = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid,
        status=ContentArtifactStatus.PENDING_REVIEW,
        row_version=None,
    )
    factory_mock.get_artifact = AsyncMock(return_value=art_pending)
    t_reject = await service.reject_artifact(session, aid, "actor-1", "Fails pedagogical accuracy")
    assert t_reject.new_status == ContentArtifactStatus.REJECTED.value
    assert art_pending.status == ContentArtifactStatus.REJECTED
    assert art_pending.publication_eligible is False
    assert art_pending.row_version == 2

    # 6. quarantine_artifact execution
    art_quarantined = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid,
        status=ContentArtifactStatus.QUARANTINED,
    )
    gov_mock.quarantine_artifact = AsyncMock(return_value=art_quarantined)
    t_quarantine = await service.quarantine_artifact(session, aid, "actor-1", "Harmful content suspected")
    assert t_quarantine.new_status == ContentArtifactStatus.QUARANTINED.value
    assert t_quarantine.reason == "Harmful content suspected"

    # 7. retire_artifact validation & execution
    with pytest.raises(ValueError, match="Retiring an artifact requires a reason."):
        await service.retire_artifact(session, aid, "actor-1", "")

    t_retire = await service.retire_artifact(session, aid, "actor-1", "Curriculum superseded")
    assert t_retire.new_status == ContentArtifactStatus.RETIRED.value

    # 8. mark_seeded_staging branches
    art_not_approved = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid,
        status=ContentArtifactStatus.PENDING_REVIEW,
        publication_eligible=True,
    )
    factory_mock.get_artifact = AsyncMock(return_value=art_not_approved)
    with pytest.raises(ValueError, match="Only quorum-approved artifacts can be seeded to staging."):
        await service.mark_seeded_staging(session, aid, "actor-1")

    art_approved_not_eligible = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid,
        status=ContentArtifactStatus.APPROVED,
        publication_eligible=False,
    )
    factory_mock.get_artifact = AsyncMock(return_value=art_approved_not_eligible)
    with pytest.raises(ValueError, match="Artifact is not publication eligible."):
        await service.mark_seeded_staging(session, aid, "actor-1")

    art_approved_eligible = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid,
        status=ContentArtifactStatus.APPROVED,
        publication_eligible=True,
        row_version=2,
    )
    factory_mock.get_artifact = AsyncMock(return_value=art_approved_eligible)
    t_staging = await service.mark_seeded_staging(session, aid, "actor-1")
    assert t_staging.new_status == ContentArtifactStatus.SEEDED_STAGING.value
    assert art_approved_eligible.status == ContentArtifactStatus.SEEDED_STAGING
    assert art_approved_eligible.row_version == 3

    # 9. mark_promoted_production branches
    art_staging_not_eligible = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid,
        status=ContentArtifactStatus.SEEDED_STAGING,
        publication_eligible=False,
    )
    factory_mock.get_artifact = AsyncMock(return_value=art_staging_not_eligible)
    with pytest.raises(ValueError, match="Artifact is not publication eligible."):
        await service.mark_promoted_production(session, aid, "actor-1")

    art_wrong_for_promoted = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid,
        status=ContentArtifactStatus.APPROVED,
        publication_eligible=True,
    )
    factory_mock.get_artifact = AsyncMock(return_value=art_wrong_for_promoted)
    with pytest.raises(ValueError, match="Only seeded_staging artifacts can be promoted to production."):
        await service.mark_promoted_production(session, aid, "actor-1")

    art_staging_eligible = MagicMock(
        spec=ContentGenerationArtifact,
        artifact_id=aid,
        status=ContentArtifactStatus.SEEDED_STAGING,
        publication_eligible=True,
        row_version=3,
    )
    factory_mock.get_artifact = AsyncMock(return_value=art_staging_eligible)
    t_promoted = await service.mark_promoted_production(session, aid, "actor-1")
    assert t_promoted.new_status == ContentArtifactStatus.PROMOTED_PRODUCTION.value
    assert art_staging_eligible.status == ContentArtifactStatus.PROMOTED_PRODUCTION
    assert art_staging_eligible.row_version == 4

    # 10. Default constructors and _value helper
    default_service = ContentArtifactLifecycleService()
    assert default_service.factory_service is not None
    assert default_service.governance_service is not None
    assert _value(ContentArtifactStatus.APPROVED) == ContentArtifactStatus.APPROVED.value
    assert _value("plain_string") == "plain_string"


@pytest.mark.asyncio
async def test_content_factory_orchestrator_complete(monkeypatch):
    run_service_mock = MagicMock()
    session = AsyncMock()
    run_id = uuid.uuid4()

    mock_run = MagicMock(run_id=run_id)
    run_service_mock.create_run = AsyncMock(return_value=mock_run)
    run_service_mock.create_tasks_for_run = AsyncMock(return_value=["task1", "task2"])
    run_service_mock.get_run = AsyncMock(return_value=mock_run)
    run_service_mock.get_run_tasks = AsyncMock(return_value=["task1", "task2", "task3"])

    # 1. Generation enabled = True
    monkeypatch.setenv("CONTENT_FACTORY_GENERATION_ENABLED", "true")
    orchestrator = ContentFactoryOrchestrator(run_service=run_service_mock)
    assert orchestrator.generation_enabled is True

    plan = await orchestrator.create_dry_run_plan(
        session,
        scope_id="math_grade_4",
        layers=[ContentLayer.LESSONS],
        requested_by="admin-user",
    )
    assert plan.run_id == run_id
    assert plan.generation_enabled is True
    assert plan.dry_run is False
    assert plan.task_count == 2
    assert plan.planned_states == PIPELINE_STATES

    # 2. execute_noop
    noop_plan = await orchestrator.execute_noop(session, run_id)
    assert noop_plan.run_id == run_id
    assert noop_plan.generation_enabled is False
    assert noop_plan.dry_run is True
    assert noop_plan.task_count == 3

    # 3. Default constructor
    default_orchestrator = ContentFactoryOrchestrator()
    assert default_orchestrator.run_service is not None
