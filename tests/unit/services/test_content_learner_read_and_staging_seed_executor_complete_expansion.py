"""Comprehensive unit tests covering content learner read service and content staging seed executor."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.domain.content_coverage import ContentLayer
from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentProductionArtifact,
    ContentSeedRun,
    ContentStagingArtifact,
    ContentStagingSeedItem,
    ContentValidationReport,
)
from app.services.content_learner_read_service import (
    ContentLearnerReadService,
    LearnerDiagnosticItem,
    LearnerLesson,
    LearnerReadMode,
    LearnerScopeContentSummary,
)
from app.services.content_staging_seed_executor import (
    ContentStagingSeedExecutor,
    MissingForeignKeyError,
    SeedableArtifact,
    SkippedArtifact,
    StagingRollbackResult,
    StagingSeedItemResult,
    StagingSeedPlan,
    StagingSeedRunPage,
    StagingSeedRunResult,
    _maybe_await,
    _session_commit,
    _session_flush,
    _session_rollback,
)


# ============================================================================
# ContentLearnerReadService Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_learner_read_service():
    registry = MagicMock()
    service = ContentLearnerReadService(scope_registry=registry)
    session = AsyncMock()

    art_id = uuid.uuid4()
    prod_id = uuid.uuid4()
    scope_id = "scope_math_g4"
    caps_ref = "4.M.1"

    # 1. is_learner_visible_artifact edge cases
    gen_art = ContentGenerationArtifact(
        artifact_id=art_id,
        scope_id=scope_id,
        status=ContentArtifactStatus.PROMOTED_PRODUCTION,
        sources=[MagicMock()],
    )
    prod_art = ContentProductionArtifact(
        id=prod_id,
        artifact_id=art_id,
        scope_id=scope_id,
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        payload_json={"q": 1},
        source_artifact_hash="hash1",
        production_status="active",
        created_at=datetime.now(timezone.utc),
    )

    # Valid
    assert service.is_learner_visible_artifact(gen_art, prod_art) is True

    # No prod art or prod not active
    assert service.is_learner_visible_artifact(gen_art, None) is False
    prod_art_inactive = ContentProductionArtifact(production_status="superseded")
    assert service.is_learner_visible_artifact(gen_art, prod_art_inactive) is False

    # Generation art not promoted_production
    gen_pending = ContentGenerationArtifact(status=ContentArtifactStatus.PENDING_REVIEW, sources=[MagicMock()])
    assert service.is_learner_visible_artifact(gen_pending, prod_art) is False

    # Generation art quarantined, rejected, retired, validation failed
    for bad_status in [
        ContentArtifactStatus.QUARANTINED,
        ContentArtifactStatus.REJECTED,
        ContentArtifactStatus.RETIRED,
        ContentArtifactStatus.VALIDATION_FAILED,
    ]:
        gen_bad = ContentGenerationArtifact(status=bad_status, sources=[MagicMock()])
        assert service.is_learner_visible_artifact(gen_bad, prod_art) is False

    # No sources
    gen_no_src = ContentGenerationArtifact(status=ContentArtifactStatus.PROMOTED_PRODUCTION, sources=[])
    assert service.is_learner_visible_artifact(gen_no_src, prod_art) is False

    # 2. get_diagnostic_items
    session.execute.return_value = [(prod_art, gen_art)]
    items = await service.get_diagnostic_items(session, scope_id=scope_id, caps_ref=caps_ref, limit=10)
    assert len(items) == 1
    assert isinstance(items[0], LearnerDiagnosticItem)
    assert items[0].scope_id == scope_id
    registry.require_active_scope.assert_called_with(scope_id)

    # Legacy fallback path
    service._read_mode = LearnerReadMode.PRODUCTION_WITH_LEGACY_FALLBACK
    session.execute.return_value = []
    fallback_items = await service.get_diagnostic_items(session, scope_id=scope_id)
    assert fallback_items == []

    # 3. get_lessons
    prod_lesson = ContentProductionArtifact(
        id=prod_id,
        artifact_id=art_id,
        scope_id=scope_id,
        layer="lessons",
        artifact_type="lesson",
        payload_json={"body": "text"},
        source_artifact_hash="hash2",
        production_status="active",
        created_at=datetime.now(timezone.utc),
    )
    session.execute.return_value = [(prod_lesson, gen_art)]
    lessons = await service.get_lessons(session, scope_id=scope_id, caps_ref=caps_ref, limit=10)
    assert len(lessons) == 1
    assert isinstance(lessons[0], LearnerLesson)

    session.execute.return_value = []
    fallback_lessons = await service.get_lessons(session, scope_id=scope_id)
    assert fallback_lessons == []

    # 4. get_scope_content_summary
    session.scalar.side_effect = [5, 10, 15, datetime.now(timezone.utc)]
    summary = await service.get_scope_content_summary(session, scope_id)
    assert isinstance(summary, LearnerScopeContentSummary)
    assert summary.diagnostic_items_count == 5
    assert summary.lessons_count == 10
    assert summary.total_artifacts_count == 15
    assert summary.last_promotion_at is not None


# ============================================================================
# ContentStagingSeedExecutor Tests
# ============================================================================
@pytest.mark.asyncio
async def test_content_staging_seed_executor():
    factory_service = AsyncMock()
    executor = ContentStagingSeedExecutor(factory_service=factory_service)
    session = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()

    art_id = uuid.uuid4()
    scope_id = "scope_math_g4"

    # Helpers check
    await _session_flush(session)
    await _session_commit(session)
    await _session_rollback(session)
    assert await _maybe_await(42) == 42

    # 1. _plan_seed edge cases (skips: pending, rejected, quarantined, validation_failed, not approved, bad provenance, missing report, failed report)
    art_pending = ContentGenerationArtifact(artifact_id=uuid.uuid4(), scope_id=scope_id, content_layer=ContentLayer.DIAGNOSTIC_ITEMS, status=ContentArtifactStatus.PENDING_REVIEW)
    art_rej = ContentGenerationArtifact(artifact_id=uuid.uuid4(), scope_id=scope_id, content_layer=ContentLayer.DIAGNOSTIC_ITEMS, status=ContentArtifactStatus.REJECTED)
    art_quar = ContentGenerationArtifact(artifact_id=uuid.uuid4(), scope_id=scope_id, content_layer=ContentLayer.DIAGNOSTIC_ITEMS, status=ContentArtifactStatus.QUARANTINED)
    art_val_fail = ContentGenerationArtifact(artifact_id=uuid.uuid4(), scope_id=scope_id, content_layer=ContentLayer.DIAGNOSTIC_ITEMS, status=ContentArtifactStatus.VALIDATION_FAILED)
    art_draft = ContentGenerationArtifact(artifact_id=uuid.uuid4(), scope_id=scope_id, content_layer=ContentLayer.DIAGNOSTIC_ITEMS, status=ContentArtifactStatus.DRAFT)
    art_bad_prov = ContentGenerationArtifact(artifact_id=uuid.uuid4(), scope_id=scope_id, content_layer=ContentLayer.DIAGNOSTIC_ITEMS, status=ContentArtifactStatus.APPROVED)
    art_no_rep = ContentGenerationArtifact(artifact_id=uuid.uuid4(), scope_id=scope_id, content_layer=ContentLayer.DIAGNOSTIC_ITEMS, status=ContentArtifactStatus.APPROVED)
    art_rep_fail = ContentGenerationArtifact(artifact_id=uuid.uuid4(), scope_id=scope_id, content_layer=ContentLayer.DIAGNOSTIC_ITEMS, status=ContentArtifactStatus.APPROVED)
    art_ok = ContentGenerationArtifact(artifact_id=art_id, scope_id=scope_id, content_layer=ContentLayer.DIAGNOSTIC_ITEMS, status=ContentArtifactStatus.APPROVED, artifact_json={"q": 1}, artifact_hash="h1")

    session.execute.side_effect = [
        # All artifacts query
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[
            art_pending, art_rej, art_quar, art_val_fail, art_draft, art_bad_prov, art_no_rep, art_rep_fail, art_ok
        ])))),
        # val reports for art_no_rep
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        # val reports for art_rep_fail
        MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock(passed=False))),
        # val reports for art_ok
        MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock(passed=True))),
    ]
    # Provenance returns: fail for art_bad_prov, pass for art_no_rep, art_rep_fail, art_ok
    factory_service.get_artifact_provenance.side_effect = [
        MagicMock(passed=False),
        MagicMock(passed=True),
        MagicMock(passed=True),
        MagicMock(passed=True),
    ]

    plan = await executor.dry_run_seed(session, scope_id, layers=["diagnostic_items"])
    assert isinstance(plan, StagingSeedPlan)
    assert len(plan.seedable) == 1
    assert len(plan.skipped) == 8

    # 2. seed_staging - allow_partial=False with skipped (mock _plan_seed to return plan)
    executor._plan_seed = AsyncMock(return_value=plan)
    res_disallowed = await executor.seed_staging(session, scope_id, actor_id="admin", allow_partial=False)
    assert res_disallowed.status == "failed"
    assert res_disallowed.seeded_count == 0


    # 3. seed_staging - allow_partial=True with clean seeding & upsert
    plan_with_skipped = StagingSeedPlan(
        scope_id=scope_id,
        layers=["diagnostic_items"],
        seedable=[SeedableArtifact(
            artifact_id=art_id,
            scope_id=scope_id,
            caps_ref="4.M.1",
            layer="diagnostic_items",
            artifact_type="diagnostic_item",
            payload_json={"q": 1},
            artifact_hash="h1",
        )],
        skipped=[SkippedArtifact(artifact_id=uuid.uuid4(), reason="quarantined")],
    )
    executor._plan_seed = AsyncMock(return_value=plan_with_skipped)

    # First run: existing staging artifact found -> upsert branch
    existing_stg = ContentStagingArtifact(
        id=uuid.uuid4(),
        artifact_id=art_id,
        staging_status="pending",
    )
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[existing_stg])))),
    ]
    res_seeded = await executor.seed_staging(session, scope_id, actor_id="admin", allow_partial=True, batch_size=10)
    assert isinstance(res_seeded, StagingSeedRunResult)
    assert res_seeded.status == "partially_seeded_staging"
    assert res_seeded.seeded_count == 1
    assert existing_stg.staging_status == "active"

    # Second run: no existing staging artifact -> new staging artifact creation branch
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
    ]
    res_new_art = await executor.seed_staging(session, scope_id, actor_id="admin", allow_partial=True, batch_size=10)
    assert res_new_art.seeded_count == 1

    # Third run: batch commit triggers IntegrityError -> fallback record-by-record succeeds
    from sqlalchemy.exc import IntegrityError
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[existing_stg])))),
    ]
    # First commit fails with IntegrityError, second commit (record-by-record) succeeds
    session.commit.side_effect = [IntegrityError("statement", {}, Exception("unique constraint")), None]
    res_retry_ok = await executor.seed_staging(session, scope_id, actor_id="admin", allow_partial=True, batch_size=10)
    assert res_retry_ok.seeded_count == 1
    session.commit.side_effect = None

    # Fourth run: record-by-record triggers Foreign Key IntegrityError -> raises MissingForeignKeyError
    fk_exc = IntegrityError("statement", {}, Exception("foreign key violation"))
    setattr(fk_exc, "orig", MagicMock(sqlstate="23503"))
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[existing_stg])))),
    ]
    session.commit.side_effect = [IntegrityError("statement", {}, Exception("first fail")), fk_exc]
    with pytest.raises(MissingForeignKeyError):
        await executor.seed_staging(session, scope_id, actor_id="admin", allow_partial=True, batch_size=10)
    session.commit.side_effect = None

    # Fifth run: record-by-record triggers non-FK IntegrityError -> skipped item logged
    other_exc = IntegrityError("statement", {}, Exception("check constraint violation"))
    setattr(other_exc, "orig", MagicMock(sqlstate="23514"))
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[existing_stg])))),
    ]
    session.commit.side_effect = [IntegrityError("statement", {}, Exception("first fail")), other_exc, None]
    res_skipped_constraint = await executor.seed_staging(session, scope_id, actor_id="admin", allow_partial=True, batch_size=10)
    assert res_skipped_constraint.skipped_count >= 1
    session.commit.side_effect = None



    # 4. get_seed_run
    run_uuid = uuid.uuid4()
    mock_run = ContentSeedRun(
        seed_run_id=run_uuid,
        scope_id=scope_id,
        status="seeded_staging",
        summary={"planned_count": 5, "skipped_count": 0},
    )
    session.get.return_value = None
    with pytest.raises(LookupError, match="Seed run .* not found"):
        await executor.get_seed_run(session, run_uuid)

    session.get.return_value = mock_run
    got_run = await executor.get_seed_run(session, run_uuid)
    assert got_run.seed_run_id == run_uuid
    assert got_run.seeded_count == 5

    # 5. list_seed_runs
    session.execute.side_effect = [
        MagicMock(scalar_one=MagicMock(return_value=1)),  # total count
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_run])))),
    ]
    page = await executor.list_seed_runs(session, scope_id=scope_id, limit=10, offset=0)
    assert isinstance(page, StagingSeedRunPage)
    assert page.total == 1
    assert len(page.items) == 1

    # 6. list_seed_run_items
    mock_item = ContentStagingSeedItem(
        id=uuid.uuid4(),
        seed_run_id=run_uuid,
        artifact_id=art_id,
        scope_id=scope_id,
        caps_ref="4.M.1",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        target_table="content_staging_artifacts",
        target_record_id="rec-1",
        status="seeded",
        skip_reason=None,
        seed_payload_hash="h1",
    )
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_item])))),
    ]
    items_list = await executor.list_seed_run_items(session, run_uuid)
    assert len(items_list) == 1
    assert isinstance(items_list[0], StagingSeedItemResult)

    # 7. rollback_seed_run
    session.get.return_value = None
    with pytest.raises(LookupError, match="Seed run .* not found"):
        await executor.rollback_seed_run(session, run_uuid, actor_id="admin", reason="bad deploy")

    session.get.return_value = mock_run
    session.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_item])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[existing_stg])))),
    ]
    res_rollback = await executor.rollback_seed_run(session, run_uuid, actor_id="admin", reason="bad deploy")
    assert isinstance(res_rollback, StagingRollbackResult)
    assert res_rollback.status == "rolled_back"
    assert res_rollback.rolled_back_count == 1
    assert mock_item.status == "rolled_back"
    assert existing_stg.staging_status == "rolled_back"
