"""Comprehensive unit tests for ContentLearnerReadService models and read modes."""
from __future__ import annotations

import pytest

from app.services.content_learner_read_service import (
    LearnerDiagnosticItem,
    LearnerLesson,
    LearnerScopeContentSummary,
    LearnerReadMode,
    ContentLearnerReadService,
)


class TestLearnerReadModels:
    def test_learner_diagnostic_item_dataclass(self):
        item = LearnerDiagnosticItem(
            artifact_id="art-100",
            scope_id="grade4_mathematics_en",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATH",
            language="en",
            title="Addition Practice",
            payload={"question": "2 + 2 = ?"},
            source_artifact_hash="hash-123",
            promotion_event_id="prom-1",
            created_at="2026-08-28T00:00:00Z",
        )
        assert item.artifact_id == "art-100"
        assert item.grade == 4
        assert item.subject_code == "MATH"

    def test_learner_lesson_dataclass(self):
        lesson = LearnerLesson(
            artifact_id="les-200",
            scope_id="grade4_mathematics_en",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATH",
            language="en",
            title="Understanding Fractions",
            payload={"explanation": "Fractions represent parts of a whole."},
            source_artifact_hash="hash-456",
            promotion_event_id="prom-2",
            created_at="2026-08-28T00:00:00Z",
        )
        assert lesson.artifact_id == "les-200"
        assert lesson.title == "Understanding Fractions"

    def test_learner_scope_content_summary_dataclass(self):
        summary = LearnerScopeContentSummary(
            scope_id="grade4_mathematics_en",
            diagnostic_items_count=40,
            lessons_count=20,
            total_artifacts_count=60,
            last_promotion_at="2026-08-28T00:00:00Z",
        )
        assert summary.scope_id == "grade4_mathematics_en"
        assert summary.total_artifacts_count == 60

    def test_learner_read_modes(self):
        assert LearnerReadMode.PRODUCTION_ONLY == "production_only"
        assert LearnerReadMode.PRODUCTION_WITH_LEGACY_FALLBACK == "production_with_legacy_fallback"
        assert LearnerReadMode.LEGACY_ONLY == "legacy_only"

    def test_content_learner_read_service_init(self):
        service = ContentLearnerReadService()
        assert service is not None
