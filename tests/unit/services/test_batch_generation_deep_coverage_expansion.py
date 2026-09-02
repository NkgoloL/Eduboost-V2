import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel


from app.models.content_factory import (
    ContentGenerationArtifact,
    ContentGenerationRun,
    ContentGenerationTask,
    ContentLayer,
    ContentArtifactType,
    ContentArtifactStatus,
)
from app.services.batch_generation import (
    BatchGenerationEngine,
    GenerationTaskSpec,
    RunResult,
    _acquire_task_lock,
)
from app.services.llm_provider import GenerationResult, TokenUsage


class _DummyPayload(BaseModel):
    title: str = "Test Lesson"
    question: str = "What is 2+2?"
    options: list[str] = ["3", "4", "5"]
    correct_answer: str = "4"


class _FakeDbSession:
    """Non-mock class name to test real branches of _verify_source_snapshot and _resolve_sources."""
    def __init__(self):
        self.added = []
        self.committed = False
        self.flushed = False

    def add(self, item):
        self.added.append(item)

    async def flush(self):
        self.flushed = True

    async def commit(self):
        self.committed = True

    async def execute(self, stmt):
        return MagicMock(scalar_one_or_none=lambda: None)


def _create_engine():
    return BatchGenerationEngine(
        provider_router=MagicMock(),
        provenance_service=MagicMock(),
        safety_filter=MagicMock(),
        source_context_service=MagicMock(),
        validator=MagicMock(),
    )


@pytest.mark.asyncio
async def test_persist_artifact_diagnostic_item_and_lesson():
    engine = _create_engine()

    db = _FakeDbSession()
    task_id = uuid.uuid4()
    run_id = uuid.uuid4()
    task = ContentGenerationTask(
        task_id=task_id,
        run_id=run_id,
        scope_id="grade_4_maths",
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS.value,
        admin_actor_id=str(uuid.uuid4()),
        task_metadata={"grade": 4, "subject_code": "MATHS", "language": "en"},
    )

    payload = _DummyPayload()
    generation = GenerationResult(
        text="{}",
        provider="groq",
        model="llama3",
        usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150, estimated_cost_usd=0.002),
        latency_ms=120.0,
        request_id="req-123",
    )

    sources = [
        {
            "source_document_id": "doc-1",
            "source_chunk_id": "chk-1",
            "source_title": "DBE Workbook",
            "source_type": "textbook",
            "source_uri": "s3://eduboost/doc1.pdf",
            "citation_text": "Sample citation",
            "text": "Full text of chunk",
            "license_status": "open_license",
            "source_quality_score": 0.95,
            "chunk_quality_score": 0.90,
            "etl_version": "v2",
            "document_version_id": "v1",
            "chunk_hash": "chash1",
            "curriculum_mapping_id": "map-1",
            "source_hash": "shash1",
            "source_role": "primary_context",
            "document_status": "approved",
            "extra_custom_metadata": "custom_val",
        }
    ]

    # Diagnostic item persistence
    art_item = await engine._persist_artifact(
        task=task,
        content_type="diagnostic_item",
        validated_payload=payload,
        generation=generation,
        schema_version="1.0",
        prompt_version="1.0",
        sources=sources,
        source_snapshot_hash="snap-hash-123",
        db=db,
    )

    assert art_item.artifact_type == ContentArtifactType.DIAGNOSTIC_ITEM
    assert art_item.content_layer == ContentLayer.DIAGNOSTIC_ITEMS
    assert art_item.status == ContentArtifactStatus.PENDING_REVIEW
    assert len(db.added) == 2  # 1 artifact + 1 source

    # Lesson persistence
    db.added.clear()
    task.content_layer = ContentLayer.LESSONS
    art_lesson = await engine._persist_artifact(

        task=task,
        content_type="lesson",
        validated_payload=payload,
        generation=generation,
        schema_version="1.0",
        prompt_version="1.0",
        sources=sources,
        source_snapshot_hash="snap-hash-123",
        db=db,
    )
    assert art_lesson.artifact_type == ContentArtifactType.LESSON
    assert art_lesson.content_layer == ContentLayer.LESSONS


def test_build_source_context_variations():
    sources = [
        {"source_title": "Title 1", "text": "Content 1"},
        {"title": "Title 2", "citation_text": "Content 2"},
        {"content": "Content 3"},  # defaults to Source 3
        {"title": "Empty source", "text": ""},  # empty ignored
    ]
    res = BatchGenerationEngine._build_source_context(sources)
    assert "[Source 1: Title 1]" in res
    assert "Content 1" in res
    assert "[Source 2: Title 2]" in res
    assert "Content 2" in res
    assert "[Source 3: Source 3]" in res
    assert "Content 3" in res
    assert "Empty source" not in res


@pytest.mark.asyncio
async def test_verify_source_snapshot_error_branches():
    engine = _create_engine()

    db = _FakeDbSession()
    task = ContentGenerationTask(
        task_id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        scope_id="grade_4_maths",
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS.value,
        admin_actor_id=str(uuid.uuid4()),
        task_metadata={},
    )

    # 1. Missing source_snapshot_hash
    with pytest.raises(ValueError, match="has no source_snapshot_hash"):
        await engine._verify_source_snapshot(task, db)
    assert task.status == "failed"

    # 2. Source context failed verification
    task.task_metadata = {"source_snapshot_hash": "hash-123"}
    engine._source_context.build_context = AsyncMock(return_value=MagicMock(passed=False, errors=["Context unapproved"]))
    with pytest.raises(ValueError, match="Source context failed"):
        await engine._verify_source_snapshot(task, db)

    # 3. Source snapshot mismatch
    engine._source_context.build_context = AsyncMock(return_value=MagicMock(passed=True, chunks=[]))
    with patch("app.services.batch_generation.source_rows_for_chunks", return_value=[]), \
         patch("app.services.batch_generation.stable_json_hash", return_value="different-hash"):
        with pytest.raises(ValueError, match="Source snapshot mismatch"):
            await engine._verify_source_snapshot(task, db)


@pytest.mark.asyncio
async def test_resolve_sources_branches():
    engine = _create_engine()

    db = _FakeDbSession()
    task = ContentGenerationTask(
        task_id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        scope_id="grade_4_maths",
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS.value,
        admin_actor_id=str(uuid.uuid4()),
        task_metadata={"source_chunk_ids": ["c1"]},
    )

    # When context passes
    engine._source_context.build_context = AsyncMock(return_value=MagicMock(passed=True, chunks=[MagicMock()]))
    with patch("app.services.batch_generation.source_rows_for_chunks", return_value=[{"id": "c1"}]):
        sources = await engine._resolve_sources(task, supplied={"4.M.1.1": []}, db=db)
        assert len(sources) == 1

    # When context fails
    engine._source_context.build_context = AsyncMock(return_value=MagicMock(passed=False))
    sources_failed = await engine._resolve_sources(task, supplied=None, db=db)
    assert sources_failed == []


@pytest.mark.asyncio
async def test_execute_run_all_outcomes_and_db_session_arg():
    engine = _create_engine()

    run_id = uuid.uuid4()
    mock_run = MagicMock(spec=ContentGenerationRun, run_id=run_id, status="queued", run_metadata={})

    t1 = MagicMock(spec=ContentGenerationTask, task_id=uuid.uuid4(), run_id=run_id, caps_ref="4.M.1.1", status="queued")
    t2 = MagicMock(spec=ContentGenerationTask, task_id=uuid.uuid4(), run_id=run_id, caps_ref="4.M.1.2", status="queued")
    t3 = MagicMock(spec=ContentGenerationTask, task_id=uuid.uuid4(), run_id=run_id, caps_ref="4.M.1.3", status="queued")
    t4 = MagicMock(spec=ContentGenerationTask, task_id=uuid.uuid4(), run_id=run_id, caps_ref="4.M.1.4", status="queued")

    db = AsyncMock()

    # Query 1 returns run, Query 2 returns tasks
    mock_run_result = MagicMock()
    mock_run_result.scalar_one_or_none.return_value = mock_run

    mock_tasks_result = MagicMock()
    mock_tasks_result.scalars.return_value.all.return_value = [t1, t2, t3, t4]

    db.execute.side_effect = [mock_run_result, mock_tasks_result, None, None]

    engine._verify_source_snapshot = AsyncMock()
    engine._resolve_sources = AsyncMock(return_value=[])

    # Outcomes: success, safety_blocked, skipped, failed
    engine._execute_task = AsyncMock(side_effect=["success", "safety_blocked", "skipped", "error"])

    # Call with db_session parameter
    stats = await engine.process_run(run_id, db_or_sources={"4.M.1.1": []}, db_session=db)
    assert stats.succeeded == 1
    assert stats.safety_blocked == 1
    assert stats.skipped == 1
    assert stats.failed == 1
    assert stats.total_tasks == 4


@pytest.mark.asyncio
async def test_execute_task_empty_source_context_unexpected_error():
    engine = _create_engine()
    db = AsyncMock()
    task = MagicMock(
        spec=ContentGenerationTask,
        task_id=uuid.uuid4(),
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS.value,
        status="queued",
        task_metadata={"grade": 4, "subject": "Mathematics", "language": "en"},
        admin_actor_id=str(uuid.uuid4()),
        validation_failures=[],
    )

    with patch("app.services.batch_generation._acquire_task_lock", return_value=True):
        engine._provenance.validate_source_bundle = AsyncMock(return_value=MagicMock(passed=True, errors=[], source_snapshot_hash="h1"))
        engine._safety.check_source_bundle = AsyncMock(return_value=MagicMock(passed=True))
        # Empty source context
        engine._build_source_context = MagicMock(return_value="")
        engine._fail_task = AsyncMock()

        outcome = await engine._execute_task(task, {"4.M.1.1": [{"id": 1}]}, db=db, worker_id="w-1")
        assert outcome == "failed"
        engine._fail_task.assert_awaited_once()


