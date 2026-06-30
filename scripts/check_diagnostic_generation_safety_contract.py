#!/usr/bin/env python3
"""Validate diagnostic generation safety evidence contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "diagnostic_generation_safety_contract.md"

REQUIRED_SNIPPETS = (
    "Diagnostic Generation Safety Contract",
    "learner grade",
    "CAPS strand or skill",
    "diagnostic objective",
    "difficulty band",
    "item count",
    "consent-authorized learner identifier",
    "questions must be age-appropriate",
    "questions must avoid unsafe instructions",
    "questions must not include sexual content",
    "questions must not include self-harm content",
    "questions must not expose another learner's data",
    "every item must map to the diagnostic objective",
    "answer keys must be present",
    "make diagnostic-generation-safety-check",
)


@dataclass(frozen=True)
class DiagnosticSafetyResult:
    ok: bool
    detail: str


def run_checks() -> list[DiagnosticSafetyResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [DiagnosticSafetyResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            DiagnosticSafetyResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Diagnostic generation safety contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
