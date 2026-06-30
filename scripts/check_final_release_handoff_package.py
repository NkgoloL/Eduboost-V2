#!/usr/bin/env python3
"""Validate final release handoff package."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_release_handoff_package.md"

REQUIRED_SNIPPETS = (
    "Final Release Handoff Package",
    "docs/operations/cluster_h_terminal_closure_assertion.md",
    "docs/operations/beta_release_final_index.md",
    "docs/operations/beta_governance_seal_checklist.md",
    "docs/operations/post_beta_evidence_archive_manifest.md",
    "docs/operations/beta_outcome_report_template.md",
    "docs/operations/beta_retrospective_action_register.md",
    "docs/operations/beta_acceptance_exit_criteria.md",
    "docs/operations/final_beta_operator_packet_index.md",
    "docs/operations/release_owner_accountability_matrix.md",
    "docs/operations/beta_release_decision_log.md",
    "Handoff ID",
    "Release Candidate",
    "Commit SHA",
    "Handoff Owner",
    "Receiving Owner",
    "Handoff Time UTC",
    "Evidence Archive Location",
    "Outstanding Follow-Up Owner",
    "Handoff Outcome",
    "handoff must reference release candidate and commit SHA",
    "handoff must reference terminal closure assertion",
    "handoff must reference final beta release index",
    "handoff must preserve unresolved follow-up ownership",
    "handoff must preserve beta outcome and decision log references",
    "handoff must not bypass manual approval workflow evidence",
    "handoff must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or close unresolved follow-up work",
    "make final-release-handoff-package-check",
)


@dataclass(frozen=True)
class FinalReleaseHandoffPackageResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalReleaseHandoffPackageResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalReleaseHandoffPackageResult(DOC.exists(), "package present" if DOC.exists() else "package missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(FinalReleaseHandoffPackageResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))
    return results


def main() -> int:
    results = run_checks()
    print("Final release handoff package check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
