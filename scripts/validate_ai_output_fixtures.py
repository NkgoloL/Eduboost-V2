#!/usr/bin/env python3
"""Validate fixture-based AI output schemas and safety envelopes."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "ai"

FIXTURES = (
    "safe_lesson_output.json",
    "safe_diagnostic_output.json",
    "refusal_output.json",
)

COMMON_FIELDS = (
    "type",
    "grade",
    "subject",
    "topic",
    "caps_alignment_reference",
    "safety_status",
    "learner_facing_content",
    "remediation_target",
    "trace_id",
)


@dataclass(frozen=True)
class FixtureValidationResult:
    fixture: str
    ok: bool
    detail: str


def _load_fixture(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # pragma: no cover - defensive CLI path
        return None, str(exc)


def _validate_common(fixture: str, data: dict[str, Any]) -> list[FixtureValidationResult]:
    results: list[FixtureValidationResult] = []
    for field in COMMON_FIELDS:
        results.append(
            FixtureValidationResult(
                fixture,
                field in data,
                f"contains field {field!r}" if field in data else f"missing field {field!r}",
            )
        )

    results.append(
        FixtureValidationResult(
            fixture,
            data.get("safety_status") in {"safe", "refused"},
            "safety_status is safe/refused" if data.get("safety_status") in {"safe", "refused"} else "invalid safety_status",
        )
    )

    content = data.get("learner_facing_content")
    results.append(
        FixtureValidationResult(
            fixture,
            isinstance(content, dict),
            "learner_facing_content is object" if isinstance(content, dict) else "learner_facing_content is not object",
        )
    )
    return results


def _validate_lesson(fixture: str, data: dict[str, Any]) -> list[FixtureValidationResult]:
    content = data.get("learner_facing_content") or {}
    required = ("title", "learning_objective", "explanation", "worked_example", "practice_activity")
    return [
        FixtureValidationResult(
            fixture,
            key in content,
            f"lesson contains {key!r}" if key in content else f"lesson missing {key!r}",
        )
        for key in required
    ]


def _validate_diagnostic(fixture: str, data: dict[str, Any]) -> list[FixtureValidationResult]:
    content = data.get("learner_facing_content") or {}
    required = ("item_stem", "answer_options", "correct_answer", "explanation", "diagnostic_objective", "difficulty_band")
    results = [
        FixtureValidationResult(
            fixture,
            key in content,
            f"diagnostic contains {key!r}" if key in content else f"diagnostic missing {key!r}",
        )
        for key in required
    ]
    results.append(
        FixtureValidationResult(
            fixture,
            isinstance(content.get("answer_options"), list) and len(content.get("answer_options", [])) >= 2,
            "diagnostic has answer options" if isinstance(content.get("answer_options"), list) and len(content.get("answer_options", [])) >= 2 else "diagnostic answer options invalid",
        )
    )
    return results


def _validate_refusal(fixture: str, data: dict[str, Any]) -> list[FixtureValidationResult]:
    content = data.get("learner_facing_content") or {}
    required = ("refusal_reason", "safe_educational_redirection", "no_unsafe_operational_detail", "no_hidden_prompt_disclosure")
    results = [
        FixtureValidationResult(
            fixture,
            key in content,
            f"refusal contains {key!r}" if key in content else f"refusal missing {key!r}",
        )
        for key in required
    ]
    results.append(
        FixtureValidationResult(
            fixture,
            content.get("no_unsafe_operational_detail") is True and content.get("no_hidden_prompt_disclosure") is True,
            "refusal suppresses unsafe detail and hidden prompts"
            if content.get("no_unsafe_operational_detail") is True and content.get("no_hidden_prompt_disclosure") is True
            else "refusal safety booleans invalid",
        )
    )
    return results


def validate_fixture(path: Path) -> list[FixtureValidationResult]:
    data, error = _load_fixture(path)
    if data is None:
        return [FixtureValidationResult(path.name, False, f"invalid json: {error}")]

    results = _validate_common(path.name, data)
    output_type = data.get("type")

    if output_type == "lesson":
        results.extend(_validate_lesson(path.name, data))
    elif output_type == "diagnostic":
        results.extend(_validate_diagnostic(path.name, data))
    elif output_type == "refusal":
        results.extend(_validate_refusal(path.name, data))
    else:
        results.append(FixtureValidationResult(path.name, False, f"unsupported type {output_type!r}"))

    return results


def run_checks() -> list[FixtureValidationResult]:
    results: list[FixtureValidationResult] = []
    for fixture in FIXTURES:
        path = FIXTURE_DIR / fixture
        if not path.exists():
            results.append(FixtureValidationResult(fixture, False, "fixture missing"))
            continue
        results.extend(validate_fixture(path))
    return results


def main() -> int:
    results = run_checks()
    print("AI output fixture validation")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.fixture}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
