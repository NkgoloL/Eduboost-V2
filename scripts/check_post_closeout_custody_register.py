#!/usr/bin/env python3
"""Validate post-closeout custody register."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "post_closeout_custody_register.md"

REQUIRED_SNIPPETS = (
    "Post-Closeout Custody Register",
    "final archive accession record",
    "final sealed package manifest",
    "audit review closeout certificate",
    "terminal handoff closure note",
    "sealed evidence access handoff",
    "post-closeout evidence access policy",
    "release evidence retention finalization",
    "final release evidence ledger",
    "final release evidence table of contents",
    "cluster h release evidence checksum index",
    "Custody Register ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Custodian",
    "Custody Time UTC",
    "Custody Outcome",
    "Evidence Archive Location",
    "custody register must reference release candidate and commit SHA",
    "custody register must reference branch and PR number",
    "custody register must preserve final archive accession record references",
    "custody register must preserve post-closeout evidence access policy references",
    "custody register must preserve retention finalization references",
    "custody register must preserve checksum and ledger references",
    "custody register must avoid unnecessary learner personal information",
    "custody register must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make post-closeout-custody-register-check",
)


@dataclass(frozen=True)
class PostCloseoutCustodyRegisterResult:
    ok: bool
    detail: str


def run_checks() -> list[PostCloseoutCustodyRegisterResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [PostCloseoutCustodyRegisterResult(DOC.exists(), "register present" if DOC.exists() else "register missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PostCloseoutCustodyRegisterResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Post-closeout custody register check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
