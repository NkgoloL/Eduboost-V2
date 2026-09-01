"""Batch 241 — BlueprintGenerator and ScopeBlueprintGenerator branch coverage expansion.

Tests:
- app/services/content_generation/blueprint_generator.py:
  - generate: deterministic provider and LLM provider paths
  - generate: validation failure status (VALIDATION_FAILED)
  - _validate_blueprint: missing caps_ref, caps_ref mismatch, missing assessment_type, missing question_mix
  - _compute_hash: payload hashing
- app/services/content_generation/scope_blueprint_generator.py:
  - _now_utc, _slug, _safe_ref helpers
  - generate: builds baseline blueprint, topic diagnostic, short practice, and mastery check blueprints
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.models.content_factory import ContentArtifactStatus
from app.services.content_generation.blueprint_generator import (
    BlueprintGenerationResult,
    BlueprintGenerator,
)
from app.services.content_generation.scope_blueprint_generator import (
    ScopeBlueprintGenerator,
    _now_utc,
    _safe_ref,
    _slug,
)


# ---------------------------------------------------------------------------
# BlueprintGenerator Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_blueprint_generator_flow():
    generator = BlueprintGenerator()
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

    # 3. Validation failure path
    with patch.object(
        generator,
        "_generate_deterministic_blueprint",
        return_value={"scope_id": "scope-1", "caps_ref": "mismatched_ref"},
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
def test_blueprint_generator_validation_and_hashing():
    generator = BlueprintGenerator()

    # Missing fields in validation
    errors1 = generator._validate_blueprint({}, "scope-1", "4.M.1.1")
    assert "Missing caps_ref" in errors1
    assert "Missing assessment_type" in errors1
    assert "Missing question_mix" in errors1

    # caps_ref mismatch
    errors2 = generator._validate_blueprint({"caps_ref": "4.M.1.2"}, "scope-1", "4.M.1.1")
    assert any("mismatch" in e for e in errors2)

    # _compute_hash
    h1 = generator._compute_hash({"a": 1, "b": 2})
    h2 = generator._compute_hash({"b": 2, "a": 1})
    assert h1 == h2
    assert len(h1) == 64


# ---------------------------------------------------------------------------
# ScopeBlueprintGenerator Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_scope_blueprint_generator_helpers_and_generation():
    assert _slug("term_1_maths") == "term-1-maths"
    assert _safe_ref("4.M.1.1") == "4-M-1-1"
    assert "T" in _now_utc() and _now_utc().endswith("Z")

    generator = ScopeBlueprintGenerator()
    caps_refs = ["4.M.1.1", "4.M.1.2"]
    contexts = {
        "4.M.1.1": {
            "grade": 4,
            "subject": "Mathematics",
            "topic": "Addition",
            "common_misconceptions": ["Carry over error"],
        },
        "4.M.1.2": {
            "grade": 4,
            "subject": "Mathematics",
            "topic": "Subtraction",
            "common_misconceptions": [],  # fallback tag
        },
    }

    res = generator.generate(
        scope_id="term_1_maths",
        caps_refs=caps_refs,
        contexts=contexts,
        source_context_hashes={"4.M.1.1": "hash_123"},
    )

    assert res["scope"] == "term_1_maths"
    assert res["grade"] == 4
    assert res["subject"] == "Mathematics"
    # 1 baseline + 3 per ref (total 1 + 6 = 7)
    assert len(res["blueprints"]) == 7

    types = [b["type"] for b in res["blueprints"]]
    assert types[0] == "baseline_diagnostic"
    assert "topic_diagnostic" in types
    assert "short_practice_quiz" in types
    assert "mastery_check" in types
