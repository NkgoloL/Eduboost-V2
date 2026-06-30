from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from app.services.content_generation.generated_item_contract import GeneratedItemQualityValidator
from app.services.content_generation.generated_lesson_contract import GeneratedLessonQualityValidator
from app.services.content_generation.scope_lesson_generator import ScopeLessonGenerator
from app.services.content_generation.topic_map_source_context import TopicMapSourceContextBuilder
from app.services.content_file_lesson_quality import ContentFileLessonQualityService, LessonFileQualityResult
from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService
from scripts.curriculum.build_scope_content_artifacts import build_scope_content_artifacts

pytestmark = pytest.mark.unit
REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "generated_lessons"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_valid_fixture_passes_generated_lesson_quality_validator() -> None:
    validator = GeneratedLessonQualityValidator()
    lesson = _load("valid_scope_lesson.json")

    issues = validator.validate_lesson(
        lesson,
        scope_id="grade5_mathematics_en",
        subject_code="M",
        subject="Mathematics",
        source_document_ids=["caps_intermediate_phase_mathematics_grade4_6"],
    )

    assert issues == []


@pytest.mark.parametrize(
    "fixture_name",
    [
        "invalid_placeholder_lesson.json",
        "invalid_missing_fields_lesson.json",
        "invalid_all_option_a_lesson.json",
    ],
)
def test_invalid_fixtures_fail_generated_lesson_quality_validator(fixture_name: str) -> None:
    validator = GeneratedLessonQualityValidator()
    lesson = _load(fixture_name)

    issues = validator.validate_lesson(
        lesson,
        scope_id="grade5_mathematics_en",
        subject_code="M",
        subject="Mathematics",
        source_document_ids=["caps_intermediate_phase_mathematics_grade4_6"],
    )

    assert issues
    assert all(issue.lesson_id for issue in issues)
    assert all(issue.caps_ref for issue in issues)
    assert all(issue.field for issue in issues)


def test_scope_builder_generates_lessons_that_pass_quality_audit(tmp_path: Path) -> None:
    report = build_scope_content_artifacts("grade5_mathematics_en", output_root=tmp_path, write=True)
    lesson_path = tmp_path / report["output_files"]["lessons"]
    payload = json.loads(lesson_path.read_text(encoding="utf-8"))
    validator = GeneratedLessonQualityValidator()

    for lesson in payload["lessons"]:
        issues = validator.validate_lesson(
            lesson,
            scope_id="grade5_mathematics_en",
            subject_code="M",
            subject="Mathematics",
            source_document_ids=["caps_intermediate_phase_mathematics_grade4_6"],
        )
        assert not issues, issues


def test_scope_builder_generates_items_that_pass_quality_audit(tmp_path: Path) -> None:
    report = build_scope_content_artifacts("grade5_mathematics_en", output_root=tmp_path, write=True)
    item_path = tmp_path / report["output_files"]["diagnostic_items"]
    payload = json.loads(item_path.read_text(encoding="utf-8"))
    result = GeneratedItemQualityValidator().validate_file_payload(payload)

    assert result.passed, result.issues[:5]
    assert payload["items"]
    assert all(item.get("source") == "scope_item_generator_v2" for item in payload["items"][:5])
    assert all("What should you do first" not in item.get("stem", "") for item in payload["items"])


def test_regenerated_grade6_lessons_pass_quality_audit() -> None:
    service = ContentFileLessonQualityService(project_root=REPO_ROOT)
    result = service.audit_scope("grade6_mathematics_en")

    assert result.exists is True
    assert result.quarantined is False
    assert result.failed_lesson_count == 0


def test_regenerated_grade5_lessons_pass_quality_audit() -> None:
    service = ContentFileLessonQualityService(project_root=REPO_ROOT)
    result = service.audit_scope("grade5_mathematics_en")

    assert result.exists is True
    assert result.quarantined is False
    assert result.failed_lesson_count == 0


def test_promotion_readiness_blocks_staging_when_lessons_quarantined() -> None:
    lesson_quality = Mock()
    lesson_quality.audit_scope.return_value = LessonFileQualityResult(
        scope_id="grade6_mathematics_en",
        relative_path="data/generated/lessons/grade6_mathematics_en_lessons.json",
        exists=True,
        passed=False,
        lesson_count=128,
        failed_lesson_count=128,
        quarantined=True,
        blockers=["Lesson layer failed quality audit: 128/128 lessons invalid."],
        aggregate={},
        issues=[],
    )
    service = ContentFilePromotionReadinessService(
        project_root=REPO_ROOT,
        lesson_quality_service=lesson_quality,
    )
    result = service.evaluate_scope("grade6_mathematics_en")

    assert result.staging_eligible is False
    assert any("quality audit" in blocker for blocker in result.blockers)


def test_scope_builder_records_source_context_hash(tmp_path: Path) -> None:
    report = build_scope_content_artifacts("grade5_mathematics_en", output_root=tmp_path, write=True)
    run_manifest = json.loads((tmp_path / report["output_files"]["run_manifest"]).read_text(encoding="utf-8"))
    assert report["source_context_hashes"]
    assert run_manifest["source_context_hashes"]


def test_topic_map_source_context_builder_refuses_thin_context(tmp_path: Path) -> None:
    builder = TopicMapSourceContextBuilder(project_root=tmp_path)
    topic_map_path = tmp_path / "topic.json"
    topic_map_path.write_text(
        json.dumps(
            {
                "_meta": {"source_document_ids": []},
                "grade": 5,
                "subject": "Mathematics",
                "subject_code": "M",
                "terms": [],
            }
        ),
        encoding="utf-8",
    )
    result = builder.build(
        scope_id="grade5_mathematics_en",
        caps_ref="5.M.1.1",
        topic_context={"grade": 5, "subject": "Mathematics", "subject_code": "M", "topic": "Numbers", "subtopic": "Numbers", "term": 1},
        topic_map_path=str(topic_map_path.relative_to(tmp_path)),
        source_document_ids=[],
    )

    assert result.passed is False
    assert result.errors


def test_scope_lesson_generator_varies_correct_options() -> None:
    builder = TopicMapSourceContextBuilder(project_root=REPO_ROOT)
    generator = ScopeLessonGenerator()
    context = builder.build(
        scope_id="grade5_mathematics_en",
        caps_ref="5.M.1.1",
        topic_context={
            "grade": 5,
            "subject": "Mathematics",
            "subject_code": "M",
            "topic": "Numbers, operations and relationships",
            "subtopic": "Numbers, operations and relationships",
            "term": 1,
            "weeks": "1-10",
            "assessment_standards": [
                "Solve grade-appropriate problems involving numbers, operations and relationships.",
                "Use mathematical language, representations and strategies accurately.",
            ],
            "common_misconceptions": ["topic_vocabulary_confusion"],
        },
        topic_map_path="data/caps/topic_maps/grade5_mathematics_en.json",
        source_document_ids=["caps_intermediate_phase_mathematics_grade4_6"],
        phase="intermediate",
        language="en",
    ).context
    assert context is not None
    lessons = [generator.generate(context, index=index) for index in range(8)]
    correct_sets = {tuple(q["correct_option"] for q in lesson["practice_questions"]) for lesson in lessons}
    assert len(correct_sets) > 1
