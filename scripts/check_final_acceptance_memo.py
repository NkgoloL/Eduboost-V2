#!/usr/bin/env python3
"""Validate final acceptance memo."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_acceptance_memo.md"

REQUIRED_SNIPPETS = (
    "Final Acceptance Memo",
    "final release readiness rollup",
    "evidence freeze confirmation record",
    "PR merge evidence summary",
    "final reviewer pack checklist",
    "merge-control evidence gate",
    "release evidence retention finalization",
    "final release evidence table of contents",
    "PR-ready final closure certificate",
    "archival lock assertion",
    "final acceptance packet index",
    "Memo ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Acceptance Summary",
    "Reviewer",
    "Memo Time UTC",
    "Evidence Archive Location",
    "memo must reference release candidate and commit SHA",
    "memo must reference branch and PR number",
    "memo must preserve final release readiness rollup references",
    "memo must preserve evidence freeze confirmation record references",
    "memo must preserve PR merge evidence summary references",
    "memo must preserve no-op execution boundary references",
    "memo must preserve controlled staging/beta scope",
    "memo must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make final-acceptance-memo-check",
)


@dataclass(frozen=True)
class FinalAcceptanceMemoResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalAcceptanceMemoResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalAcceptanceMemoResult(DOC.exists(), "memo present" if DOC.exists() else "memo missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalAcceptanceMemoResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final acceptance memo check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
