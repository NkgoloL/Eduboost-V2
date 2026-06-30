#!/usr/bin/env python3
"""Validate post-merge release handoff checklist."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "post_merge_release_handoff_checklist.md"

REQUIRED_SNIPPETS = (
    "Post-Merge Release Handoff Checklist",
    "merged commit SHA recorded",
    "release state snapshot generated after merge",
    "final PR merge readiness check passed before merge",
    "final release verification bundle passed before merge",
    "beta release evidence bundle linked",
    "Cluster H closure report linked",
    "rollback runbook linked",
    "post-deploy staging smoke checklist linked",
    "release candidate tag manifest linked",
    "manual approval workflow location documented",
    "release operator",
    "technical approver",
    "privacy/POPIA approver",
    "rollback owner",
    "post-deploy verification owner",
    "incident contact",
    "verify remote default branch contains merged commit",
    "regenerate release state snapshot from merged branch",
    "confirm beta sign-off manifest still references intended commit",
    "confirm release candidate tag has not been pushed before approval",
    "record approval outcome in beta release decision log",
    "Post-merge handoff does not execute deployment, tagging, approval, or production launch",
    "make post-merge-release-handoff-check",
)


@dataclass(frozen=True)
class PostMergeReleaseHandoffResult:
    ok: bool
    detail: str


def run_checks() -> list[PostMergeReleaseHandoffResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        PostMergeReleaseHandoffResult(DOC.exists(), "checklist present" if DOC.exists() else "checklist missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PostMergeReleaseHandoffResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Post-merge release handoff check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
