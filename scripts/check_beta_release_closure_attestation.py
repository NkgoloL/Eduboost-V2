#!/usr/bin/env python3
"""Validate beta release closure attestation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_release_closure_attestation.md"

REQUIRED_SNIPPETS = (
    "Beta Release Closure Attestation",
    "Cluster H release readiness evidence is present",
    "Cluster H closure evidence is present",
    "final release verification bundle is present",
    "release audit trail index is present",
    "beta evidence consistency guard is present",
    "final PR merge readiness contract is present",
    "post-merge release handoff checklist is present",
    "release owner accountability matrix is present",
    "beta release decision log is present",
    "generated artifact hygiene contract is present",
    "Reviewer",
    "Review Date UTC",
    "Release Candidate",
    "Commit SHA",
    "Attestation Outcome",
    "does not grant release approval, execute deployment, create release tags, or authorize production launch",
    "make beta-release-closure-attestation-check",
)


@dataclass(frozen=True)
class BetaReleaseClosureAttestationResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaReleaseClosureAttestationResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaReleaseClosureAttestationResult(DOC.exists(), "attestation present" if DOC.exists() else "attestation missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaReleaseClosureAttestationResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta release closure attestation check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
