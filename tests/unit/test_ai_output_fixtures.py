from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "ai"


@pytest.mark.unit
@pytest.mark.parametrize(
    "fixture_name",
    [
        "safe_lesson_output.json",
        "safe_diagnostic_output.json",
        "refusal_output.json",
    ],
)
def test_ai_output_fixtures_are_valid_json(fixture_name: str) -> None:
    data = json.loads((FIXTURE_DIR / fixture_name).read_text(encoding="utf-8"))

    assert data["grade"] == 8
    assert data["subject"]
    assert data["topic"]
    assert data["caps_alignment_reference"]
    assert data["safety_status"] in {"safe", "refused"}
    assert data["trace_id"]


@pytest.mark.unit
def test_safe_lesson_fixture_has_lesson_shape() -> None:
    data = json.loads((FIXTURE_DIR / "safe_lesson_output.json").read_text(encoding="utf-8"))
    content = data["learner_facing_content"]

    assert data["type"] == "lesson"
    assert "learning_objective" in content
    assert "worked_example" in content
    assert "practice_activity" in content


@pytest.mark.unit
def test_safe_diagnostic_fixture_has_diagnostic_shape() -> None:
    data = json.loads((FIXTURE_DIR / "safe_diagnostic_output.json").read_text(encoding="utf-8"))
    content = data["learner_facing_content"]

    assert data["type"] == "diagnostic"
    assert "item_stem" in content
    assert "answer_options" in content
    assert "correct_answer" in content
    assert "diagnostic_objective" in content


@pytest.mark.unit
def test_refusal_fixture_has_safe_redirection_shape() -> None:
    data = json.loads((FIXTURE_DIR / "refusal_output.json").read_text(encoding="utf-8"))
    content = data["learner_facing_content"]

    assert data["type"] == "refusal"
    assert content["no_unsafe_operational_detail"] is True
    assert content["no_hidden_prompt_disclosure"] is True
    assert "safe_educational_redirection" in content
