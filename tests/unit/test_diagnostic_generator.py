from __future__ import annotations

from app.services.content_generation.diagnostic_generator import DiagnosticGenerator
from app.services.content_generation.prompt_payloads import GeneratedDiagnosticItem


def _item(**kwargs):
    data = {
        "question_text": "Question?",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "Because source says so.",
        "caps_ref": "4.M.1.1",
        "grade": 4,
        "subject_code": "MAT",
        "language": "en",
        "source_chunk_ids": ["chunk-1"],
    }
    data.update(kwargs)
    return GeneratedDiagnosticItem(**data)


def test_diagnostic_generator_accepts_schema_valid_item() -> None:
    assert DiagnosticGenerator().validate(_item(), caps_ref="4.M.1.1") == []


def test_diagnostic_without_answer_key_fails_validation() -> None:
    errors = DiagnosticGenerator().validate(_item(correct_answer=""), caps_ref="4.M.1.1")

    assert any("answer key" in error for error in errors)


def test_diagnostic_duplicate_hash_fails_validation() -> None:
    errors = DiagnosticGenerator().validate(_item(), caps_ref="4.M.1.1", existing_hashes={"hash"}, artifact_hash="hash")

    assert any("duplicates" in error for error in errors)
