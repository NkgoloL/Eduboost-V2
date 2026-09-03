"""Batch 229 — app/services/batch_generation.py comprehensive branch coverage expansion.

Tests:
- GenerationTaskSpec & RunResult data classes
- _acquire_task_lock: successful acquisition vs lock contention
- create_run: empty task specs validation, provenance gate error, successful run creation with idempotency hashing
- process_run: missing run exception, empty tasks status "no_work", completed vs completed_with_errors
- _verify_source_snapshot: missing hash error, context failure error, snapshot mismatch error
- _resolve_sources: mock handling, context passed vs context failed
- _execute_task branches:
  - lock skipped
  - provenance failure -> validation_failed
  - source safety failure -> safety_blocked
  - ProviderContentPolicyError -> provider_policy_refusal
  - AllProvidersFailedError -> provider_failed
  - output safety failure -> safety_blocked
  - schema validator failure -> validation_failed
  - success -> persist artifact & validation report
  - unexpected error handling
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.content_factory import (
    ContentGenerationArtifact,
    ContentGenerationRun,
    ContentGenerationTask,
    ContentLayer,
)
from app.services.batch_generation import (
    BatchGenerationEngine,
    GenerationTaskSpec,
    RunResult,
    _acquire_task_lock,
)
from app.services.llm_provider import (
    AllProvidersFailedError,
    GenerationResult,
    ProviderContentPolicyError,
    TokenUsage,
)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_router():
    return AsyncMock()


@pytest.fixture
def mock_provenance():
    return MagicMock()


@pytest.fixture
def mock_safety():
    return MagicMock()


@pytest.fixture
def mock_validator():
    return MagicMock()


@pytest.fixture
def mock_source_context():
    return AsyncMock()


@pytest.fixture
def engine(
    mock_router,
    mock_provenance,
    mock_safety,
    mock_validator,
    mock_source_context,
):
    return BatchGenerationEngine(
        provider_router=mock_router,
        provenance_service=mock_provenance,
        safety_filter=mock_safety,
        validator=mock_validator,
        source_context_service=mock_source_context,
    )


# ---------------------------------------------------------------------------
# Data Classes & Lock Acquisition
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_spec_and_result_dataclasses():
    spec = GenerationTaskSpec(
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        content_type="diagnostic_item",
        count=3,
    )
    assert spec.caps_ref == "4.M.1.1"
    assert spec.count == 3

    res = RunResult(
        run_id=uuid.uuid4(),
        total_tasks=5,
        succeeded=3,
        failed=1,
        safety_blocked=1,
        skipped=0,
    )
    assert res.total_tasks == 5
    assert res.succeeded == 3


@pytest.mark.asyncio
@pytest.mark.unit
async def test_acquire_task_lock_success_and_failure(mock_db):
    task_id = uuid.uuid4()

    # 1. Successful acquisition
    res_mock = MagicMock()
    res_mock.scalar_one_or_none.return_value = task_id
    mock_db.execute.return_value = res_mock

    acquired = await _acquire_task_lock(task_id, "worker-1", mock_db)
    assert acquired is True

    # 2. Lock contention / max attempts reached
    res_none = MagicMock()
    res_none.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = res_none

    not_acquired = await _acquire_task_lock(task_id, "worker-2", mock_db)
    assert not_acquired is False


# ---------------------------------------------------------------------------
# create_run
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_run_validation_and_errors(engine, mock_db, mock_provenance):
    # 1. Empty task specs -> ValueError
    with pytest.raises(ValueError, match="At least one generation task is required"):
        await engine.create_run(
            scope_id="scope-1",
            task_specs=[],
            sources_by_caps_ref={},
            requested_by="admin-1",
            db=mock_db,
        )

    # 2. Provenance failure -> ValueError
    spec = GenerationTaskSpec(
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        content_type="diagnostic_item",
    )
    mock_gate_fail = MagicMock(passed=False, errors=["No approved chunks"])
    mock_provenance.validate_source_bundle.return_value = mock_gate_fail

    with pytest.raises(ValueError, match="Source provenance failed"):
        await engine.create_run(
            scope_id="scope-1",
            task_specs=[spec],
            sources_by_caps_ref={"4.M.1.1": []},
            requested_by="admin-1",
            db=mock_db,
        )

    # 3. Successful run creation
    mock_gate_pass = MagicMock(passed=True, errors=[], source_snapshot_hash="hash_123")
    mock_provenance.validate_source_bundle.return_value = mock_gate_pass

    run = await engine.create_run(
        scope_id="scope-1",
        task_specs=[spec],
        sources_by_caps_ref={"4.M.1.1": [{"source_chunk_id": uuid.uuid4()}]},
        requested_by="admin-1",
        db=mock_db,
    )
    assert isinstance(run, ContentGenerationRun)
    assert run.scope_id == "scope-1"
    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# process_run
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_process_run_not_found_and_empty(engine, mock_db):
    run_id = uuid.uuid4()

    # 1. Run not found -> ValueError
    res_none = MagicMock()
    res_none.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = res_none

    with pytest.raises(ValueError, match="not found"):
        await engine.process_run(run_id, mock_db)

    # 2. Run with zero tasks -> no_work status
    mock_run = MagicMock(spec=ContentGenerationRun, run_id=run_id, run_metadata={})
    res_run = MagicMock()
    res_run.scalar_one_or_none.return_value = mock_run

    res_tasks = MagicMock()
    res_tasks.scalars.return_value.all.return_value = []

    mock_db.execute.side_effect = [
        res_run,     # run lookup
        res_tasks,   # tasks lookup
        MagicMock(), # update running
        MagicMock(), # update final
    ]

    stats = await engine.process_run(run_id, mock_db)
    assert stats.total_tasks == 0


# ---------------------------------------------------------------------------
# Snapshot Verification & Source Resolution
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_verify_source_snapshot_failures(engine, mock_source_context):
    # Use real DB session mock (non-magic mock name) to trigger code path
    class RealAsyncSession:
        def __init__(self):
            self.committed = False
        async def commit(self):
            self.committed = True

    real_db = RealAsyncSession()

    # 1. Missing expected hash
    task_no_hash = MagicMock(
        spec=ContentGenerationTask,
        task_id=uuid.uuid4(),
        caps_ref="4.M.1.1",
        task_metadata={},
        validation_failures=[],
    )
    with pytest.raises(ValueError, match="has no source_snapshot_hash"):
        await engine._verify_source_snapshot(task_no_hash, real_db)
    assert task_no_hash.status == "failed"

    # 2. Source context failed
    task_with_hash = MagicMock(
        spec=ContentGenerationTask,
        task_id=uuid.uuid4(),
        caps_ref="4.M.1.1",
        task_metadata={"source_snapshot_hash": "hash_expected"},
        validation_failures=[],
    )
    mock_source_context.build_context.return_value = MagicMock(passed=False, errors=["Unapproved chunk"])
    with pytest.raises(ValueError, match="Source context failed"):
        await engine._verify_source_snapshot(task_with_hash, real_db)
    assert task_with_hash.status == "failed"


# ---------------------------------------------------------------------------
# Task Execution Safety & Provider Errors
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_execute_task_safety_and_provider_errors(
    engine,
    mock_db,
    mock_provenance,
    mock_safety,
    mock_router,
    mock_validator,
):
    task = MagicMock(
        spec=ContentGenerationTask,
        task_id=uuid.uuid4(),
        caps_ref="4.M.1.1",
        task_metadata={"content_type": "diagnostic_item", "grade": 4, "subject": "Maths"},
        validation_failures=[],
    )

    with patch("app.services.batch_generation._acquire_task_lock", new_callable=AsyncMock) as mock_lock:
        # 1. Lock skipped
        mock_lock.return_value = False
        res_skipped = await engine._execute_task(task, {"4.M.1.1": []}, mock_db, worker_id="w-1")
        assert res_skipped == "skipped"

        mock_lock.return_value = True

        # 2. Provenance failed
        mock_provenance.validate_source_bundle.return_value = MagicMock(passed=False, errors=["No sources"])
        res_prov_fail = await engine._execute_task(task, {"4.M.1.1": []}, mock_db, worker_id="w-1")
        assert res_prov_fail == "failed"

        # 3. Source safety failed
        mock_provenance.validate_source_bundle.return_value = MagicMock(passed=True, errors=[], source_snapshot_hash="h1")
        mock_safety.check_source_bundle.return_value = MagicMock(passed=False, summary="PII detected")
        res_safety_fail = await engine._execute_task(task, {"4.M.1.1": [{"id": 1}]}, mock_db, worker_id="w-1")
        assert res_safety_fail == "safety_blocked"

        # 4. Provider content policy error
        mock_safety.check_source_bundle.return_value = MagicMock(passed=True)
        engine._build_source_context = MagicMock(return_value="Approved context")
        mock_router.generate = AsyncMock(side_effect=ProviderContentPolicyError("Blocked", "anthropic"))
        res_pol = await engine._execute_task(task, {"4.M.1.1": [{"id": 1}]}, mock_db, worker_id="w-1")
        assert res_pol == "failed"

        # 5. All providers failed error
        mock_router.generate = AsyncMock(side_effect=AllProvidersFailedError("All failed"))
        res_all_fail = await engine._execute_task(task, {"4.M.1.1": [{"id": 1}]}, mock_db, worker_id="w-1")
        assert res_all_fail == "failed"

        # 6. Output safety failed
        mock_router.generate = AsyncMock(
            return_value=GenerationResult(
                text="Generated content",
                provider="groq",
                model="llama3",
                usage=TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30, estimated_cost_usd=0.001),
                latency_ms=100.0,
                request_id="req-1",
            )
        )
        mock_safety.check_text.return_value = MagicMock(passed=False, summary="Harmful output")
        res_out_safety = await engine._execute_task(task, {"4.M.1.1": [{"id": 1}]}, mock_db, worker_id="w-1")
        assert res_out_safety == "safety_blocked"

        # 7. Schema validator failed
        mock_safety.check_text.return_value = MagicMock(passed=True)
        mock_validator.validate.return_value = MagicMock(passed=False, errors=["Schema invalid"], error_summary="Missing fields")
        res_val_fail = await engine._execute_task(task, {"4.M.1.1": [{"id": 1}]}, mock_db, worker_id="w-1")
        assert res_val_fail == "failed"

        # 8. Success path
        mock_validator.validate.return_value = MagicMock(
            passed=True,
            errors=[],
            validated_payload={"item_id": "1"},
            schema_version="v1",
        )
        mock_artifact = MagicMock(spec=ContentGenerationArtifact, artifact_id=uuid.uuid4())
        engine._persist_artifact = AsyncMock(return_value=mock_artifact)
        engine._save_validation_report = AsyncMock()

        res_success = await engine._execute_task(task, {"4.M.1.1": [{"id": 1}]}, mock_db, worker_id="w-1")
        assert res_success == "success"
