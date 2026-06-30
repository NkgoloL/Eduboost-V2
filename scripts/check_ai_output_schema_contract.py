#!/usr/bin/env python3
"""Validate AI output schema/safety envelope contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "ai_output_schema_contract.md"

REQUIRED_SNIPPETS = (
    "AI Output Schema Contract",
    "CAPS alignment reference",
    "safety status",
    "learner-facing content",
    "generated-at timestamp or trace identifier",
    "learning objective",
    "worked example",
    "practice activity",
    "item stem",
    "answer options",
    "correct answer",
    "diagnostic objective",
    "difficulty band",
    "refusal reason",
    "safe educational redirection",
    "no hidden prompt disclosure",
    "make ai-output-schema-contract-check",
)


@dataclass(frozen=True)
class AiOutputSchemaResult:
    ok: bool
    detail: str


def run_checks() -> list[AiOutputSchemaResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [AiOutputSchemaResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            AiOutputSchemaResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("AI output schema contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
