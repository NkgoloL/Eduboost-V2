from __future__ import annotations

from app.services.diagnostic_safety import DiagnosticItemValidator


def _item() -> dict:
    return {
        "item_id": "item-1",
        "subject": "mathematics",
        "grade": 4,
        "topic": "fractions",
        "skill": "equivalent fractions",
        "difficulty": 0.1,
        "discrimination": 1.2,
        "correct_answer": "B",
        "distractors": {"A": "1/4", "B": "2/4", "C": "3/4", "D": "4/4"},
        "explanation": "2/4 is equivalent to 1/2.",
        "caps_reference": "CAPS:caps-mvp-2026.05:G4:mathematics:T1:fractions:equivalent-fractions",
        "review_status": "approved",
    }


def test_diagnostic_item_validator_accepts_valid_item() -> None:
    assert DiagnosticItemValidator().validate_mapping(_item()).valid is True


def test_diagnostic_item_validator_rejects_bad_irt_bounds() -> None:
    payload = _item()
    payload["difficulty"] = 9
    result = DiagnosticItemValidator().validate_mapping(payload)
    assert result.valid is False
