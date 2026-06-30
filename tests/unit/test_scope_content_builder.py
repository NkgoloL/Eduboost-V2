from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.modules.diagnostics.item_validator import ItemValidator
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService
from app.modules.lessons.lesson_validator import LessonValidator
from app.services.content_generation.generated_lesson_contract import GeneratedLessonQualityValidator
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.build_scope_content_artifacts import build_scope_content_artifacts
from scripts.validate_item_bank import coverage_summary


pytestmark = pytest.mark.unit
REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_generic_scope_builder_generates_valid_launch_slice(tmp_path: Path) -> None:
    report = build_scope_content_artifacts("grade4_mathematics_en", output_root=tmp_path, write=True)

    assert report["scope_id"] == "grade4_mathematics_en"
    assert report["item_counts"] == {"4.M.1.1": 40, "4.M.1.2": 40, "4.M.1.3": 40}
    assert report["lesson_counts"] == {"4.M.1.1": 8, "4.M.1.2": 8, "4.M.1.3": 8}
    assert report["blueprint_count"] == 10
    assert report["study_plan_counts"]["topic_sequence"] == 3
    assert report["validation"] == {
        "items": [],
        "lessons": [],
        "blueprints": [],
        "study_plans": [],
    }

    registry = ContentScopeRegistry()
    scope = registry.get_scope("grade4_mathematics_en")
    topic_map_path = REPO_ROOT / scope.topic_map_path
    topic_map = _load_json(topic_map_path)
    item_validator = ItemValidator(topic_map=topic_map)
    lesson_validator = LessonValidator(caps_service=CAPSTopicMapService(map_paths=[topic_map_path]))

    item_path = tmp_path / report["output_files"]["diagnostic_items"]
    lesson_path = tmp_path / report["output_files"]["lessons"]
    blueprint_path = tmp_path / report["output_files"]["assessment_blueprints"]
    study_plan_path = tmp_path / report["output_files"]["study_plan_templates"]
    run_manifest_path = tmp_path / report["output_files"]["run_manifest"]

    assert item_path.exists()
    assert lesson_path.exists()
    assert blueprint_path.exists()
    assert study_plan_path.exists()
    assert run_manifest_path.exists()

    item_payload = _load_json(item_path)
    lesson_payload = _load_json(lesson_path)
    blueprint_payload = _load_json(blueprint_path)
    study_plan_payload = _load_json(study_plan_path)

    assert len(item_payload["items"]) == 120
    assert len(lesson_payload["lessons"]) == 24
    assert len(blueprint_payload["blueprints"]) == 10
    assert len(study_plan_payload["topic_sequence"]) == 3
    assert len(study_plan_payload["remediation_mappings"]) >= 3
    assert len(study_plan_payload["extension_mappings"]) == 3

    for item in item_payload["items"]:
        assert not item_validator.validate_all(item)
        assert item["review_status"] == "approved"

    for lesson in lesson_payload["lessons"]:
        validation = lesson_validator.validate(lesson, require_verified=True)
        assert validation.passed, validation.failures
        quality_issues = GeneratedLessonQualityValidator().validate_lesson(
            lesson,
            scope_id=report["scope_id"],
            subject_code=scope.subject_code,
            subject=scope.subject,
            source_document_ids=list(scope.source_documents or []),
        )
        assert not quality_issues, quality_issues
        assert lesson["review_status"] == "approved"


def test_generic_scope_builder_generates_valid_review_scope(tmp_path: Path) -> None:
    report = build_scope_content_artifacts("grade5_mathematics_en", output_root=tmp_path, write=True)

    assert report["scope_id"] == "grade5_mathematics_en"
    assert report["generation_ready"] is True
    assert len(report["item_counts"]) == 16
    assert len(report["lesson_counts"]) == 16
    assert set(report["validation"]) == {"items", "lessons", "blueprints", "study_plans"}
    assert not any(report["validation"].values())
    for output_file in report["output_files"].values():
        assert (tmp_path / output_file).exists()


def test_scope_aware_item_bank_coverage_uses_registry_targets() -> None:
    registry = ContentScopeRegistry()
    seed = _load_json(REPO_ROOT / "data/generated/items/grade4_maths_launch_item_bank.json")

    coverage = coverage_summary(seed["items"], scope_id="grade4_mathematics_en", registry=registry)

    assert set(coverage) == {"4.M.1.1", "4.M.1.2", "4.M.1.3"}
    assert coverage["4.M.1.1"]["target"] == 40
    assert coverage["4.M.1.1"]["met"] is True


def test_all_generation_ready_scopes_have_generated_artifact_layers() -> None:
    registry = ContentScopeRegistry()
    expected_layers = {
        "diagnostic_items",
        "lessons",
        "assessment_blueprints",
        "study_plan_templates",
    }

    for scope in registry.list_scopes():
        assert expected_layers <= set(scope.artifact_paths), scope.scope_id
        for layer in expected_layers:
            artifact_path = REPO_ROOT / scope.artifact_paths[layer]
            assert artifact_path.exists(), f"{scope.scope_id} missing {layer}: {artifact_path}"
