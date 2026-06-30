from __future__ import annotations

from app.services.content_generation.lesson_generator import LessonGenerator
from app.services.content_generation.prompt_payloads import GeneratedLesson


def _lesson(**kwargs):
    data = {
        "title": "Lesson",
        "summary": "Summary",
        "learning_objectives": ["Objective"],
        "teacher_notes": "Notes",
        "learner_activity": "Activity",
        "worked_examples": ["Example"],
        "practice_questions": ["Question"],
        "answer_key": ["Answer"],
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "subject_code": "MAT",
        "language": "en",
        "source_chunk_ids": ["chunk-1"],
    }
    data.update(kwargs)
    return GeneratedLesson(**data)


def test_lesson_generator_accepts_schema_valid_lesson() -> None:
    assert LessonGenerator().validate(_lesson(), caps_ref="4.M.1.1") == []


def test_lesson_without_answer_key_fails_validation() -> None:
    errors = LessonGenerator().validate(_lesson(answer_key=[]), caps_ref="4.M.1.1")

    assert any("answer key" in error for error in errors)


def test_lesson_without_objectives_fails_validation() -> None:
    errors = LessonGenerator().validate(_lesson(learning_objectives=[]), caps_ref="4.M.1.1")

    assert any("objectives" in error for error in errors)


def test_lesson_caps_ref_mismatch_fails_validation() -> None:
    errors = LessonGenerator().validate(_lesson(caps_ref="5.M.2.1"), caps_ref="4.M.1.1")

    assert any("does not match task caps_ref" in error for error in errors)


def test_lesson_without_source_citations_fails_validation() -> None:
    errors = LessonGenerator().validate(_lesson(source_chunk_ids=[]), caps_ref="4.M.1.1")

    assert any("source citations" in error for error in errors)


def test_lesson_grade_below_zero_fails_validation() -> None:
    errors = LessonGenerator().validate(_lesson(grade=-1), caps_ref="4.M.1.1")

    assert any("grade must be age appropriate" in error for error in errors)


def test_lesson_grade_above_twelve_fails_validation() -> None:
    errors = LessonGenerator().validate(_lesson(grade=13), caps_ref="4.M.1.1")

    assert any("grade must be age appropriate" in error for error in errors)


def test_lesson_duplicate_hash_fails_validation() -> None:
    errors = LessonGenerator().validate(
        _lesson(),
        caps_ref="4.M.1.1",
        existing_hashes={"hash-123"},
        artifact_hash="hash-123"
    )

    assert any("duplicates an existing artifact hash" in error for error in errors)


def test_lesson_duplicate_hash_passes_when_no_existing_hashes() -> None:
    errors = LessonGenerator().validate(
        _lesson(),
        caps_ref="4.M.1.1",
        existing_hashes=None,
        artifact_hash="hash-123"
    )

    assert errors == []


def test_lesson_duplicate_hash_passes_when_hash_not_in_existing() -> None:
    errors = LessonGenerator().validate(
        _lesson(),
        caps_ref="4.M.1.1",
        existing_hashes={"hash-456"},
        artifact_hash="hash-123"
    )

    assert errors == []


def test_lesson_without_practice_questions_passes_validation() -> None:
    errors = LessonGenerator().validate(_lesson(practice_questions=[]), caps_ref="4.M.1.1")

    assert errors == []


def test_lesson_with_multiple_errors_returns_all_errors() -> None:
    errors = LessonGenerator().validate(
        _lesson(
            learning_objectives=[],
            answer_key=[],
            caps_ref="5.M.2.1",
            source_chunk_ids=[],
            grade=-1
        ),
        caps_ref="4.M.1.1"
    )

    assert len(errors) > 1
    assert any("objectives" in error for error in errors)
    assert any("answer key" in error for error in errors)
    assert any("caps_ref" in error for error in errors)
    assert any("source citations" in error for error in errors)
    assert any("grade" in error for error in errors)
