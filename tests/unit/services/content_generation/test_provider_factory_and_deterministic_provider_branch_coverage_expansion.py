"""Batch 243 — Provider factory and deterministic provider branch coverage expansion.

Tests:
- app/services/content_generation/provider_factory.py:
  - get_generation_settings from env
  - get_content_generation_provider:
    - deterministic: production forbidden error vs dev success
    - llm: disabled error vs enabled success
    - disabled provider error
    - unsupported provider ValueError
- app/services/content_generation/providers/deterministic.py:
  - generate_diagnostic_items
  - generate_lessons
  - generate_assessment_blueprints
  - generate_study_plan_templates
"""
from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    LessonGenerationRequest,
)
from app.services.content_generation.provider_factory import (
    GenerationSettings,
    get_content_generation_provider,
    get_generation_settings,
)
from app.services.content_generation.providers.deterministic import (
    DeterministicContentGenerationProvider,
)
from app.services.content_generation.providers.llm import LLMContentGenerationProvider


# ---------------------------------------------------------------------------
# Provider Factory Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_generation_settings_and_providers():
    with patch.dict(os.environ, {
        "CONTENT_FACTORY_GENERATION_ENABLED": "true",
        "CONTENT_FACTORY_PROVIDER": "llm",
        "CONTENT_FACTORY_MAX_ARTIFACTS_PER_TASK": "15",
        "CONTENT_FACTORY_MAX_SCOPE_RUN_ARTIFACTS": "300",
    }):
        settings = get_generation_settings()
        assert settings.enabled is True
        assert settings.provider == "llm"
        assert settings.max_artifacts_per_task == 15
        assert settings.max_scope_run_artifacts == 300

    # 1. Deterministic provider in production -> RuntimeError
    with patch.dict(os.environ, {"APP_ENV": "production"}):
        settings_det = GenerationSettings(
            enabled=True,
            provider="deterministic",
            max_artifacts_per_task=10,
            max_scope_run_artifacts=250,
        )
        with pytest.raises(RuntimeError, match="forbidden in production"):
            get_content_generation_provider(settings_det)

    # 2. Deterministic provider in development -> Success
    with patch.dict(os.environ, {"APP_ENV": "development"}):
        prov_det = get_content_generation_provider(settings_det)
        assert isinstance(prov_det, DeterministicContentGenerationProvider)

    # 3. LLM provider disabled -> RuntimeError
    settings_llm_dis = GenerationSettings(
        enabled=False,
        provider="llm",
        max_artifacts_per_task=10,
        max_scope_run_artifacts=250,
    )
    with pytest.raises(RuntimeError, match="must be true"):
        get_content_generation_provider(settings_llm_dis)

    # 4. LLM provider enabled -> Success
    settings_llm_en = GenerationSettings(
        enabled=True,
        provider="llm",
        max_artifacts_per_task=10,
        max_scope_run_artifacts=250,
    )
    prov_llm = get_content_generation_provider(settings_llm_en)
    assert isinstance(prov_llm, LLMContentGenerationProvider)

    # 5. Disabled provider
    settings_disabled = GenerationSettings(
        enabled=True,
        provider="disabled",
        max_artifacts_per_task=10,
        max_scope_run_artifacts=250,
    )
    with pytest.raises(RuntimeError, match="is disabled"):
        get_content_generation_provider(settings_disabled)

    # 6. Unsupported provider
    settings_unsupported = GenerationSettings(
        enabled=True,
        provider="unknown_provider",
        max_artifacts_per_task=10,
        max_scope_run_artifacts=250,
    )
    with pytest.raises(ValueError, match="Unsupported"):
        get_content_generation_provider(settings_unsupported)


# ---------------------------------------------------------------------------
# Deterministic Provider Generation Methods
# ---------------------------------------------------------------------------

from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    LessonGenerationRequest,
    SourceContextChunk,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_deterministic_provider_generation_methods():
    provider = DeterministicContentGenerationProvider()
    chunk = SourceContextChunk(
        source_document_id="doc-1",
        source_chunk_id="chunk-1",
        text="Sample lesson text chunk.",
    )

    # 1. generate_diagnostic_items
    diag_req = DiagnosticGenerationRequest(
        scope_id="scope-1",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        topic_title="Addition",
        language="en",
        required_count=5,
        approved_count=3,
        missing_count=2,
        source_chunks=[chunk],
        source_chunk_ids=["chunk-1"],
    )
    diag_items = await provider.generate_diagnostic_items(diag_req)
    assert len(diag_items) == 2
    assert diag_items[0].correct_answer == "A"

    # 2. generate_lessons
    lesson_req = LessonGenerationRequest(
        scope_id="scope-1",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATH",
        topic_title="Addition",
        language="en",
        required_count=5,
        approved_count=4,
        missing_count=1,
        source_chunks=[chunk],
        source_chunk_ids=["chunk-1"],
    )
    lessons = await provider.generate_lessons(lesson_req)
    assert len(lessons) == 1
    assert "Understand Addition" in lessons[0].learning_objectives

    # 3. generate_assessment_blueprints
    bp_req = {
        "missing_count": 2,
        "caps_ref": "4.M.1.1",
        "scope_id": "scope-1",
        "grade": 4,
        "subject_code": "MATH",
        "language": "en",
        "source_chunk_ids": ["chunk-1"],
    }
    blueprints = await provider.generate_assessment_blueprints(bp_req)
    assert len(blueprints) == 2
    assert blueprints[0]["assessment_type"] == "summative"

    # 4. generate_study_plan_templates
    sp_req = {
        "missing_count": 1,
        "caps_ref": "4.M.1.1",
        "scope_id": "scope-1",
        "grade": 4,
        "subject_code": "MATH",
        "language": "en",
        "source_chunk_ids": ["chunk-1"],
    }
    templates = await provider.generate_study_plan_templates(sp_req)
    assert len(templates) == 1
    assert templates[0]["estimated_minutes"] == 45
