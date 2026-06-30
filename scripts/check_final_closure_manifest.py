#!/usr/bin/env python3
"""Validate final closure manifest."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_closure_manifest.md"

REQUIRED_SNIPPETS = (
    "Final Closure Manifest",
    "final acceptance memo",
    "release record closure ledger",
    "post-merge evidence continuity note",
    "final release readiness rollup",
    "evidence freeze confirmation record",
    "PR merge evidence summary",
    "final reviewer pack checklist",
    "merge-control evidence gate",
    "release evidence retention finalization",
    "final release evidence table of contents",
    "Manifest ID",
    "Release Candidate",
    "Commit SHA",
    "Branch",
    "PR Number",
    "Manifest Owner",
    "Manifest Time UTC",
    "Manifest Outcome",
    "Evidence Archive Location",
    "manifest must reference release candidate and commit SHA",
    "manifest must reference branch and PR number",
    "manifest must preserve final acceptance memo references",
    "manifest must preserve release record closure ledger references",
    "manifest must preserve post-merge evidence continuity note references",
    "manifest must preserve controlled staging/beta scope",
    "manifest must preserve no-op execution boundary",
    "manifest must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make final-closure-manifest-check",
)


@dataclass(frozen=True)
class FinalClosureManifestResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalClosureManifestResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalClosureManifestResult(DOC.exists(), "manifest present" if DOC.exists() else "manifest missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalClosureManifestResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final closure manifest check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
