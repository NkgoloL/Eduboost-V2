"""Comprehensive unit tests for LessonFileQualityResult data model and ContentFileLessonQualityService methods."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.content_file_lesson_quality import (
    ContentFileLessonQualityService,
    LessonFileQualityResult,
)


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


class TestContentFileLessonQualityServiceBranches:
    def test_audit_scope_missing_path_and_missing_file(self, tmp_path: Path):
        mock_registry = MagicMock()
        mock_validator = MagicMock()

        service = ContentFileLessonQualityService(
            project_root=tmp_path,
            registry=mock_registry,
            validator=mock_validator,
        )

        # 1. Lessons path missing from artifact_paths
        mock_registry.get_scope.return_value = SimpleNamespace(
            scope_id="term_1_maths",
            artifact_paths={},
        )
        res_no_path = service.audit_scope("term_1_maths")
        assert res_no_path.exists is False
        assert res_no_path.quarantined is True
        assert "not configured" in res_no_path.blockers[0]

        # 2. Lessons file missing on disk
        mock_registry.get_scope.return_value = SimpleNamespace(
            scope_id="term_1_maths",
            artifact_paths={"lessons": "data/missing.json"},
        )
        res_missing = service.audit_scope("term_1_maths")
        assert res_missing.exists is False
        assert res_missing.quarantined is True
        assert "is missing" in res_missing.blockers[0]

    def test_audit_scope_failed_validation_and_write_manifests(self, tmp_path: Path):
        mock_registry = MagicMock()
        mock_validator = MagicMock()

        service = ContentFileLessonQualityService(
            project_root=tmp_path,
            registry=mock_registry,
            validator=mock_validator,
        )

        # Create dummy lesson file
        lesson_path = tmp_path / "data" / "lessons.json"
        lesson_path.parent.mkdir(parents=True, exist_ok=True)
        lesson_path.write_text(json.dumps({"lessons": [{"id": 1}]}), encoding="utf-8")

        mock_registry.get_scope.return_value = SimpleNamespace(
            scope_id="term_1_maths",
            subject_code="MATH",
            subject="Mathematics",
            source_documents=["doc-1"],
            artifact_paths={"lessons": "data/lessons.json"},
        )
        mock_registry.list_scopes.return_value = [mock_registry.get_scope.return_value]

        mock_validator.validate_file_payload.return_value = SimpleNamespace(
            passed=False,
            lesson_count=10,
            failed_lesson_count=3,
            aggregate={"fk_exceeded": 3},
            issues=[
                SimpleNamespace(
                    lesson_id="les-1",
                    caps_ref="4.M.1.1",
                    field="reading_level",
                    reason="Grade level too high",
                )
            ],
        )

        # audit_scope
        res = service.audit_scope("term_1_maths")
        assert res.exists is True
        assert res.passed is False
        assert res.quarantined is True
        assert res.failed_lesson_count == 3
        assert len(res.issues) == 1
        assert "Lesson layer failed quality audit" in res.blockers[0]

        # write_manifests
        output_dir = tmp_path / "manifests"
        summary = service.write_manifests(output_dir=output_dir)
        assert summary["summary"]["scope_count"] == 1
        assert summary["summary"]["lesson_layers_quarantined"] == 1

        scope_file = output_dir / "term_1_maths_lesson_quality.json"
        assert scope_file.exists()
        summary_file = output_dir / "all_scopes_lesson_quality_summary.json"
        assert summary_file.exists()
