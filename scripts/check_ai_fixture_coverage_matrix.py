#!/usr/bin/env python3
"""Validate AI fixture coverage matrix."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "ai_fixture_coverage_matrix.md"

REQUIRED_FIXTURES = (
    "tests/fixtures/ai/safe_lesson_output.json",
    "tests/fixtures/ai/safe_diagnostic_output.json",
    "tests/fixtures/ai/refusal_output.json",
    "tests/fixtures/ai/refusals/unsafe_instruction_refusal.json",
    "tests/fixtures/ai/refusals/privacy_leakage_refusal.json",
    "tests/fixtures/ai/refusals/hidden_prompt_refusal.json",
)

REQUIRED_SNIPPETS = (
    "AI Fixture Coverage Matrix",
    "safe lesson output has objective",
    "safe diagnostic output has answer key",
    "refusal output has safe educational redirection",
    "refusal suppresses unsafe operational detail",
    "refusal protects another learner's data",
    "refusal does not disclose hidden prompts",
    "make ai-fixture-coverage-check",
)


@dataclass(frozen=True)
class FixtureCoverageResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[FixtureCoverageResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        FixtureCoverageResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "matrix present" if DOC.exists() else "matrix missing")
    ]

    for fixture in REQUIRED_FIXTURES:
        results.append(
            FixtureCoverageResult(
                fixture,
                (REPO_ROOT / fixture).exists(),
                "fixture present" if (REPO_ROOT / fixture).exists() else "fixture missing",
            )
        )
        results.append(
            FixtureCoverageResult(
                str(DOC.relative_to(REPO_ROOT)),
                fixture in text,
                f"matrix references {fixture}" if fixture in text else f"matrix missing {fixture}",
            )
        )

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FixtureCoverageResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("AI fixture coverage matrix check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
