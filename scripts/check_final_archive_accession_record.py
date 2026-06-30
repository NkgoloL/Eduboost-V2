#!/usr/bin/env python3
"""Validate final archive accession record."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_archive_accession_record.md"

REQUIRED_SNIPPETS = (
    "Final Archive Accession Record",
    "final sealed package manifest",
    "audit review closeout certificate",
    "terminal handoff closure note",
    "sealed reviewer closeout packet",
    "final audit handoff register",
    "terminal PR evidence index",
    "terminal evidence seal",
    "release evidence retention finalization",
    "post-closeout evidence access policy",
    "cluster h release evidence checksum index",
    "Accession ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Archive Owner",
    "Accession Time UTC",
    "Accession Outcome",
    "Evidence Archive Location",
    "accession must reference release candidate and commit SHA",
    "accession must reference branch and PR number",
    "accession must preserve final sealed package manifest references",
    "accession must preserve audit review closeout certificate references",
    "accession must preserve terminal handoff closure note references",
    "accession must preserve checksum and ledger references",
    "accession must avoid unnecessary learner personal information",
    "accession must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make final-archive-accession-record-check",
)


@dataclass(frozen=True)
class FinalArchiveAccessionRecordResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalArchiveAccessionRecordResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalArchiveAccessionRecordResult(DOC.exists(), "record present" if DOC.exists() else "record missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalArchiveAccessionRecordResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final archive accession record check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
