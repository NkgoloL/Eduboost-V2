"""Regression tests for Phase 1 review findings."""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api_v2_deps.auth import require_admin
from app.api_v2_routers import generation
from app.models.content_factory import (
    ContentGenerationTask,
    ContentLayer,
    ContentValidationReport,
)
from app.modules.jobs import WorkerSettings
from app.services.batch_generation import BatchGenerationEngine
from app.services.content_generation.prompt_payloads import SourceContextChunk
from app.services.content_generation.source_context import SourceContextResult
from app.services.content_schemas import DiagnosticItemPayload
from app.services.llm_provider import (
    DeterministicProvider,
    LLMProvider,
    ProviderRouter,
    TokenUsage,
    GenerationResult,
    build_provider_router,
)
from tests.phase01.conftest import VALID_DIAGNOSTIC_ITEM


class _UnexpectedFailureProvider(LLMProvider):
    name = "unexpected"

    async def generate(self, **_: object) -> GenerationResult:
        raise OSError("network reset")

    async def health_check(self) -> bool:
        return False


class _SlowProvider(LLMProvider):
    name = "slow"

    async def generate(self, **_: object) -> GenerationResult:
        await asyncio.sleep(0.05)
        return GenerationResult("late", self.name, "slow-v1", TokenUsage(1, 1, 2), 50)

    async def health_check(self) -> bool:
        return True


def _approved_sources() -> dict[str, list[dict[str, object]]]:
    return {
        "4.M.1.1": [
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "source_title": "Approved Grade 4 source",
                "text": "Multiplication is repeated addition and four times three is twelve.",
                "caps_ref": "4.M.1.1",
                "document_status": "approved",
                "license_status": "government_open",
                "source_hash": "sha256:source-1",
                "chunk_quality_score": 0.95,
            }
        ]
    }


def test_generated_schema_rejects_unknown_fields() -> None:
    payload = {**VALID_DIAGNOSTIC_ITEM, "unapproved_extra": "ignored before fix"}
    with pytest.raises(ValidationError):
        DiagnosticItemPayload.model_validate(payload)


def test_schema_version_is_metadata_not_serialized_field() -> None:
    item = DiagnosticItemPayload.model_validate(VALID_DIAGNOSTIC_ITEM)
    assert item.SCHEMA_VERSION == "1.0"
    assert "SCHEMA_VERSION" not in item.model_dump()


@pytest.mark.asyncio
async def test_unexpected_provider_exception_uses_fallback() -> None:
    fallback = DeterministicProvider()
    fallback.name = "fallback"
    fallback.register_default("safe fallback")
    router = ProviderRouter(
        [_UnexpectedFailureProvider(), fallback],
        max_retries_per_provider=1,
    )
    result = await router.generate(system="s", user="u")
    assert result.text == "safe fallback"
    assert result.provider == "fallback"


@pytest.mark.asyncio
async def test_router_level_timeout_uses_fallback() -> None:
    fallback = DeterministicProvider()
    fallback.name = "fallback"
    fallback.register_default("after timeout")
    router = ProviderRouter(
        [_SlowProvider(), fallback],
        max_retries_per_provider=1,
        request_timeout_seconds=0.005,
    )
    result = await router.generate(system="s", user="u")
    assert result.text == "after timeout"


def test_configured_primary_keeps_other_provider_as_fallback() -> None:
    settings = SimpleNamespace(
        APP_ENV="staging",
        ENVIRONMENT="staging",
        LLM_PROVIDER="groq",
        GROQ_API_KEY="gsk-test",
        GROQ_MODEL="test-groq",
        ANTHROPIC_API_KEY="sk-ant-test",
        ANTHROPIC_MODEL="test-anthropic",
        LLM_TIMEOUT_SECONDS=1,
        LLM_MAX_RETRIES=1,
    )
    router = build_provider_router(settings)
    assert [provider.name for provider in router._providers] == ["groq", "anthropic"]


def test_validation_report_supports_task_only_failures() -> None:
    table = ContentValidationReport.__table__
    assert table.c.artifact_id.nullable is True
    assert table.c.task_id.nullable is True
    assert any(
        constraint.name == "ck_content_validation_reports_subject_present"
        for constraint in table.constraints
    )


def test_generation_request_cannot_supply_actor_or_source_text() -> None:
    with pytest.raises(ValidationError):
        generation.StartRunRequest.model_validate(
            {
                "scope_id": "grade4-maths-en",
                "task_specs": [
                    {"caps_ref": "4.M.1.1", "content_type": "diagnostic_item"}
                ],
                "requested_by": "spoofed-admin",
                "sources_by_caps_ref": {
                    "4.M.1.1": [{"text": "caller supplied source"}]
                },
            }
        )


def test_all_generation_routes_require_admin_dependency() -> None:
    for route in generation.router.routes:
        calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_admin in calls, f"{route.path} does not require admin"


def test_generation_job_and_router_are_registered() -> None:
    assert any(
        getattr(function, "__name__", "") == "generate_content_batch"
        for function in WorkerSettings.functions
    )
    api_source = open("app/api_v2.py", encoding="utf-8").read()
    assert '("generation", generation.router)' in api_source


@pytest.mark.asyncio
async def test_queue_failure_fails_closed_without_inline_execution() -> None:
    now = datetime.now(UTC)
    run = SimpleNamespace(
        run_id=uuid.uuid4(),
        scope_id="grade4-maths-en",
        status="created",
        requested_by="admin-1",
        provider=None,
        run_metadata={},
        created_at=now,
        updated_at=now,
    )
    engine = SimpleNamespace(create_run=AsyncMock(return_value=run))
    class QueueResult:
        def scalar_one_or_none(self):
            return "queued"

    class QueueDB:
        async def execute(self, statement):
            del statement
            return QueueResult()

        async def commit(self):
            return None

        async def rollback(self):
            return None

    db = QueueDB()
    context = SourceContextResult(
        passed=True,
        errors=[],
        chunks=[
            SourceContextChunk(
                source_document_id="doc-1",
                source_chunk_id="chunk-1",
                text="Multiplication is repeated addition.",
                source_title="Approved source",
                source_hash="sha256:source-1",
                source_quality_score=0.9,
                license_status="government_open",
                document_status="approved",
            )
        ],
    )
    body = generation.StartRunRequest.model_validate(
        {
            "scope_id": "grade4-maths-en",
            "task_specs": [
                {"caps_ref": "4.M.1.1", "content_type": "diagnostic_item"}
            ],
        }
    )
    with (
        patch.object(
            generation.ContentGenerationSourceContextService,
            "build_context",
            new=AsyncMock(return_value=context),
        ),
        patch.object(
            generation,
            "enqueue_durable",
            new=AsyncMock(side_effect=RuntimeError("redis unavailable")),
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await generation.start_generation_run(
                body=body,
                auth=SimpleNamespace(user_id="admin-1"),
                db=db,
                engine=engine,
            )
    assert exc_info.value.status_code == 503
    assert engine.create_run.await_count == 1
    assert not hasattr(engine, "process_run")


@pytest.mark.asyncio
async def test_engine_fails_before_provider_when_source_provenance_missing() -> None:
    provider = DeterministicProvider()
    provider.register_default(json.dumps([VALID_DIAGNOSTIC_ITEM]))
    provider_called = False

    async def should_not_generate(**kwargs):
        nonlocal provider_called
        provider_called = True
        raise AssertionError(f"provider should not be called: {kwargs}")

    provider.generate = should_not_generate
    engine = BatchGenerationEngine(provider_router=ProviderRouter([provider]))

    run = SimpleNamespace(run_id=uuid.uuid4(), run_metadata={})
    task = SimpleNamespace(
        task_id=uuid.uuid4(),
        run_id=run.run_id,
        scope_id="grade4-maths-en",
        caps_ref="4.M.1.1",
        task_metadata={
            "content_type": "diagnostic_item",
            "grade": 4,
            "subject": "Mathematics",
            "subject_code": "MATHS",
            "language": "en",
        },
        status="queued",
        attempt_number=1,
        max_attempts=3,
        validation_failures=[],
        artifact_paths=[],
        output_artifact_ids=[],
        locked_by=None,
        lock_expires_at=None,
        started_at=None,
        finished_at=None,
        provider=None,
        model=None,
        prompt_version=None,
        token_usage=None,
        cost_metadata=None,
        admin_actor_id=None,
    )
    class ResultProxy:
        def scalar_one_or_none(self):
            return run

        class Scalars:
            @staticmethod
            def all():
                return [task]

        def scalars(self):
            return self.Scalars()

    class FakeDB:
        def __init__(self):
            self.added = []

        async def execute(self, statement):
            del statement
            return ResultProxy()

        def add(self, obj):
            self.added.append(obj)

        async def flush(self):
            return None

        async def commit(self):
            return None

        async def rollback(self):
            return None

    db = FakeDB()

    with patch(
        "app.services.batch_generation._acquire_task_lock",
        new=AsyncMock(return_value=True),
    ):
        with pytest.raises(ValueError, match="source_snapshot_hash"):
            await engine.process_run(run.run_id, {}, db, worker_id="worker")

    assert provider_called is False
    assert task.status == "failed"
    assert "source_snapshot_hash_missing" in task.validation_failures


@pytest.mark.asyncio
async def test_create_run_idempotency_keys_are_run_scoped() -> None:
    provider = DeterministicProvider()
    provider.register_default(json.dumps([VALID_DIAGNOSTIC_ITEM]))
    engine = BatchGenerationEngine(provider_router=ProviderRouter([provider]))
    spec = generation.GenerationTaskSpec(
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        content_type="diagnostic_item",
    )

    async def one_run() -> str:
        added: list[object] = []
        class CreateRunDB:
            def add(self, obj):
                added.append(obj)

            async def flush(self):
                return None

            async def commit(self):
                return None

        db = CreateRunDB()
        await engine.create_run(
            scope_id="grade4-maths-en",
            task_specs=[spec],
            sources_by_caps_ref=_approved_sources(),
            requested_by="admin-1",
            db=db,
        )
        task = next(obj for obj in added if isinstance(obj, ContentGenerationTask))
        return task.idempotency_key

    assert await one_run() != await one_run()
