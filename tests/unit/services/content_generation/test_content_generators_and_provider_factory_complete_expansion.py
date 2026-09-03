from unittest.mock import AsyncMock, MagicMock
import os
import pytest

from app.models.content_factory import ContentArtifactStatus
from app.services.content_generation.blueprint_generator import (
    BlueprintGenerationResult,
    BlueprintGenerator,
)
from app.services.content_generation.diagnostic_generator import DiagnosticGenerator
from app.services.content_generation.lesson_generator import LessonGenerator
from app.services.content_generation.prompt_payloads import (
    GeneratedDiagnosticItem,
    GeneratedLesson,
)
from app.services.content_generation.provider_factory import (
    GenerationSettings,
    get_content_generation_provider,
    get_generation_settings,
)
from app.services.content_generation.providers.deterministic import DeterministicContentGenerationProvider
from app.services.content_generation.providers.llm import LLMContentGenerationProvider


@pytest.mark.asyncio
async def test_blueprint_generator_lifecycle():
    gen = BlueprintGenerator()
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()

    # 1. Successful deterministic generation
    res = await gen.generate(
        session,
        scope_id="scope_test",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
    )
    assert isinstance(res, BlueprintGenerationResult)
    assert res.status == ContentArtifactStatus.PENDING_REVIEW.value
    assert session.add.called
    assert session.flush.await_count == 1

    # 2. Validation failure branch
    bad_payload = {"caps_ref": "mismatch_ref"}
    errors = gen._validate_blueprint(bad_payload, "scope_test", "4.M.1.1")
    assert len(errors) >= 3
    assert any("mismatch" in e for e in errors)
    assert any("assessment_type" in e for e in errors)
    assert any("question_mix" in e for e in errors)


def test_diagnostic_and_lesson_generators():
    diag_gen = DiagnosticGenerator()
    item = GeneratedDiagnosticItem(
        question_text="What is 3 + 3?",
        options=["5", "6"],
        correct_answer="6",
        explanation="3 + 3 = 6",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        source_chunk_ids=["chunk_1"],
    )
    # Valid
    assert diag_gen.validate(item, caps_ref="4.M.1.1") == []

    # Invalid item
    bad_item = GeneratedDiagnosticItem(
        question_text="What is 3 + 3?",
        options=["5"],
        correct_answer="6",
        explanation="",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        source_chunk_ids=[],
    )
    errs = diag_gen.validate(
        bad_item,
        caps_ref="OTHER.REF",
        existing_hashes={"dup_hash"},
        artifact_hash="dup_hash",
    )
    assert len(errs) >= 4

    # Lesson generator
    lesson_gen = LessonGenerator()
    lesson = GeneratedLesson(
        title="Place Value",
        summary="Summary",
        learning_objectives=["Understand tens and units"],
        teacher_notes="Notes",
        learner_activity="Activity",
        worked_examples=["Example"],
        practice_questions=["Question 1"],
        answer_key=["Answer 1"],
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        language="en",
        source_chunk_ids=["chunk_1"],
    )
    assert lesson_gen.validate(lesson, caps_ref="4.M.1.1") == []

    bad_lesson = GeneratedLesson(
        title="Place Value",
        summary="Summary",
        learning_objectives=[],
        teacher_notes="Notes",
        learner_activity="Activity",
        worked_examples=[],
        practice_questions=["Question 1"],
        answer_key=[],
        caps_ref="4.M.1.1",
        grade=15,
        subject_code="MATH",
        language="en",
        source_chunk_ids=[],
    )
    lesson_errs = lesson_gen.validate(
        bad_lesson,
        caps_ref="OTHER.REF",
        existing_hashes={"dup"},
        artifact_hash="dup",
    )
    assert len(lesson_errs) >= 5


def test_provider_factory(monkeypatch):
    monkeypatch.setenv("CONTENT_FACTORY_GENERATION_ENABLED", "true")
    monkeypatch.setenv("CONTENT_FACTORY_PROVIDER", "deterministic")
    monkeypatch.setenv("APP_ENV", "development")

    settings = get_generation_settings()
    assert settings.enabled is True
    assert settings.provider == "deterministic"

    provider = get_content_generation_provider(settings)
    assert isinstance(provider, DeterministicContentGenerationProvider)

    # Production check for deterministic provider
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(RuntimeError, match="forbidden in production"):
        get_content_generation_provider(settings)

    # LLM provider
    llm_settings = GenerationSettings(
        enabled=True,
        provider="llm",
        max_artifacts_per_task=5,
        max_scope_run_artifacts=50,
    )
    llm_provider = get_content_generation_provider(llm_settings)
    assert isinstance(llm_provider, LLMContentGenerationProvider)

    # LLM disabled check
    disabled_llm_settings = GenerationSettings(
        enabled=False,
        provider="llm",
        max_artifacts_per_task=5,
        max_scope_run_artifacts=50,
    )
    with pytest.raises(RuntimeError, match="must be true before using the LLM"):
        get_content_generation_provider(disabled_llm_settings)

    # Disabled provider
    disabled_settings = GenerationSettings(
        enabled=True,
        provider="disabled",
        max_artifacts_per_task=5,
        max_scope_run_artifacts=50,
    )
    with pytest.raises(RuntimeError, match="is disabled"):
        get_content_generation_provider(disabled_settings)

    # Unsupported provider
    invalid_settings = GenerationSettings(
        enabled=True,
        provider="unknown_provider",
        max_artifacts_per_task=5,
        max_scope_run_artifacts=50,
    )
    with pytest.raises(ValueError, match="Unsupported content generation provider"):
        get_content_generation_provider(invalid_settings)
