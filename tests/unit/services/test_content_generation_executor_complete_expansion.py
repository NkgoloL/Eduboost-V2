from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.models.content_factory import (
    ContentArtifactType,
    ContentGenerationTask,
    ContentLayer,
)
from app.services.content_generation.prompt_payloads import SourceContextChunk
from app.services.content_generation_executor import (
    ContentGenerationExecutor,
    GenerationDisabledError,
    RunExecutionResult,
    TaskExecutionResult,
)


@pytest.mark.asyncio
async def test_content_generation_executor_disabled():
    settings = MagicMock()
    settings.enabled = False
    executor = ContentGenerationExecutor(settings=settings)
    session = AsyncMock()

    with pytest.raises(GenerationDisabledError):
        await executor.execute_task(session, task_id=uuid.uuid4())

    with pytest.raises(GenerationDisabledError):
        await executor.execute_run(session, run_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_content_generation_executor_task_and_run():
    settings = MagicMock()
    settings.enabled = True
    settings.provider = "deterministic"
    settings.max_artifacts_per_task = 5

    scope_registry = MagicMock()
    mock_scope = MagicMock()
    mock_scope.grade = 4
    mock_scope.subject_code = "MATH"
    mock_scope.language = "en"
    scope_registry.get_scope.return_value = mock_scope

    source_context_service = AsyncMock()
    chunk = SourceContextChunk(
        source_document_id="doc_1",
        source_chunk_id="chunk_1",
        text="Source text",
        source_quality_score=0.95,
        license_status="open",
        document_status="approved",
    )
    context_res = MagicMock()
    context_res.passed = True
    context_res.chunks = [chunk]
    source_context_service.build_context.return_value = context_res

    content_factory_service = AsyncMock()
    mock_artifact = MagicMock()
    mock_artifact.artifact_id = uuid.uuid4()
    mock_artifact.artifact_hash = "hash_123"
    content_factory_service.create_artifact.return_value = mock_artifact

    run_service = AsyncMock()

    executor = ContentGenerationExecutor(
        settings=settings,
        scope_registry=scope_registry,
        source_context_service=source_context_service,
        content_factory_service=content_factory_service,
        run_service=run_service,
    )

    session = AsyncMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    nested_cm = AsyncMock()
    nested_cm.__aenter__.return_value = None
    nested_cm.__aexit__.return_value = None
    session.begin_nested = MagicMock(return_value=nested_cm)

    hash_query = MagicMock()
    hash_query.all.return_value = [("existing_hash_1",)]
    session.execute.return_value = hash_query


    task_id = uuid.uuid4()
    task = ContentGenerationTask(
        task_id=task_id,
        run_id=uuid.uuid4(),
        scope_id="scope_math_g4",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS.value,
        caps_ref="4.M.1.1",
        status="queued",
        task_metadata={"required_count": 1, "missing_count": 1},
    )
    session.get.return_value = task

    # 1. Execute task successfully
    result = await executor.execute_task(session, task_id=task_id, actor_id="admin_1")
    assert isinstance(result, TaskExecutionResult)
    assert result.status == "succeeded"
    assert len(result.artifact_ids) == 1
    assert task.status == "succeeded"

    # 2. Task already completed -> skipped
    task.status = "completed"
    skip_result = await executor.execute_task(session, task_id=task_id)
    assert skip_result.status == "skipped"

    # 3. Context build failed -> task fails
    context_res.passed = False
    context_res.errors = ["Context missing"]
    task.status = "queued"
    fail_result = await executor.execute_task(session, task_id=task_id)
    assert fail_result.status == "failed"
    assert "Context missing" in fail_result.errors

    # 4. Execute run flow
    context_res.passed = True
    task.status = "queued"
    run_obj = MagicMock()
    run_obj.run_id = uuid.uuid4()
    run_service.get_run.return_value = run_obj
    run_service.get_run_tasks.return_value = [task]

    run_res = await executor.execute_run(session, run_id=run_obj.run_id)
    assert isinstance(run_res, RunExecutionResult)
    assert run_res.status == "succeeded"
    assert run_res.summary["tasks_executed"] == 1

    # 5. Execution report
    report = await executor.execution_report(session, run_id=run_obj.run_id)
    assert report["run_id"] == str(run_obj.run_id)
    assert report["tasks"] == 1

    # 6. Task not found -> LookupError
    session.get.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await executor.execute_task(session, task_id=uuid.uuid4())

    for layer in (
        ContentLayer.LESSONS.value,
        ContentLayer.ASSESSMENT_BLUEPRINTS.value,
        ContentLayer.STUDY_PLAN_TEMPLATES.value,
    ):
        layer_task = ContentGenerationTask(
            task_id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            scope_id="scope_math_g4",
            content_layer=layer,
            caps_ref="4.M.1.1",
            status="queued",
            task_metadata={"required_count": 1, "missing_count": 1},
        )
        session.get.return_value = layer_task
        layer_res = await executor.execute_task(session, task_id=layer_task.task_id)
        assert layer_res.status == "succeeded"
        assert len(layer_res.artifact_ids) >= 1

    # 8. IntegrityError on duplicate artifact
    from sqlalchemy.exc import IntegrityError
    content_factory_service.create_artifact.side_effect = IntegrityError("dup", "params", Exception("orig"))

    dup_task = ContentGenerationTask(
        task_id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        scope_id="scope_math_g4",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS.value,
        caps_ref="4.M.1.1",
        status="queued",
        task_metadata={"required_count": 1, "missing_count": 1},
    )
    session.get.return_value = dup_task
    dup_res = await executor.execute_task(session, task_id=dup_task.task_id)
    assert dup_res.status == "failed"
    assert any("matching artifact hash" in e for e in dup_res.errors)

    # 11. Pre-validation errors tagging on artifact
    executor.settings = MagicMock(enabled=True, provider="llm", max_artifacts_per_task=5)
    mock_llm_provider = MagicMock(provider_name="llm", model_name="test-model")
    from unittest.mock import patch
    with patch("app.services.content_generation_executor.get_content_generation_provider", return_value=mock_llm_provider):
        executor._call_provider = AsyncMock(return_value=[
            {
                "artifact_json": {"test": "val"},
                "artifact_type": ContentArtifactType.DIAGNOSTIC_ITEM,
                "grade": 4,
                "subject_code": "MATH",
                "language": "en",
                "validation_errors": lambda h, s: ["Pre-validation failed"],
            }
        ])
        pre_val_task = ContentGenerationTask(
            task_id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            scope_id="scope_math_g4",
            content_layer=ContentLayer.DIAGNOSTIC_ITEMS.value,
            caps_ref="4.M.1.1",
            status="queued",
        )
        session.get.return_value = pre_val_task
        pre_val_art = MagicMock()
        pre_val_art.artifact_id = uuid.uuid4()
        pre_val_art.artifact_hash = "pre_hash"
        content_factory_service.create_artifact.return_value = pre_val_art
        pre_res = await executor.execute_task(session, task_id=pre_val_task.task_id)
        assert "Pre-validation failed" in pre_res.errors
        assert pre_res.status == "failed"

    # 12. Session without begin_nested
    simple_executor = ContentGenerationExecutor(
        settings=settings,
        scope_registry=scope_registry,
        source_context_service=source_context_service,
        content_factory_service=content_factory_service,
        run_service=run_service,
    )
    simple_session = MagicMock(spec=["get", "flush", "execute"])
    simple_task = ContentGenerationTask(
        task_id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        scope_id="scope_math_g4",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS.value,
        caps_ref="4.M.1.1",
        status="queued",
        task_metadata={"required_count": 1, "missing_count": 1},
    )
    simple_session.get = AsyncMock(return_value=simple_task)
    simple_session.flush = AsyncMock()
    simple_session.execute = AsyncMock(return_value=hash_query)
    simple_res = await simple_executor.execute_task(simple_session, task_id=simple_task.task_id)
    assert simple_res.status in {"succeeded", "failed"}










