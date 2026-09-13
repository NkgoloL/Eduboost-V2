import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError

from app.models.content_factory import (
    ContentGenerationTask,
    ContentLayer,
    ContentArtifactType,
)
from app.services.content_generation.prompt_payloads import SourceContextChunk
from app.services.content_generation.provider_factory import GenerationSettings
from app.services.content_generation_executor import (
    ContentGenerationExecutor,
    GenerationDisabledError,
    TaskExecutionResult,
)



@pytest.mark.asyncio
async def test_execute_task_edge_conditions():
    settings = GenerationSettings(
        enabled=True,
        provider="deterministic",
        max_artifacts_per_task=10,
        max_scope_run_artifacts=100,
    )
    executor = ContentGenerationExecutor(settings=settings)
    session = AsyncMock()

    # 1. Task not found -> LookupError
    session.get.return_value = None
    with pytest.raises(LookupError, match="not found"):
        await executor.execute_task(session, uuid.uuid4())

    # 2. Task already succeeded -> skipped result
    task_done = MagicMock(
        task_id=uuid.uuid4(),
        status="succeeded",
    )
    session.get.return_value = task_done
    res_skipped = await executor.execute_task(session, task_done.task_id)
    assert res_skipped.status == "skipped"

    # 3. Context failed -> task failed
    task_queued = MagicMock(
        task_id=uuid.uuid4(),
        status="queued",
        scope_id="scope-1",
        caps_ref="4.M.1",
        content_layer="diagnostic_items",
        run_id=uuid.uuid4(),
        prompt_version="cf-v1",
        task_metadata={},
    )
    session.get.return_value = task_queued

    executor.source_context_service = MagicMock()
    mock_bad_ctx = MagicMock(passed=False, errors=["No approved sources"])
    executor.source_context_service.build_context = AsyncMock(return_value=mock_bad_ctx)

    res_ctx_failed = await executor.execute_task(session, task_queued.task_id)
    assert res_ctx_failed.status == "failed"
    assert "No approved sources" in res_ctx_failed.errors[0]

    # 4. Provider call raises Exception -> task failed
    mock_good_ctx = MagicMock(passed=True, chunks=[MagicMock(source_chunk_id="chk-1", source_document_id="doc-1", source_quality_score=0.9, license_status="open")])
    executor.source_context_service.build_context = AsyncMock(return_value=mock_good_ctx)

    executor._call_provider = AsyncMock(side_effect=RuntimeError("Provider offline"))
    res_prov_failed = await executor.execute_task(session, task_queued.task_id)
    assert res_prov_failed.status == "failed"
    assert "Provider offline" in res_prov_failed.errors[0]

    # 5. IntegrityError on create_artifact handled cleanly
    del session.begin_nested
    executor._call_provider = AsyncMock(return_value=[
        {
            "artifact_json": {"title": "A1"},
            "artifact_type": ContentArtifactType.DIAGNOSTIC_ITEM,
            "grade": 4,
            "subject_code": "MATHS",
            "language": "en",
            "validation_errors": lambda hash_val, existing: [],
        }
    ])
    executor._existing_hashes = AsyncMock(return_value=set())
    executor.content_factory_service = MagicMock()
    executor.content_factory_service.create_artifact = AsyncMock(side_effect=IntegrityError("stmt", "params", Exception("orig")))

    res_integrity = await executor.execute_task(session, task_queued.task_id)
    assert res_integrity.status == "failed"
    assert any("matching artifact hash already exists" in e for e in res_integrity.errors)

    # 6. Generic Exception on create_artifact -> task failed
    executor.content_factory_service.create_artifact = AsyncMock(side_effect=ValueError("Schema mismatch"))
    res_create_failed = await executor.execute_task(session, task_queued.task_id)
    assert res_create_failed.status == "failed"
    assert any("Artifact creation failed: Schema mismatch" in e for e in res_create_failed.errors)


@pytest.mark.asyncio
async def test_execute_run_and_execution_report():
    settings = GenerationSettings(
        enabled=True,
        provider="deterministic",
        max_artifacts_per_task=10,
        max_scope_run_artifacts=100,
    )
    executor = ContentGenerationExecutor(settings=settings)
    session = AsyncMock()

    run_id = uuid.uuid4()
    mock_run = MagicMock(run_id=run_id, status="draft")
    t1 = MagicMock(task_id=uuid.uuid4(), status="queued", output_artifact_ids=["art-1"])
    t2 = MagicMock(task_id=uuid.uuid4(), status="failed", output_artifact_ids=[])

    executor.run_service = MagicMock()
    executor.run_service.get_run = AsyncMock(return_value=mock_run)
    executor.run_service.get_run_tasks = AsyncMock(return_value=[t1, t2])

    # 1. execute_run with max_tasks=1
    executor.execute_task = AsyncMock(return_value=TaskExecutionResult(t1.task_id, "succeeded", [uuid.uuid4()]))
    run_res = await executor.execute_run(session, run_id, max_tasks=1)
    assert run_res.status == "succeeded"
    assert run_res.summary["tasks_executed"] == 1

    # 2. execution_report
    report = await executor.execution_report(session, run_id)
    assert report["run_id"] == str(run_id)
    assert report["tasks"] == 2
    assert report["queued"] == 1
    assert report["failed"] == 1
    assert report["artifacts"] == 1


@pytest.mark.asyncio
async def test_call_provider_all_layer_branches():
    settings = GenerationSettings(
        enabled=True,
        provider="deterministic",
        max_artifacts_per_task=10,
        max_scope_run_artifacts=100,
    )
    executor = ContentGenerationExecutor(settings=settings)
    executor.scope_registry = MagicMock()
    executor.scope_registry.get_scope.return_value = MagicMock(grade=4, subject_code="MATHS", language="en")
    provider = MagicMock()


    chunk = SourceContextChunk(
        source_chunk_id="chk-1",
        source_document_id="doc-1",
        text="Sample context",
        source_quality_score=0.9,
        license_status="government_open",
        document_status="approved",
    )


    # 1. Lessons layer
    task_lesson = MagicMock(
        content_layer=ContentLayer.LESSONS.value,
        scope_id="scope-1",
        caps_ref="4.M.1",
        task_metadata={"grade": 4, "subject_code": "MATHS", "language": "en"},
        prompt_version="v1",
    )
    mock_lesson = MagicMock()
    mock_lesson.to_artifact_json.return_value = {"title": "L1"}
    mock_lesson.grade = 4
    mock_lesson.subject_code = "MATHS"
    mock_lesson.language = "en"
    provider.generate_lessons = AsyncMock(return_value=[mock_lesson])

    payloads_lesson = await executor._call_provider(provider, task_lesson, [chunk])
    assert len(payloads_lesson) == 1
    assert payloads_lesson[0]["artifact_type"] == ContentArtifactType.LESSON

    # 2. Assessment blueprints layer
    task_blueprints = MagicMock(
        content_layer=ContentLayer.ASSESSMENT_BLUEPRINTS.value,
        scope_id="scope-1",
        caps_ref="4.M.1",
        task_metadata={"grade": 4, "subject_code": "MATHS", "language": "en"},
        prompt_version="v1",
    )
    provider.generate_assessment_blueprints = AsyncMock(return_value=[{"title": "BP1"}])
    payloads_bp = await executor._call_provider(provider, task_blueprints, [chunk])
    assert len(payloads_bp) == 1
    assert payloads_bp[0]["artifact_type"] == ContentArtifactType.ASSESSMENT_BLUEPRINT

    # 3. Study plan templates layer
    task_templates = MagicMock(
        content_layer=ContentLayer.STUDY_PLAN_TEMPLATES.value,
        scope_id="scope-1",
        caps_ref="4.M.1",
        task_metadata={"grade": 4, "subject_code": "MATHS", "language": "en"},
        prompt_version="v1",
    )
    provider.generate_study_plan_templates = AsyncMock(return_value=[{"title": "SP1"}])
    payloads_sp = await executor._call_provider(provider, task_templates, [chunk])
    assert len(payloads_sp) == 1
    assert payloads_sp[0]["artifact_type"] == ContentArtifactType.STUDY_PLAN_TEMPLATE

    # 4. Unsupported layer -> ValueError
    task_bad = MagicMock(content_layer="unsupported_layer", scope_id="scope-1", task_metadata={})
    with pytest.raises(ValueError, match="Unsupported generation layer"):
        await executor._call_provider(provider, task_bad, [chunk])
