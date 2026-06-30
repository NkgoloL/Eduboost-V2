#!/usr/bin/env python3
"""Validate final project closeout attestation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_project_closeout_attestation.md"

REQUIRED_SNIPPETS = (
    "Final Project Closeout Attestation",
    "Cluster H terminal closure assertion is present",
    "beta governance seal checklist is present",
    "beta release final index is present",
    "final release handoff package is present",
    "evidence archive completeness guard is present",
    "post-terminal audit readiness assertion is present",
    "release owner execution guardrail is present",
    "post-beta evidence archive manifest is present",
    "project release closure index is present",
    "PR integration summary is updated",
    "project status is updated",
    "Attestation ID",
    "Release Candidate",
    "Commit SHA",
    "Attesting Owner",
    "Attestation Time UTC",
    "Evidence Archive Location",
    "Closeout Outcome",
    "Outstanding Follow-Up Owner",
    "closeout must reference release candidate and commit SHA",
    "closeout must reference Cluster H terminal closure assertion",
    "closeout must reference final release handoff package",
    "closeout must preserve unresolved follow-up ownership",
    "closeout must remain controlled staging/beta evidence",
    "closeout must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or replace manual approval",
    "make final-project-closeout-attestation-check",
)


@dataclass(frozen=True)
class FinalProjectCloseoutAttestationResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalProjectCloseoutAttestationResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalProjectCloseoutAttestationResult(DOC.exists(), "attestation present" if DOC.exists() else "attestation missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalProjectCloseoutAttestationResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final project closeout attestation check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
