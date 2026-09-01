"""Batch 238 — Study Plan Template Generator & Scope Study Plan Generator branch coverage expansion.

Tests:
- app/services/content_generation/study_plan_template_generator.py:
  - generate: deterministic provider and non-deterministic provider
  - generate: validation failure status (VALIDATION_FAILED)
  - _validate_template: missing caps_ref, caps_ref mismatch, missing triggers, missing minutes
  - _compute_hash: deterministic payload hashing
- app/services/content_generation/scope_study_plan_generator.py:
  - _now_utc and _slug helpers
  - _cycle and _teacher_cue helper branches (lesson, practice, review / default)
  - generate: full schedule generation with remediation and extension blueprints
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.models.content_factory import ContentArtifactStatus
from app.services.content_generation.scope_study_plan_generator import (
    ScopeStudyPlanGenerator,
    _cycle,
    _now_utc,
    _slug,
    _teacher_cue,
)
from app.services.content_generation.study_plan_template_generator import (
    StudyPlanTemplateGenerationResult,
    StudyPlanTemplateGenerator,
)


# ---------------------------------------------------------------------------
# StudyPlanTemplateGenerator Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_study_plan_template_generator_flow():
    generator = StudyPlanTemplateGenerator()
    mock_session = AsyncMock()

    # 1. Deterministic generation success
    res_det = await generator.generate(
        mock_session,
        scope_id="scope-1",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATHS",
        language="en",
        provider="deterministic",
    )
    assert res_det.status == ContentArtifactStatus.PENDING_REVIEW.value
    assert res_det.errors == []
    mock_session.add.assert_called()
    mock_session.flush.assert_called()

    # 2. Non-deterministic provider path
    res_llm = await generator.generate(
        mock_session,
        scope_id="scope-1",
        caps_ref="4.M.1.1",
        grade=4,
        subject_code="MATHS",
        language="en",
        provider="anthropic",
    )
    assert res_llm.status == ContentArtifactStatus.PENDING_REVIEW.value

    # 3. Validation failure branch
    with patch.object(
        generator,
        "_generate_deterministic_template",
        return_value={"scope_id": "scope-1", "caps_ref": "wrong_ref"},
    ):
        res_fail = await generator.generate(
            mock_session,
            scope_id="scope-1",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATHS",
        )
        assert res_fail.status == ContentArtifactStatus.VALIDATION_FAILED.value
        assert len(res_fail.errors) > 0


@pytest.mark.unit
def test_study_plan_template_generator_validation_and_hashing():
    generator = StudyPlanTemplateGenerator()

    # Missing fields in validation
    errors1 = generator._validate_template({}, "scope-1", "4.M.1.1")
    assert "Missing caps_ref" in errors1
    assert "Missing diagnostic_trigger_conditions" in errors1
    assert "Missing estimated_minutes" in errors1

    # caps_ref mismatch
    errors2 = generator._validate_template({"caps_ref": "4.M.1.2"}, "scope-1", "4.M.1.1")
    assert any("mismatch" in e for e in errors2)

    # _compute_hash
    h1 = generator._compute_hash({"a": 1, "b": 2})
    h2 = generator._compute_hash({"b": 2, "a": 1})
    assert h1 == h2
    assert len(h1) == 64


# ---------------------------------------------------------------------------
# ScopeStudyPlanGenerator Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_scope_study_plan_generator_helpers():
    assert _slug("term_1_maths") == "term-1-maths"
    assert "T" in _now_utc() and _now_utc().endswith("Z")
    assert _cycle(("A", "B"), 0) == "A"
    assert _cycle(("A", "B"), 1) == "B"
    assert _cycle(("A", "B"), 2) == "A"

    cue_lesson = _teacher_cue("lesson", "Fractions")
    assert "Teach Fractions" in cue_lesson
    cue_practice = _teacher_cue("practice", "Fractions")
    assert "practice quiz" in cue_practice
    cue_review = _teacher_cue("review", "Fractions")
    assert cue_review is not None


@pytest.mark.unit
def test_scope_study_plan_generator_generate():
    scope_gen = ScopeStudyPlanGenerator()
    caps_refs = ["4.M.1.1", "4.M.1.2"]
    contexts = {
        "4.M.1.1": {
            "grade": 4,
            "subject": "Mathematics",
            "topic": "Addition",
            "subtopic": "2-digit Addition",
            "term": 1,
            "prerequisites": ["Number Sense"],
            "common_misconceptions": ["Carry over error"],
            "assessment_standards": ["Adds numbers"],
        },
        "4.M.1.2": {
            "grade": 4,
            "subject": "Mathematics",
            "topic": "Subtraction",
            "subtopic": None,  # fallback to topic
            "term": 1,
            "prerequisites": [],
            "common_misconceptions": [],  # fallback tag
            "assessment_standards": [],
        },
    }

    result = scope_gen.generate(
        scope_id="term_1_maths",
        caps_refs=caps_refs,
        contexts=contexts,
        source_context_hashes={"4.M.1.1": "hash_123"},
    )

    assert result["scope"] == "term_1_maths"
    assert result["grade"] == 4
    assert result["subject"] == "Mathematics"
    assert len(result["weekly_template"]) == 5
    assert len(result["topic_sequence"]) == 2
    assert len(result["remediation_mappings"]) >= 2
    assert len(result["extension_mappings"]) == 2
    assert "pacing_guidance" in result
