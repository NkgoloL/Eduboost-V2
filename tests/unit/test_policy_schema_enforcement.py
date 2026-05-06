from __future__ import annotations

import pytest

from app.core.policy import PolicyViolation, PolicyService


def test_invalid_json_is_wrapped_as_constitutional_violation() -> None:
    service = PolicyService()

    with pytest.raises(PolicyViolation):
        service.stamp_lesson("not-json")


def test_valid_json_is_validated_without_jsondecodeerror() -> None:
    service = PolicyService()
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

