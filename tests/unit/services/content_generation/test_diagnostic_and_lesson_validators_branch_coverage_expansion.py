"""Batch 242 — DiagnosticGenerator and LessonGenerator validation branch coverage expansion.

Tests:
- app/services/content_generation/diagnostic_generator.py:
  - Missing correct answer
  - Single choice: less than 2 options
  - Single choice: correct answer not in options / multiple occurrences
  - Missing explanation
  - CAPS ref mismatch
  - Missing source citations
  - Duplicate artifact hash
  - Valid item
- app/services/content_generation/lesson_generator.py:
  - Missing learning objectives
  - Practice questions present without answer key
  - CAPS ref mismatch
  - Missing source citations
  - Invalid grade out of range (< 0 or > 12)
  - Duplicate artifact hash
  - Valid lesson
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services.content_generation.diagnostic_generator import DiagnosticGenerator
from app.services.content_generation.lesson_generator import LessonGenerator


# ---------------------------------------------------------------------------
# DiagnosticGenerator Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_diagnostic_generator_validation_branches():
    validator = DiagnosticGenerator()

    # 1. Missing correct answer & explanation & source chunks
    item_empty = SimpleNamespace(
        correct_answer="",
        item_type="single_choice",
        options=["A"],
        explanation="",
        caps_ref="4.M.1.2",
        source_chunk_ids=[],
    )
    errors = validator.validate(
        item_empty,
        caps_ref="4.M.1.1",
        existing_hashes={"hash_123"},
        artifact_hash="hash_123",
    )
    assert any("answer key" in e for e in errors)
    assert any("at least two options" in e for e in errors)
    assert any("explanation" in e for e in errors)
    assert any("does not match task caps_ref" in e for e in errors)
    assert any("source citations" in e for e in errors)
    assert any("duplicates an existing artifact hash" in e for e in errors)

    # 2. Correct answer count != 1
    item_opts = SimpleNamespace(
        correct_answer="C",
        item_type="single_choice",
        options=["A", "B"],
        explanation="Explanation text",
        caps_ref="4.M.1.1",
        source_chunk_ids=["chunk-1"],
    )
    errors_opts = validator.validate(item_opts, caps_ref="4.M.1.1")
    assert any("exactly one correct answer" in e for e in errors_opts)

    # 3. Clean valid item
    item_valid = SimpleNamespace(
        correct_answer="B",
        item_type="single_choice",
        options=["A", "B"],
        explanation="Full explanation",
        caps_ref="4.M.1.1",
        source_chunk_ids=["chunk-1"],
    )
    errors_valid = validator.validate(item_valid, caps_ref="4.M.1.1")
    assert errors_valid == []


# ---------------------------------------------------------------------------
# LessonGenerator Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_lesson_generator_validation_branches():
    validator = LessonGenerator()

    # 1. Missing objectives, practice without answer key, caps mismatch, grade out of bounds, duplicate hash
    lesson_bad = SimpleNamespace(
        learning_objectives=[],
        practice_questions=["What is 2+2?"],
        answer_key="",
        caps_ref="4.M.1.2",
        source_chunk_ids=[],
        grade=14,
    )
    errors = validator.validate(
        lesson_bad,
        caps_ref="4.M.1.1",
        existing_hashes={"hash_999"},
        artifact_hash="hash_999",
    )
    assert any("learning objectives" in e for e in errors)
    assert any("answer key for practice questions" in e for e in errors)
    assert any("does not match task caps_ref" in e for e in errors)
    assert any("source citations" in e for e in errors)
    assert any("age appropriate" in e for e in errors)
    assert any("duplicates an existing artifact hash" in e for e in errors)

    # 2. Clean valid lesson
    lesson_valid = SimpleNamespace(
        learning_objectives=["Understand fractions"],
        practice_questions=["What is 1/2 of 4?"],
        answer_key="2",
        caps_ref="4.M.1.1",
        source_chunk_ids=["chunk-1"],
        grade=4,
    )
    errors_valid = validator.validate(lesson_valid, caps_ref="4.M.1.1")
    assert errors_valid == []
