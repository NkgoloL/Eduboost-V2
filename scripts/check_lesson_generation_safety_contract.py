#!/usr/bin/env python3
"""Validate lesson generation safety evidence contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "lesson_generation_safety_contract.md"

REQUIRED_SNIPPETS = (
    "Lesson Generation Safety Contract",
    "learner grade",
    "CAPS strand or skill",
    "learner mastery state",
    "lesson objective",
    "consent-authorized learner identifier",
    "safety boundary instructions",
    "lesson content must be age-appropriate",
    "lesson content must avoid unsafe instructions",
    "lesson content must not include sexual content",
    "lesson content must not include self-harm content",
    "lesson content must not expose another learner's data",
    "every lesson must map to a lesson objective",
    "worked examples must match the grade and subject",
    "practice activities must map to the learner gap",
    "make lesson-generation-safety-check",
)


@dataclass(frozen=True)
class LessonSafetyResult:
    ok: bool
    detail: str


def run_checks() -> list[LessonSafetyResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [LessonSafetyResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            LessonSafetyResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Lesson generation safety contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
