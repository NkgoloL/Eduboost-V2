from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.models.content_factory import ContentGenerationTask, ContentLayer
from app.services.content_generation.provider_factory import GenerationSettings
from app.services.content_generation.providers.deterministic import DeterministicContentGenerationProvider
from app.services.content_generation.prompt_payloads import SourceContextChunk
from app.services.content_generation.prompt_payloads import LessonGenerationRequest
from app.services.content_generation.source_context import SourceContextResult
from app.services.content_generation_executor import ContentGenerationExecutor, GenerationDisabledError


class Result:
    def __init__(self, rows=None):
        self.rows = rows or []
    def all(self):
        return self.rows


class Session:
    def __init__(self, task):
        self.task = task
        self.added = []
        self._flushed = False
    async def get(self, model, key):
        return self.task
    async def execute(self, stmt):
        return Result([])
    def add(self, obj):
        self.added.append(obj)
    async def flush(self):
        self._flushed = True
        return None
    async def refresh(self, obj):
        return None
    class NestedTransaction:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return None
    def begin_nested(self):
        return self.NestedTransaction()


class Registry:
    def get_scope(self, scope_id):
        return SimpleNamespace(scope_id=scope_id, grade=4, subject_code="MAT", language="en")


class Sources:
    async def build_context(self, session, *, scope_id, caps_ref, limit=8):
        return SourceContextResult(True, [], [SourceContextChunk(source_document_id="doc", source_chunk_id="chunk", text="text", license_status="government_open", source_quality_score=0.9)])


class Factory:
    async def create_artifact(self, session, *, payload):
        artifact = SimpleNamespace(artifact_id=uuid.uuid4(), artifact_hash="hash-" + str(len(session.added)), status="pending_review", sources=payload["sources"])
        session.add(artifact)
        return artifact


def _task(layer=ContentLayer.DIAGNOSTIC_ITEMS):
    return ContentGenerationTask(task_id=uuid.uuid4(), run_id=uuid.uuid4(), scope_id="grade4_mathematics_en", caps_ref="4.M.1.1", content_layer=layer, status="queued", task_metadata={"missing_count": 1, "grade": 4, "subject_code": "MAT", "language": "en"})


def _lesson_request(language: str) -> LessonGenerationRequest:
    return LessonGenerationRequest(
        scope_id=f"grade4_mathematics_{language}",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MAT",
        language=language,
        topic_title="Fractions",
        required_count=1,
        approved_count=0,
        missing_count=1,
        source_chunks=[
            SourceContextChunk(
                source_document_id="doc",
                source_chunk_id="chunk",
                text="Fractions describe equal parts of a whole.",
                license_status="government_open",
                source_quality_score=0.9,
            )
        ],
        source_document_ids=["doc"],
        source_chunk_ids=["chunk"],
    )


@pytest.mark.asyncio
async def test_executor_refuses_when_generation_disabled() -> None:
    executor = ContentGenerationExecutor(settings=GenerationSettings(False, "deterministic", 10, 250), scope_registry=Registry(), source_context_service=Sources(), content_factory_service=Factory())

    with pytest.raises(GenerationDisabledError):
        await executor.execute_task(Session(_task()), uuid.uuid4())


@pytest.mark.asyncio
async def test_valid_deterministic_artifact_enters_pending_review_and_has_sources() -> None:
    """Executor must create artifact in PENDING_REVIEW status with sources attached."""
    task = _task()
    session = Session(task)
    executor = ContentGenerationExecutor(
        settings=GenerationSettings(True, "deterministic", 10, 250),
        scope_registry=Registry(),
        source_context_service=Sources(),
        content_factory_service=Factory()
    )

    result = await executor.execute_task(session, task.task_id, actor_id="admin")

    assert result.status == "succeeded"
    assert session.added[0].status == "pending_review"
    assert session.added[0].sources[0]["source_chunk_id"] == "chunk"
    assert task.output_artifact_ids


@pytest.mark.asyncio
async def test_deterministic_lesson_generation_preserves_supported_languages() -> None:
    """Local CI smoke proof: one generated lesson per supported language."""
    provider = DeterministicContentGenerationProvider()

    for language in ("en", "zu", "af", "xh"):
        lessons = await provider.generate_lessons(_lesson_request(language))

        assert len(lessons) == 1
        assert lessons[0].language == language
        assert lessons[0].source_chunk_ids == ["chunk"]
        assert lessons[0].safety_status == "passed"


@pytest.mark.asyncio
async def test_invalid_generated_artifact_enters_validation_failed() -> None:
    """Executor must mark task as failed when validation errors occur."""
    class BadProvider:
        provider_name = "deterministic"
        model_name = "bad"
        async def generate_diagnostic_items(self, request):
            from app.services.content_generation.prompt_payloads import GeneratedDiagnosticItem
            return [GeneratedDiagnosticItem(
                question_text="Q",
                options=["A", "B"],
                correct_answer="",  # Invalid: empty correct answer
                explanation="",
                caps_ref=request.caps_ref,
                grade=4,
                subject_code="MAT",
                language="en",
                source_chunk_ids=[]
            )]
        async def generate_lessons(self, request):
            return []

    import app.services.content_generation_executor as module
    original = module.get_content_generation_provider
    module.get_content_generation_provider = lambda settings: BadProvider()

    try:
        task = _task()
        session = Session(task)
        executor = ContentGenerationExecutor(
            settings=GenerationSettings(True, "deterministic", 10, 250),
            scope_registry=Registry(),
            source_context_service=Sources(),
            content_factory_service=Factory()
        )
        result = await executor.execute_task(session, task.task_id, actor_id="admin")
    finally:
        module.get_content_generation_provider = original

    assert result.status == "failed"
    # Validation errors prevent artifact creation, so no artifacts are added
    assert result.errors
