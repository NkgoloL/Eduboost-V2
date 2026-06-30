#!/usr/bin/env python3
"""Validate beta outcome report template."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_outcome_report_template.md"

REQUIRED_SNIPPETS = (
    "Beta Outcome Report Template",
    "Report ID",
    "Release Candidate",
    "Commit SHA",
    "accepted / rejected / deferred / rolled back",
    "Decision Owner",
    "Decision Time UTC",
    "Evidence Reviewer",
    "Support Summary Owner",
    "Known Issues Summary",
    "Follow-Up Owner",
    "beta acceptance exit criteria",
    "beta release decision log",
    "beta known issues register",
    "beta feedback intake contract",
    "beta monitoring and incident trigger matrix",
    "beta participant support handoff checklist",
    "final beta operator packet index",
    "release audit trail index",
    "accepted outcome must reference release candidate and commit SHA",
    "rejected outcome must reference failed evidence or missing approval",
    "deferred outcome must include reason, owner, and target milestone",
    "rolled back outcome must reference rollback runbook and decision log entry",
    "support summary must avoid unnecessary learner personal information",
    "unresolved blocker issues must prevent accepted outcome",
    "privacy or consent issues must include POPIA owner disposition",
    "AI safety issues must include AI safety owner disposition",
    "does not approve production launch, execute deployment, create release tags, or close follow-up work automatically",
    "make beta-outcome-report-template-check",
)


@dataclass(frozen=True)
class BetaOutcomeReportTemplateResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaOutcomeReportTemplateResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaOutcomeReportTemplateResult(DOC.exists(), "template present" if DOC.exists() else "template missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaOutcomeReportTemplateResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta outcome report template check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
