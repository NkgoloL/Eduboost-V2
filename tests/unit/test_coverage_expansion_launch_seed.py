"""
Unit tests for app.services.launch_content_seed pure helpers:
  - _lesson_row
  - _artifact_path
  - module-level constants
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from unittest.mock import MagicMock


from app.services.launch_content_seed import (
    ADVISORY_LOCK,
    DEFAULT_ITEM_TARGET,
    DEFAULT_LESSON_TARGET,
    LAUNCH_SCOPE_ID,
    SEED_LEARNER_GRADE,
    _artifact_path,
    _lesson_row,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_advisory_lock_is_tuple(self):
        assert isinstance(ADVISORY_LOCK, tuple)
        assert len(ADVISORY_LOCK) == 2

    def test_default_targets(self):
        assert DEFAULT_ITEM_TARGET > 0
        assert DEFAULT_LESSON_TARGET > 0

    def test_launch_scope_id(self):
        assert isinstance(LAUNCH_SCOPE_ID, str)
        assert LAUNCH_SCOPE_ID

    def test_seed_learner_grade(self):
        assert isinstance(SEED_LEARNER_GRADE, int)


# ---------------------------------------------------------------------------
# _lesson_row
# ---------------------------------------------------------------------------

class TestLessonRow:
    def _make_lesson(self, **overrides):
        base = {
            "lesson_id": str(uuid.uuid4()),
            "grade": 4,
            "subject": "Mathematics",
            "topic": "Fractions",
            "caps_ref": "CAPS/MATH/GR4",
            "term": 1,
            "subtopic": "Unit fractions",
            "safety_classification": "safe",
            "pii_check_passed": True,
            "answer_key_verified": True,
            "alignment_confidence": 0.95,
            "quality_score": 0.88,
        }
        base.update(overrides)
        return base

    def test_returns_dict_with_required_keys(self):
        lesson = self._make_lesson()
        learner_id = str(uuid.uuid4())
        row = _lesson_row(lesson, learner_id)
        assert row["grade"] == 4
        assert row["subject"] == "Mathematics"
        assert row["caps_ref"] == "CAPS/MATH/GR4"
        assert row["learner_id"] == learner_id

    def test_content_is_json_serialized(self):
        lesson = self._make_lesson()
        row = _lesson_row(lesson, "learner-1")
        parsed = json.loads(row["content"])
        assert parsed["grade"] == lesson["grade"]

    def test_pii_check_passed_is_bool(self):
        lesson = self._make_lesson(pii_check_passed=1)
        row = _lesson_row(lesson, "learner-1")
        assert row["pii_check_passed"] is True

    def test_alignment_confidence_is_float(self):
        lesson = self._make_lesson(alignment_confidence="0.9")
        row = _lesson_row(lesson, "learner-1")
        assert isinstance(row["alignment_confidence"], float)

    def test_quality_score_is_float(self):
        lesson = self._make_lesson(quality_score=None)
        row = _lesson_row(lesson, "learner-1")
        assert row["quality_score"] == 0.0

    def test_default_safety_classification(self):
        lesson = self._make_lesson()
        del lesson["safety_classification"]
        row = _lesson_row(lesson, "learner-1")
        assert row["safety_classification"] == "safe"

    def test_reviewer_id_none_when_missing(self):
        lesson = self._make_lesson()
        row = _lesson_row(lesson, "learner-1")
        assert row["reviewer_id"] is None

    def test_reviewer_id_parsed_when_present(self):
        rid = str(uuid.uuid4())
        lesson = self._make_lesson(reviewer_id=rid)
        row = _lesson_row(lesson, "learner-1")
        assert row["reviewer_id"] == uuid.UUID(rid)

    def test_generation_latency_defaults_to_zero(self):
        lesson = self._make_lesson()
        row = _lesson_row(lesson, "learner-1")
        assert row["generation_latency_ms"] == 0

    def test_variant_type_default(self):
        lesson = self._make_lesson()
        row = _lesson_row(lesson, "learner-1")
        assert row["variant_type"] == "standard"


# ---------------------------------------------------------------------------
# _artifact_path
# ---------------------------------------------------------------------------

class TestArtifactPath:
    def test_uses_configured_path_when_present(self):
        scope = MagicMock()
        scope.artifact_paths = {"diagnostic_items": "data/items"}
        path = _artifact_path(scope, "diagnostic_items", "fallback/items.json")
        assert "data/items" in str(path)

    def test_uses_fallback_when_path_not_configured(self):
        scope = MagicMock()
        scope.artifact_paths = {}
        path = _artifact_path(scope, "lessons", "fallback/lessons.json")
        assert "fallback/lessons.json" in str(path)

    def test_returns_path_object(self):
        scope = MagicMock()
        scope.artifact_paths = None
        path = _artifact_path(scope, "lessons", "fallback.json")
        assert isinstance(path, Path)
