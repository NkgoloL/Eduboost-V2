#!/usr/bin/env python3
"""Validate CAPS alignment evidence contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "caps_alignment_contract.md"

REQUIRED_SNIPPETS = (
    "CAPS Alignment Contract",
    "grade",
    "subject",
    "topic",
    "CAPS strand or skill",
    "learner mastery state",
    "diagnostic objective",
    "remediation objective",
    "generated lessons must reference learner grade and subject",
    "generated diagnostics must be objective-bound",
    "model fallback must preserve CAPS-aligned prompts",
)


@dataclass(frozen=True)
class CapsAlignmentResult:
    ok: bool
    detail: str


def run_checks() -> list[CapsAlignmentResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [CapsAlignmentResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            CapsAlignmentResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("CAPS alignment contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
