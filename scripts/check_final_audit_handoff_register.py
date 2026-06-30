#!/usr/bin/env python3
"""Validate final audit handoff register."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_audit_handoff_register.md"

REQUIRED_SNIPPETS = (
    "Final Audit Handoff Register",
    "sealed reviewer closeout packet",
    "final release operator brief",
    "terminal review index",
    "sealed evidence access handoff",
    "terminal evidence seal",
    "release evidence retention finalization",
    "post-closeout evidence access policy",
    "final release evidence ledger",
    "final release evidence table of contents",
    "cluster h release evidence checksum index",
    "Audit Handoff ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Audit Owner",
    "Receiving Auditor",
    "Handoff Time UTC",
    "Handoff Outcome",
    "audit handoff must reference release candidate and commit SHA",
    "audit handoff must reference branch and PR number",
    "audit handoff must preserve sealed reviewer closeout packet references",
    "audit handoff must preserve sealed evidence access handoff references",
    "audit handoff must preserve retention finalization references",
    "audit handoff must preserve checksum and ledger references",
    "audit handoff must avoid unnecessary learner personal information",
    "audit handoff must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make final-audit-handoff-register-check",
)


@dataclass(frozen=True)
class FinalAuditHandoffRegisterResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalAuditHandoffRegisterResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalAuditHandoffRegisterResult(DOC.exists(), "register present" if DOC.exists() else "register missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalAuditHandoffRegisterResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final audit handoff register check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
