"""Comprehensive branch coverage expansion for content_staging_seed_executor.py."""
from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentLayer,
    ContentSeedRun,
    ContentStagingArtifact,
    ContentStagingSeedItem,
    ContentValidationReport,
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


@pytest.mark.asyncio
async def test_session_helpers_edge_cases():
    # Sync double and None operations
    class NoOps:
        pass

    no_ops = NoOps()
    await _session_flush(no_ops)
    await _session_commit(no_ops)
    await _session_rollback(no_ops)

    # Coroutine vs non-coroutine in _maybe_await
    assert await _maybe_await(42) == 42

    # Async operations
    mock_session = AsyncMock()
    await _session_flush(mock_session)
    await _session_commit(mock_session)
    await _session_rollback(mock_session)
    assert mock_session.flush.await_count == 1
    assert mock_session.commit.await_count == 1
    assert mock_session.rollback.await_count == 1



def test_dataclasses_and_page():
    art_id = uuid.uuid4()
    run_id = uuid.uuid4()
    item_id = uuid.uuid4()

    item_res = StagingSeedItemResult(
        id=item_id,
        seed_run_id=run_id,
        artifact_id=art_id,
        scope_id="scope-1",
        caps_ref="4.M.1.1",
        layer="lessons",
        artifact_type="lesson",
        target_table="content_staging_artifacts",
        target_record_id=str(art_id),
        status="seeded",
        skip_reason=None,
        seed_payload_hash="hash123",
    )
    assert item_res.id == item_id

    run_res = StagingSeedRunResult(
        seed_run_id=run_id,
        scope_id="scope-1",
        status="seeded_staging",
        seeded_count=5,
        skipped_count=1,
    )
    page = StagingSeedRunPage(items=[run_res], total=1, limit=50, offset=0)
    assert page.total == 1
    assert len(page.items) == 1


@pytest.mark.asyncio
async def test_seed_staging_flush_failure_rollback():
    executor = ContentStagingSeedExecutor()
    plan_mock = StagingSeedPlan(
        scope_id="scope-01",
        layers=["lessons"],
        seedable=[],
        skipped=[SkippedArtifact(artifact_id=uuid.uuid4(), reason="Rejected")],
    )
    executor._plan_seed = AsyncMock(return_value=plan_mock)

    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock(side_effect=RuntimeError("DB flush error"))
    session.rollback = AsyncMock()

    with pytest.raises(RuntimeError, match="DB flush error"):
        await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True)
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_seed_staging_upsert_existing_staging():
    executor = ContentStagingSeedExecutor()
    art_id = uuid.uuid4()
    existing_staging_id = uuid.uuid4()

    plan_mock = StagingSeedPlan(
        scope_id="scope-01",
        layers=["lessons"],
        seedable=[
            SeedableArtifact(
                artifact_id=art_id,
                scope_id="scope-01",
                caps_ref="4.M.1",
                layer="lessons",
                artifact_type="lesson",
                payload_json={"title": "Updated Title"},
                artifact_hash="hash-updated",
            )
        ],
        skipped=[SkippedArtifact(artifact_id=uuid.uuid4(), reason="Quarantined")],
    )
    executor._plan_seed = AsyncMock(return_value=plan_mock)

    existing_staging = ContentStagingArtifact(
        id=existing_staging_id,
        artifact_id=art_id,
        scope_id="scope-01",
        caps_ref="4.M.1",
        layer="lessons",
        artifact_type="lesson",
        payload_json={"title": "Old Title"},
        source_artifact_hash="hash-old",
        staging_status="active",
        created_by_seed_run_id=uuid.uuid4(),
    )

    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    exec_res = MagicMock()
    exec_res.scalars.return_value.all.return_value = [existing_staging]
    session.execute = AsyncMock(return_value=exec_res)

    result = await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True)
    assert result.status == "partially_seeded_staging"
    assert result.seeded_count == 1
    assert result.skipped_count == 1
    assert existing_staging.source_artifact_hash == "hash-updated"


@pytest.mark.asyncio
async def test_seed_staging_integrity_error_recovery_and_foreign_key_failure():
    executor = ContentStagingSeedExecutor()
    art1_id = uuid.uuid4()
    art2_id = uuid.uuid4()

    plan_mock = StagingSeedPlan(
        scope_id="scope-01",
        layers=["lessons"],
        seedable=[
            SeedableArtifact(
                artifact_id=art1_id,
                scope_id="scope-01",
                caps_ref="4.M.1",
                layer="lessons",
                artifact_type="lesson",
                payload_json={"title": "Item 1"},
                artifact_hash="hash-1",
            ),
            SeedableArtifact(
                artifact_id=art2_id,
                scope_id="scope-01",
                caps_ref="4.M.2",
                layer="lessons",
                artifact_type="lesson",
                payload_json={"title": "Item 2"},
                artifact_hash="hash-2",
            ),
        ],
        skipped=[],
    )
    executor._plan_seed = AsyncMock(return_value=plan_mock)

    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.rollback = AsyncMock()

    exec_res = MagicMock()
    exec_res.scalars.return_value.all.return_value = []
    exec_res.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=exec_res)

    # 1. Batch commit fails with IntegrityError, then record 1 succeeds, record 2 fails with FK error
    class ForeignKeyOrigException(Exception):
        pgcode = "23503"
        def __str__(self):
            return "foreign key constraint violation"

    orig_fk_err = ForeignKeyOrigException()
    fk_error = IntegrityError("insert", {}, orig_fk_err)


    batch_err = IntegrityError("batch insert", {}, Exception("unique violation"))

    session.commit = AsyncMock(side_effect=[batch_err, None, fk_error])

    with pytest.raises(MissingForeignKeyError, match="Missing foreign key reference"):
        await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True)


@pytest.mark.asyncio
async def test_seed_staging_integrity_error_recovery_and_generic_constraint_violation():
    executor = ContentStagingSeedExecutor()
    art1_id = uuid.uuid4()

    plan_mock = StagingSeedPlan(
        scope_id="scope-01",
        layers=["lessons"],
        seedable=[
            SeedableArtifact(
                artifact_id=art1_id,
                scope_id="scope-01",
                caps_ref="4.M.1",
                layer="lessons",
                artifact_type="lesson",
                payload_json={"title": "Item 1"},
                artifact_hash="hash-1",
            )
        ],
        skipped=[],
    )
    executor._plan_seed = AsyncMock(return_value=plan_mock)

    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.rollback = AsyncMock()

    exec_res = MagicMock()
    exec_res.scalars.return_value.all.return_value = []
    exec_res.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=exec_res)

    batch_err = IntegrityError("batch insert", {}, Exception("check violation"))
    item_err = IntegrityError("item insert", {}, Exception("check constraint failed"))

    # batch fails -> item 1 fails -> log skipped item succeeds
    session.commit = AsyncMock(side_effect=[batch_err, item_err, None])

    res = await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True)
    assert res.seeded_count == 0
    assert res.skipped_count == 1
    assert len(res.errors) == 1


@pytest.mark.asyncio
async def test_seed_staging_operational_error_retry_and_timeout():
    executor = ContentStagingSeedExecutor()
    art1_id = uuid.uuid4()

    plan_mock = StagingSeedPlan(
        scope_id="scope-01",
        layers=["lessons"],
        seedable=[
            SeedableArtifact(
                artifact_id=art1_id,
                scope_id="scope-01",
                caps_ref="4.M.1",
                layer="lessons",
                artifact_type="lesson",
                payload_json={"title": "Item 1"},
                artifact_hash="hash-1",
            )
        ],
        skipped=[],
    )
    executor._plan_seed = AsyncMock(return_value=plan_mock)

    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.rollback = AsyncMock()

    exec_res = MagicMock()
    exec_res.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=exec_res)

    # 1. Retry succeeds on attempt 2
    op_err = OperationalError("connection lost", {}, Exception("network issue"))
    session.commit = AsyncMock(side_effect=[op_err, None])

    with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
        res = await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True)
        assert res.seeded_count == 1
        mock_sleep.assert_awaited_once()

    # 2. Retry exhausts 3 attempts
    session.commit = AsyncMock(side_effect=[op_err, op_err, op_err])
    with patch("asyncio.sleep", new=AsyncMock()):
        with pytest.raises(OperationalError):
            await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True)


@pytest.mark.asyncio
async def test_seed_staging_unhandled_batch_exception():
    executor = ContentStagingSeedExecutor()
    art1_id = uuid.uuid4()

    plan_mock = StagingSeedPlan(
        scope_id="scope-01",
        layers=["lessons"],
        seedable=[
            SeedableArtifact(
                artifact_id=art1_id,
                scope_id="scope-01",
                caps_ref="4.M.1",
                layer="lessons",
                artifact_type="lesson",
                payload_json={"title": "Item 1"},
                artifact_hash="hash-1",
            )
        ],
        skipped=[],
    )
    executor._plan_seed = AsyncMock(return_value=plan_mock)

    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.rollback = AsyncMock()

    exec_res = MagicMock()
    exec_res.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=exec_res)
    session.commit = AsyncMock(side_effect=TypeError("Unexpected error"))

    with pytest.raises(TypeError, match="Unexpected error"):
        await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True)


@pytest.mark.asyncio
async def test_seed_staging_integrity_error_with_existing_staging_and_log_error():
    executor = ContentStagingSeedExecutor()
    art1_id = uuid.uuid4()
    existing_staging_id = uuid.uuid4()

    plan_mock = StagingSeedPlan(
        scope_id="scope-01",
        layers=["lessons"],
        seedable=[
            SeedableArtifact(
                artifact_id=art1_id,
                scope_id="scope-01",
                caps_ref="4.M.1",
                layer="lessons",
                artifact_type="lesson",
                payload_json={"title": "Item 1"},
                artifact_hash="hash-1",
            )
        ],
        skipped=[],
    )
    executor._plan_seed = AsyncMock(return_value=plan_mock)

    existing_staging = ContentStagingArtifact(
        id=existing_staging_id,
        artifact_id=art1_id,
        scope_id="scope-01",
        caps_ref="4.M.1",
        layer="lessons",
        artifact_type="lesson",
        payload_json={"title": "Old Title"},
        source_artifact_hash="hash-old",
        staging_status="active",
        created_by_seed_run_id=uuid.uuid4(),
    )

    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.rollback = AsyncMock()

    exec_res = MagicMock()
    exec_res.scalars.return_value.all.return_value = [existing_staging]
    session.execute = AsyncMock(return_value=exec_res)

    batch_err = IntegrityError("batch insert", {}, Exception("unique violation"))
    # Retry 1: batch fails with IntegrityError, record 1 with existing_staging succeeds!
    session.commit = AsyncMock(side_effect=[batch_err, None])

    res = await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True, batch_size=10)
    assert res.seeded_count == 1
    assert existing_staging.source_artifact_hash == "hash-1"

    # 2. Case where logging the skipped item fails
    item_err = IntegrityError("item insert", {}, Exception("check constraint failed"))
    session.commit = AsyncMock(side_effect=[batch_err, item_err, RuntimeError("Log commit failed")])
    exec_res.scalars.return_value.all.return_value = []
    exec_res.scalar_one_or_none.return_value = None

    res2 = await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True)
    assert res2.seeded_count == 0
    assert res2.skipped_count == 1

    # 3. Case where item throws generic unhandled exception (lines 337-340)
    session.commit = AsyncMock(side_effect=[batch_err, TypeError("Item type error")])
    with pytest.raises(TypeError, match="Item type error"):
        await executor.seed_staging(session, "scope-01", actor_id="admin", allow_partial=True)



@pytest.mark.asyncio
async def test_get_and_list_seed_runs():
    executor = ContentStagingSeedExecutor()
    run_id = uuid.uuid4()
    session = MagicMock()

    # 1. get_seed_run 404 / LookupError
    session.get = AsyncMock(return_value=None)
    with pytest.raises(LookupError, match="not found"):
        await executor.get_seed_run(session, run_id)

    # 2. get_seed_run found
    run_mock = ContentSeedRun(
        seed_run_id=run_id,
        scope_id="scope-01",
        dry_run=False,
        status="seeded_staging",
        summary={"planned_count": 10, "skipped_count": 2},
    )
    session.get = AsyncMock(return_value=run_mock)
    res = await executor.get_seed_run(session, run_id)
    assert res.seed_run_id == run_id
    assert res.seeded_count == 10
    assert res.skipped_count == 2

    # 3. list_seed_runs (with scope_id filter)
    count_res = MagicMock()
    count_res.scalar_one.return_value = 1

    list_res = MagicMock()
    list_res.scalars.return_value.all.return_value = [run_mock]

    session.execute = AsyncMock(side_effect=[count_res, list_res, count_res, list_res])
    page = await executor.list_seed_runs(session, scope_id="scope-01", limit=10, offset=0)
    assert page.total == 1
    assert len(page.items) == 1
    assert page.items[0].scope_id == "scope-01"

    # 4. list_seed_runs (without scope_id filter)
    page_all = await executor.list_seed_runs(session, scope_id=None, limit=10, offset=0)
    assert page_all.total == 1



@pytest.mark.asyncio
async def test_list_seed_run_items_and_rollback():
    executor = ContentStagingSeedExecutor()
    run_id = uuid.uuid4()
    item_id = uuid.uuid4()
    art_id = uuid.uuid4()
    session = MagicMock()

    item_mock = ContentStagingSeedItem(
        id=item_id,
        seed_run_id=run_id,
        artifact_id=art_id,
        scope_id="scope-01",
        caps_ref="4.M.1",
        layer="lessons",
        artifact_type="lesson",
        target_table="content_staging_artifacts",
        target_record_id=str(art_id),
        status="seeded",
        skip_reason=None,
        seed_payload_hash="hash123",
        created_at=datetime.now(timezone.utc),
    )

    # 1. list_seed_run_items
    items_res = MagicMock()
    items_res.scalars.return_value.all.return_value = [item_mock]
    session.execute = AsyncMock(return_value=items_res)

    items = await executor.list_seed_run_items(session, run_id)
    assert len(items) == 1
    assert items[0].id == item_id

    # 2. rollback_seed_run not found -> LookupError
    session.get = AsyncMock(return_value=None)
    with pytest.raises(LookupError, match="not found"):
        await executor.rollback_seed_run(session, run_id, actor_id="admin", reason="Incorrect seed")

    # 3. rollback_seed_run found
    run_mock = ContentSeedRun(
        seed_run_id=run_id,
        scope_id="scope-01",
        dry_run=False,
        status="seeded_staging",
        summary={"planned_count": 1, "skipped_count": 0},
    )
    staging_art_mock = ContentStagingArtifact(
        id=uuid.uuid4(),
        artifact_id=art_id,
        scope_id="scope-01",
        caps_ref="4.M.1",
        layer="lessons",
        artifact_type="lesson",
        payload_json={},
        source_artifact_hash="hash123",
        staging_status="active",
        created_by_seed_run_id=run_id,
    )

    items_res2 = MagicMock()
    items_res2.scalars.return_value.all.return_value = [item_mock]
    arts_res = MagicMock()
    arts_res.scalars.return_value.all.return_value = [staging_art_mock]

    session.get = AsyncMock(return_value=run_mock)
    session.execute = AsyncMock(side_effect=[items_res2, arts_res])
    session.flush = AsyncMock()

    roll_res = await executor.rollback_seed_run(session, run_id, actor_id="admin", reason="Incorrect seed")
    assert roll_res.status == "rolled_back"
    assert roll_res.rolled_back_count == 1
    assert item_mock.status == "rolled_back"
    assert staging_art_mock.staging_status == "rolled_back"
    assert run_mock.status == "rolled_back"


@pytest.mark.asyncio
async def test_plan_seed_comprehensive_status_and_provenance_branches():
    mock_factory = MagicMock()
    executor = ContentStagingSeedExecutor(factory_service=mock_factory)
    session = MagicMock()

    def make_art(status: ContentArtifactStatus, layer: str = "lesson_content") -> ContentGenerationArtifact:
        art = ContentGenerationArtifact(
            artifact_id=uuid.uuid4(),
            scope_id="scope-01",
            caps_ref="4.M.1",
            content_layer=layer,
            artifact_type="lesson",
            artifact_json={"title": "Test"},
            artifact_hash="hash-123",
            status=status,
        )
        return art

    art_pending = make_art(ContentArtifactStatus.PENDING_REVIEW)
    art_rejected = make_art(ContentArtifactStatus.REJECTED)
    art_quarantined = make_art(ContentArtifactStatus.QUARANTINED)
    art_val_failed = make_art(ContentArtifactStatus.VALIDATION_FAILED)
    art_draft = make_art(ContentArtifactStatus.DRAFT)
    art_other_layer = make_art(ContentArtifactStatus.APPROVED, layer="diagnostic_items")
    art_bad_prov = make_art(ContentArtifactStatus.APPROVED)
    art_no_val = make_art(ContentArtifactStatus.APPROVED)
    art_failed_val = make_art(ContentArtifactStatus.APPROVED)
    art_approved = make_art(ContentArtifactStatus.APPROVED)

    artifacts = [
        art_pending,
        art_rejected,
        art_quarantined,
        art_val_failed,
        art_draft,
        art_other_layer,
        art_bad_prov,
        art_no_val,
        art_failed_val,
        art_approved,
    ]

    arts_res = MagicMock()
    arts_res.scalars.return_value.all.return_value = artifacts

    # Provenance mock
    prov_bad = MagicMock(passed=False)
    prov_ok = MagicMock(passed=True)
    mock_factory.get_artifact_provenance = AsyncMock(side_effect=[prov_bad, prov_ok, prov_ok, prov_ok])

    # Validation reports mock:
    # 1 for art_no_val: None
    val_none = MagicMock()
    val_none.scalar_one_or_none.return_value = None
    # 2 for art_failed_val: passed=False
    val_fail = MagicMock()
    val_fail.scalar_one_or_none.return_value = MagicMock(passed=False)
    # 3 for art_approved: passed=True
    val_pass = MagicMock()
    val_pass.scalar_one_or_none.return_value = MagicMock(passed=True)

    session.execute = AsyncMock(side_effect=[arts_res, val_none, val_fail, val_pass])

    plan = await executor._plan_seed(session, "scope-01", layers=["lesson_content"])

    assert len(plan.seedable) == 1
    assert plan.seedable[0].artifact_id == art_approved.artifact_id
    reasons = [s.reason for s in plan.skipped]
    assert any("pending review" in r for r in reasons)
    assert any("rejected" in r for r in reasons)
    assert any("quarantined" in r for r in reasons)
    assert any("validation failed" in r for r in reasons)
    assert any("not seedable" in r for r in reasons)
    assert any("Invalid provenance" in r for r in reasons)
    assert any("validation report missing" in r for r in reasons)
    assert any("Latest validation failed" in r for r in reasons)
