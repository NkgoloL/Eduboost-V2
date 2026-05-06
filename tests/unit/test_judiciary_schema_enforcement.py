from __future__ import annotations

import pytest

from app.core.judiciary import ConstitutionalViolation, JudiciaryService


def test_invalid_json_is_wrapped_as_constitutional_violation() -> None:
    service = JudiciaryService()

    with pytest.raises(ConstitutionalViolation):
        service.stamp_lesson("not-json")


def test_valid_json_is_validated_without_jsondecodeerror() -> None:
    service = JudiciaryService()
    payload = service.stamp_lesson(
        """
        {
          "title": "Fractions",
          "introduction": "Intro",
          "main_content": "Main",
          "worked_example": "Example",
          "practice_question": "Question",
          "answer": "Answer",
          "cultural_hook": "Braai maths"
        }
        """
    )

    assert payload.title == "Fractions"

