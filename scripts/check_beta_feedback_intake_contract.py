#!/usr/bin/env python3
"""Validate beta feedback intake contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_feedback_intake_contract.md"

REQUIRED_SNIPPETS = (
    "Beta Feedback Intake Contract",
    "Feedback ID",
    "Reporter Role",
    "learner / parent / operator / support / approver",
    "Submitted At UTC",
    "Release Candidate",
    "Commit SHA",
    "learner / parent / AI safety / consent / privacy / performance / support",
    "low / medium / high / blocker",
    "Evidence Link",
    "open / triaged / accepted / deferred / closed",
    "blocker feedback must be linked to beta monitoring and incident trigger matrix",
    "privacy feedback must be routed to POPIA process owner",
    "AI safety feedback must be linked to AI safety evidence owner",
    "access-boundary feedback must be escalated to technical approver and privacy/POPIA approver",
    "support feedback must reference beta participant support handoff checklist",
    "accepted feedback must reference a follow-up owner and status",
    "deferred feedback must record reason and target milestone",
    "docs/operations/beta_monitoring_incident_trigger_matrix.md",
    "docs/operations/beta_participant_support_handoff_checklist.md",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/ai/CLUSTER_F_CLOSURE.md",
    "docs/operations/beta_release_decision_log.md",
    "does not collect live participant data, approve release, execute deployment, or create product commitments",
    "make beta-feedback-intake-contract-check",
)


@dataclass(frozen=True)
class BetaFeedbackIntakeContractResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaFeedbackIntakeContractResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaFeedbackIntakeContractResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaFeedbackIntakeContractResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta feedback intake contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
