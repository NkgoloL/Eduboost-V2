#!/usr/bin/env python3
"""Validate beta known issues register."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_known_issues_register.md"

REQUIRED_SNIPPETS = (
    "Beta Known Issues Register",
    "Issue ID",
    "feedback / smoke / monitoring / support / approval",
    "Release Candidate",
    "Commit SHA",
    "low / medium / high / blocker",
    "learner / parent / consent / privacy / AI safety / deployment / data resilience",
    "accepted risk / fix required / deferred / closed",
    "Mitigation",
    "Evidence Link",
    "blocker known issue blocks beta acceptance until resolved or release is rejected",
    "privacy known issue requires POPIA owner review",
    "consent known issue requires consent boundary review",
    "AI safety known issue requires AI safety evidence owner review",
    "data resilience known issue requires backup or restore evidence review",
    "support known issue must link to participant support handoff",
    "accepted risk must record approver and mitigation",
    "deferred issue must record target milestone and owner",
    "docs/operations/beta_feedback_intake_contract.md",
    "docs/operations/beta_monitoring_incident_trigger_matrix.md",
    "docs/operations/beta_participant_support_handoff_checklist.md",
    "docs/operations/beta_release_decision_log.md",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/ai/CLUSTER_F_CLOSURE.md",
    "docs/operations/data_resilience_evidence_index.md",
    "does not accept risk automatically, approve release, execute remediation, or override incident triggers",
    "make beta-known-issues-register-check",
)


@dataclass(frozen=True)
class BetaKnownIssuesRegisterResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaKnownIssuesRegisterResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaKnownIssuesRegisterResult(DOC.exists(), "register present" if DOC.exists() else "register missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaKnownIssuesRegisterResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta known issues register check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
