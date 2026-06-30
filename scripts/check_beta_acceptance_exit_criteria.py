#!/usr/bin/env python3
"""Validate beta acceptance exit criteria."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_acceptance_exit_criteria.md"

REQUIRED_SNIPPETS = (
    "Beta Acceptance Exit Criteria",
    "Cluster H release readiness check is green",
    "final Cluster H closeout rollup check is green",
    "beta feedback intake contract is present",
    "beta known issues register is present",
    "beta monitoring and incident trigger matrix is present",
    "beta participant support handoff checklist is present",
    "beta release communications plan is present",
    "beta release decision log is updated",
    "final beta operator packet is complete",
    "release audit trail index is complete",
    "no unresolved blocker known issue may remain for acceptance",
    "privacy and consent issues require POPIA owner disposition",
    "AI safety issues require AI safety owner disposition",
    "learner data access issues require technical and privacy disposition",
    "rollback outcome must reference beta rollback runbook",
    "defer outcome must include owner, reason, and target milestone",
    "reject outcome must identify failed evidence or missing approval",
    "accept outcome must reference release candidate and commit SHA",
    "accept controlled beta outcome",
    "reject controlled beta outcome",
    "defer controlled beta outcome",
    "rollback controlled beta outcome",
    "does not approve production launch, execute deployment, create release tags, or override unresolved blocker issues",
    "make beta-acceptance-exit-criteria-check",
)


@dataclass(frozen=True)
class BetaAcceptanceExitCriteriaResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaAcceptanceExitCriteriaResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaAcceptanceExitCriteriaResult(DOC.exists(), "criteria present" if DOC.exists() else "criteria missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaAcceptanceExitCriteriaResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta acceptance exit criteria check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
