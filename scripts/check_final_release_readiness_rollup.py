#!/usr/bin/env python3
"""Validate final release readiness rollup."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_release_readiness_rollup.md"

REQUIRED_SNIPPETS = (
    "Final Release Readiness Rollup",
    "final release evidence table of contents",
    "final reviewer pack checklist",
    "merge-control evidence gate",
    "release evidence retention finalization",
    "final acceptance packet index",
    "PR-ready final closure certificate",
    "archival lock assertion",
    "final release evidence ledger",
    "final evidence no-op execution assertion",
    "post-closeout evidence access policy",
    "Rollup ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Readiness Outcome",
    "Reviewer",
    "Reviewed At UTC",
    "Evidence Archive Location",
    "rollup must reference release candidate and commit SHA",
    "rollup must preserve controlled staging/beta scope",
    "rollup must preserve final reviewer pack references",
    "rollup must preserve merge-control evidence gate references",
    "rollup must preserve no-op execution boundary references",
    "rollup must preserve retention finalization references",
    "rollup must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make final-release-readiness-rollup-check",
)


@dataclass(frozen=True)
class FinalReleaseReadinessRollupResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalReleaseReadinessRollupResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalReleaseReadinessRollupResult(DOC.exists(), "rollup present" if DOC.exists() else "rollup missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalReleaseReadinessRollupResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final release readiness rollup check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
