#!/usr/bin/env python3
"""Validate final release operator brief."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_release_operator_brief.md"

REQUIRED_SNIPPETS = (
    "Final Release Operator Brief",
    "terminal evidence seal",
    "final PR handoff summary",
    "final reviewer disposition record",
    "final closure manifest",
    "branch handoff proof record",
    "final acceptance memo",
    "release record closure ledger",
    "PR merge evidence summary",
    "merge-control evidence gate",
    "post-closeout evidence access policy",
    "Brief ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Operator",
    "Brief Time UTC",
    "Brief Outcome",
    "Evidence Archive Location",
    "brief must reference release candidate and commit SHA",
    "brief must reference branch and PR number",
    "brief must preserve terminal evidence seal references",
    "brief must preserve final PR handoff summary references",
    "brief must preserve merge-control evidence gate references",
    "brief must preserve no-op execution boundary references",
    "brief must preserve post-closeout evidence access policy references",
    "brief must remain controlled staging/beta evidence",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make final-release-operator-brief-check",
)


@dataclass(frozen=True)
class FinalReleaseOperatorBriefResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalReleaseOperatorBriefResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalReleaseOperatorBriefResult(DOC.exists(), "brief present" if DOC.exists() else "brief missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalReleaseOperatorBriefResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final release operator brief check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
