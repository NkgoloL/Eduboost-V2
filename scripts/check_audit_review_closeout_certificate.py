#!/usr/bin/env python3
"""Validate audit review closeout certificate."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "audit_review_closeout_certificate.md"

REQUIRED_SNIPPETS = (
    "Audit Review Closeout Certificate",
    "final sealed package manifest",
    "sealed reviewer closeout packet",
    "final audit handoff register",
    "terminal PR evidence index",
    "sealed evidence access handoff",
    "release evidence retention finalization",
    "final release evidence ledger",
    "cluster h release evidence checksum index",
    "post-closeout evidence access policy",
    "terminal evidence seal",
    "Audit Certificate ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Audit Reviewer",
    "Certificate Time UTC",
    "Audit Outcome",
    "Evidence Archive Location",
    "audit closeout must reference release candidate and commit SHA",
    "audit closeout must reference branch and PR number",
    "audit closeout must preserve final sealed package manifest references",
    "audit closeout must preserve final audit handoff register references",
    "audit closeout must preserve retention finalization references",
    "audit closeout must preserve checksum and ledger references",
    "audit closeout must avoid unnecessary learner personal information",
    "audit closeout must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make audit-review-closeout-certificate-check",
)


@dataclass(frozen=True)
class AuditReviewCloseoutCertificateResult:
    ok: bool
    detail: str


def run_checks() -> list[AuditReviewCloseoutCertificateResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [AuditReviewCloseoutCertificateResult(DOC.exists(), "certificate present" if DOC.exists() else "certificate missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            AuditReviewCloseoutCertificateResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Audit review closeout certificate check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
