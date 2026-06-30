#!/usr/bin/env python3
"""Validate evidence archive completeness guard."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "evidence_archive_completeness_guard.md"

REQUIRED_SNIPPETS = (
    "Evidence Archive Completeness Guard",
    "release identity evidence",
    "governance seal evidence",
    "terminal closure assertion evidence",
    "release final index evidence",
    "post-beta archive manifest evidence",
    "outcome report evidence",
    "known issues evidence",
    "feedback intake evidence",
    "retrospective action evidence",
    "support handoff evidence",
    "monitoring trigger evidence",
    "operator packet evidence",
    "docs/operations/release_state_snapshot.md",
    "docs/operations/beta_governance_seal_checklist.md",
    "docs/operations/cluster_h_terminal_closure_assertion.md",
    "docs/operations/beta_release_final_index.md",
    "docs/operations/post_beta_evidence_archive_manifest.md",
    "docs/operations/beta_outcome_report_template.md",
    "docs/operations/beta_known_issues_register.md",
    "docs/operations/beta_feedback_intake_contract.md",
    "docs/operations/beta_retrospective_action_register.md",
    "docs/operations/beta_participant_support_handoff_checklist.md",
    "docs/operations/beta_monitoring_incident_trigger_matrix.md",
    "docs/operations/final_beta_operator_packet_index.md",
    "archive completeness must reference release candidate and commit SHA",
    "archive completeness must preserve decision, outcome, feedback, and follow-up evidence",
    "archive completeness must preserve operational handoff and support references",
    "archive completeness must preserve governance and terminal closure references",
    "archive completeness must not include unnecessary learner personal information",
    "archive completeness must remain audit evidence only",
    "does not approve production launch, execute deployment, create release tags, or replace source control history",
    "make evidence-archive-completeness-guard-check",
)


@dataclass(frozen=True)
class EvidenceArchiveCompletenessGuardResult:
    ok: bool
    detail: str


def run_checks() -> list[EvidenceArchiveCompletenessGuardResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [EvidenceArchiveCompletenessGuardResult(DOC.exists(), "guard present" if DOC.exists() else "guard missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(EvidenceArchiveCompletenessGuardResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))
    return results


def main() -> int:
    results = run_checks()
    print("Evidence archive completeness guard check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
