#!/usr/bin/env python3
"""Validate beta participant support handoff checklist."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_participant_support_handoff_checklist.md"

REQUIRED_SNIPPETS = (
    "Beta Participant Support Handoff Checklist",
    "beta support contact",
    "incident contact",
    "privacy/POPIA approver",
    "technical approver",
    "post-deploy verification owner",
    "rollback owner",
    "beta boundary and non-production scope",
    "known issues and follow-ups",
    "support intake channel",
    "escalation channel",
    "privacy request escalation path",
    "data deletion request escalation path",
    "AI safety issue escalation path",
    "rollback status contact",
    "release decision log location",
    "support must not promise production availability",
    "support must not request unnecessary learner personal information",
    "privacy requests must be routed to POPIA process owner",
    "suspected access-boundary incidents must be escalated immediately",
    "AI safety issues must be linked to AI safety evidence owner",
    "support outcomes must be summarized after beta validation",
    "docs/operations/beta_release_decision_log.md",
    "docs/operations/beta_monitoring_incident_trigger_matrix.md",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/ai/CLUSTER_F_CLOSURE.md",
    "docs/operations/beta_rollback_runbook.md",
    "does not invite beta participants, approve release, execute deployment, or collect participant data",
    "make beta-participant-support-handoff-check",
)


@dataclass(frozen=True)
class BetaParticipantSupportHandoffResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaParticipantSupportHandoffResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaParticipantSupportHandoffResult(DOC.exists(), "checklist present" if DOC.exists() else "checklist missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaParticipantSupportHandoffResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta participant support handoff check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
