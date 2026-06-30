#!/usr/bin/env python3
"""Validate frontend accessibility contract evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "frontend" / "frontend_accessibility_contract.md"

REQUIRED_SNIPPETS = (
    "Frontend Accessibility Contract",
    "every interactive control has an accessible name",
    "forms expose visible labels or ARIA labels",
    "keyboard navigation reaches primary learner and parent actions",
    "focus indicators are visible",
    "error messages are announced or associated with fields",
    "status/loading states are understandable without color alone",
    "consent and authorization denial states use plain-language copy",
    "learner-facing copy remains age-appropriate",
    "parent trust and progress surfaces avoid data overexposure",
    "learner onboarding",
    "diagnostic start and submit",
    "parent dashboard",
    "authorization and consent denial states",
    "make frontend-accessibility-contract-check",
)


@dataclass(frozen=True)
class AccessibilityContractResult:
    ok: bool
    detail: str


def run_checks() -> list[AccessibilityContractResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        AccessibilityContractResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            AccessibilityContractResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend accessibility contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
