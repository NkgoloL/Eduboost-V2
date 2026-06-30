#!/usr/bin/env python3
"""Validate beta release decision log."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_release_decision_log.md"

REQUIRED_SNIPPETS = (
    "Beta Release Decision Log",
    "Decision ID",
    "Decision Type",
    "approve / reject / rollback / defer",
    "Release Candidate",
    "Commit SHA",
    "Decision Owner",
    "Decision Time UTC",
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/release_state_snapshot.md",
    "docs/operations/final_release_verification_bundle.md",
    "docs/operations/beta_rollback_runbook.md",
    "docs/operations/post_deploy_staging_smoke_checklist.md",
    "approval decision must reference the release candidate and commit SHA",
    "rejection decision must record the failed check or missing approval",
    "rollback decision must reference the rollback runbook",
    "defer decision must record the owner and next action",
    "post-deploy verification outcome must be recorded after deployment",
    "decision log does not replace platform workflow logs",
    "does not approve release automatically",
    "does not execute deployment or rollback",
    "make beta-release-decision-log-check",
)


@dataclass(frozen=True)
class BetaReleaseDecisionLogResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaReleaseDecisionLogResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaReleaseDecisionLogResult(DOC.exists(), "decision log present" if DOC.exists() else "decision log missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaReleaseDecisionLogResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta release decision log check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
