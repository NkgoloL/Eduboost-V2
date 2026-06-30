#!/usr/bin/env python3
"""Validate release owner post-closeout decision record."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_owner_post_closeout_decision_record.md"

REQUIRED_SNIPPETS = (
    "Release Owner Post-Closeout Decision Record",
    "final project closeout attestation",
    "final merge signoff lock",
    "release owner execution guardrail",
    "final release handoff package",
    "evidence archive completeness guard",
    "post-terminal audit readiness assertion",
    "beta outcome report template",
    "beta retrospective action register",
    "beta release decision log",
    "release owner accountability matrix",
    "Decision ID",
    "Release Candidate",
    "Commit SHA",
    "Decision Owner",
    "Decision Time UTC",
    "merge / defer / reject / request changes",
    "Reason",
    "Follow-Up Owner",
    "Evidence Archive Location",
    "decision must reference release candidate and commit SHA",
    "merge decision requires Cluster H release readiness check is green",
    "defer decision must include reason, owner, and target milestone",
    "reject decision must identify failed evidence or unresolved blocker",
    "request changes decision must identify owner and evidence gap",
    "decision must preserve beta release decision log references",
    "decision must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or override manual approval",
    "make release-owner-post-closeout-decision-record-check",
)


@dataclass(frozen=True)
class ReleaseOwnerPostCloseoutDecisionRecordResult:
    ok: bool
    detail: str


def run_checks() -> list[ReleaseOwnerPostCloseoutDecisionRecordResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [ReleaseOwnerPostCloseoutDecisionRecordResult(DOC.exists(), "record present" if DOC.exists() else "record missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseOwnerPostCloseoutDecisionRecordResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Release owner post-closeout decision record check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
