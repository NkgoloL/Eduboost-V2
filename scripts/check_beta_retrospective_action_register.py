#!/usr/bin/env python3
"""Validate beta retrospective action register."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_retrospective_action_register.md"

REQUIRED_SNIPPETS = (
    "Beta Retrospective Action Register",
    "Action ID",
    "outcome report / feedback / known issue / support / monitoring / approval",
    "Release Candidate",
    "Commit SHA",
    "bug / documentation / compliance / safety / operations / support",
    "low / medium / high / blocker",
    "Target Milestone",
    "Evidence Link",
    "open / in progress / done / deferred",
    "every high or blocker action must have an owner and target milestone",
    "compliance action must reference POPIA or consent evidence owner",
    "safety action must reference AI safety evidence owner",
    "operational action must reference release owner accountability matrix",
    "support action must reference participant support handoff checklist",
    "deferred action must record reason and next review date",
    "done action must reference evidence or pull request",
    "unresolved blocker action prevents accepted beta outcome",
    "docs/operations/beta_outcome_report_template.md",
    "docs/operations/beta_feedback_intake_contract.md",
    "docs/operations/beta_known_issues_register.md",
    "docs/operations/beta_participant_support_handoff_checklist.md",
    "docs/operations/release_owner_accountability_matrix.md",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/ai/CLUSTER_F_CLOSURE.md",
    "does not create tickets automatically, approve release, execute remediation, or close actions without evidence",
    "make beta-retrospective-action-register-check",
)


@dataclass(frozen=True)
class BetaRetrospectiveActionRegisterResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaRetrospectiveActionRegisterResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaRetrospectiveActionRegisterResult(DOC.exists(), "register present" if DOC.exists() else "register missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaRetrospectiveActionRegisterResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta retrospective action register check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
