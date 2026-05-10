#!/usr/bin/env python3
"""Validate beta governance seal checklist."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_governance_seal_checklist.md"

REQUIRED_SNIPPETS = (
    "Beta Governance Seal Checklist",
    "Cluster H release readiness check is green",
    "Cluster H terminal closure assertion is present",
    "beta release final index is present",
    "post-beta evidence archive manifest is present",
    "beta outcome report template is present",
    "beta retrospective action register is present",
    "beta acceptance exit criteria are present",
    "final beta operator packet index is present",
    "release audit trail index is present",
    "release owner accountability matrix is present",
    "beta release decision log is present",
    "Release owner",
    "Technical approver",
    "Privacy/POPIA approver",
    "AI safety owner",
    "Data resilience owner",
    "Frontend owner",
    "Support owner",
    "seal cannot be recorded while Cluster H release readiness check is failing",
    "seal cannot override unresolved blocker issues",
    "seal cannot bypass release owner accountability",
    "seal cannot replace manual approval workflow evidence",
    "seal must reference release candidate and commit SHA",
    "seal must reference post-beta evidence archive manifest",
    "does not approve production launch, execute deployment, create release tags, or override unresolved blocker issues",
    "make beta-governance-seal-check",
)


@dataclass(frozen=True)
class BetaGovernanceSealResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaGovernanceSealResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [BetaGovernanceSealResult(DOC.exists(), "checklist present" if DOC.exists() else "checklist missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(BetaGovernanceSealResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))
    return results


def main() -> int:
    results = run_checks()
    print("Beta governance seal check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
