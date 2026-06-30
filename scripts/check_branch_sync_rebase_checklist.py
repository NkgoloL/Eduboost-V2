#!/usr/bin/env python3
"""Validate branch sync and rebase checklist."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "branch_sync_rebase_checklist.md"

REQUIRED_SNIPPETS = (
    "Branch Sync and Rebase Checklist",
    "git status --short",
    "git fetch origin",
    "git rebase origin/<current-branch>",
    "resolve source, docs, workflow, and test conflicts intentionally",
    "remove generated `coverage.xml` conflicts with `git rm -f coverage.xml`",
    "do not carry local caches into the release commit",
    "do not force-push unless the branch owner has explicitly approved it",
    "rerun Cluster H readiness checks after rebase",
    "make generated-artifact-hygiene-check",
    "make cluster-h-release-readiness-check",
    "make cluster-h-closure-check",
    "repeat fetch/rebase rather than defaulting to force-push",
    "make branch-sync-rebase-checklist-check",
)


@dataclass(frozen=True)
class BranchSyncRebaseChecklistResult:
    ok: bool
    detail: str


def run_checks() -> list[BranchSyncRebaseChecklistResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BranchSyncRebaseChecklistResult(DOC.exists(), "checklist present" if DOC.exists() else "checklist missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BranchSyncRebaseChecklistResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Branch sync and rebase checklist check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
