"""Comprehensive unit tests for LessonFileQualityResult data model and result structures."""
from __future__ import annotations

import pytest

from app.services.content_file_lesson_quality import LessonFileQualityResult


class TestContentFileLessonQuality:
    def test_lesson_file_quality_result_dataclass(self):
        res = LessonFileQualityResult(
            scope_id="grade4_mathematics_en",
            relative_path="data/lessons.json",
            exists=True,
            passed=True,
            lesson_count=20,
            failed_lesson_count=0,
            quarantined=False,
            blockers=[],
            aggregate={"passed": 20},
            issues=[],
        )
        assert res.scope_id == "grade4_mathematics_en"
        assert res.passed is True
        assert res.lesson_count == 20
        assert res.quarantined is False

    def test_lesson_file_quality_result_quarantined_state(self):
        res = LessonFileQualityResult(
            scope_id="grade4_mathematics_en",
            relative_path="data/missing.json",
            exists=False,
            passed=False,
            lesson_count=0,
            failed_lesson_count=0,
            quarantined=True,
            blockers=["File is missing"],
            aggregate={},
            issues=[{"type": "missing_file", "message": "File not found"}],
        )
        assert res.passed is False
        assert res.quarantined is True
        assert len(res.blockers) == 1
        assert len(res.issues) == 1
