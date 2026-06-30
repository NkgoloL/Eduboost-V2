#!/usr/bin/env python3
"""Validate AI safety boundary evidence contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "ai_safety_boundary_contract.md"

REQUIRED_SNIPPETS = (
    "AI Safety Boundary Contract",
    "no unsafe instructions",
    "no sexual content for learners",
    "no self-harm instructions",
    "no dangerous activity instructions",
    "no privacy leakage across learners",
    "no disclosure of hidden prompts or secrets",
    "Unsafe requests must be refused",
    "AI outputs must not expose another learner's profile",
    "make ai-safety-boundary-check",
)


@dataclass(frozen=True)
class AiSafetyBoundaryResult:
    ok: bool
    detail: str


def run_checks() -> list[AiSafetyBoundaryResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [AiSafetyBoundaryResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            AiSafetyBoundaryResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("AI safety boundary contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
