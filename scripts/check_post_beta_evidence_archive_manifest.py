#!/usr/bin/env python3
"""Validate post-beta evidence archive manifest."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "post_beta_evidence_archive_manifest.md"

REQUIRED_SNIPPETS = (
    "Post-Beta Evidence Archive Manifest",
    "Release Identity",
    "Release Decision",
    "Feedback and Issue Evidence",
    "Operations and Support Evidence",
    "Audit Evidence",
    "docs/operations/release_state_snapshot.md",
    "docs/operations/release_candidate_tag_manifest.md",
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/beta_release_decision_log.md",
    "docs/operations/beta_acceptance_exit_criteria.md",
    "docs/operations/beta_outcome_report_template.md",
    "docs/operations/beta_feedback_intake_contract.md",
    "docs/operations/beta_known_issues_register.md",
    "docs/operations/beta_retrospective_action_register.md",
    "docs/operations/final_beta_operator_packet_index.md",
    "docs/operations/beta_participant_support_handoff_checklist.md",
    "docs/operations/beta_release_communications_plan.md",
    "docs/operations/beta_monitoring_incident_trigger_matrix.md",
    "docs/operations/release_audit_trail_index.md",
    "docs/operations/final_cluster_h_closeout_rollup.md",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "archive must reference release candidate and commit SHA",
    "archive must preserve accepted, rejected, deferred, or rolled back outcome",
    "archive must preserve feedback and known issue summaries",
    "archive must preserve unresolved follow-up ownership",
    "archive must preserve support and incident trigger references",
    "archive must not include unnecessary learner personal information",
    "archive must remain audit evidence, not production launch authorization",
    "does not approve release, execute deployment, create release tags, or replace source control history",
    "make post-beta-evidence-archive-manifest-check",
)


@dataclass(frozen=True)
class PostBetaEvidenceArchiveManifestResult:
    ok: bool
    detail: str


def run_checks() -> list[PostBetaEvidenceArchiveManifestResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        PostBetaEvidenceArchiveManifestResult(DOC.exists(), "manifest present" if DOC.exists() else "manifest missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PostBetaEvidenceArchiveManifestResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Post-beta evidence archive manifest check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
