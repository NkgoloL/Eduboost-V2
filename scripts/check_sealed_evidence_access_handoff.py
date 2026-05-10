#!/usr/bin/env python3
"""Validate sealed evidence access handoff."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "sealed_evidence_access_handoff.md"

REQUIRED_SNIPPETS = (
    "Sealed Evidence Access Handoff",
    "terminal review index",
    "final release operator brief",
    "terminal evidence seal",
    "final PR handoff summary",
    "post-closeout evidence access policy",
    "release evidence retention finalization",
    "final release evidence ledger",
    "final release evidence table of contents",
    "branch handoff proof record",
    "final closure manifest",
    "Access Handoff ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Access Owner",
    "Receiving Reviewer",
    "Handoff Time UTC",
    "Access Outcome",
    "access handoff must reference release candidate and commit SHA",
    "access handoff must reference branch and PR number",
    "access handoff must preserve post-closeout evidence access policy references",
    "access handoff must preserve terminal review index references",
    "access handoff must preserve sealed evidence references",
    "access handoff must avoid unnecessary learner personal information",
    "access handoff must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make sealed-evidence-access-handoff-check",
)


@dataclass(frozen=True)
class SealedEvidenceAccessHandoffResult:
    ok: bool
    detail: str


def run_checks() -> list[SealedEvidenceAccessHandoffResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [SealedEvidenceAccessHandoffResult(DOC.exists(), "handoff present" if DOC.exists() else "handoff missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            SealedEvidenceAccessHandoffResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Sealed evidence access handoff check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
