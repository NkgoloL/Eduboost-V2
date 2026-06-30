#!/usr/bin/env python3
"""Validate PR closeout evidence checklist."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "pr_closeout_evidence_checklist.md"

REQUIRED_SNIPPETS = (
    "PR Closeout Evidence Checklist",
    "final commit includes source, docs, workflow, and test evidence",
    "generated local artifacts are excluded",
    "branch is synchronized with remote",
    "release readiness checks are green",
    "Cluster H closure check is green",
    "PR integration summary is updated",
    "project status is updated",
    "final verification command list is included in PR body",
    "known non-goals and beta boundaries are documented",
    "rollback and post-deploy owners are documented",
    "make generated-artifact-hygiene-check",
    "make branch-sync-rebase-checklist-check",
    "make cluster-h-release-readiness-check",
    "make cluster-h-closure-check",
    "Evidence Index",
    "Known Follow-Ups",
    "make pr-closeout-evidence-checklist-check",
)


@dataclass(frozen=True)
class PRCloseoutEvidenceChecklistResult:
    ok: bool
    detail: str


def run_checks() -> list[PRCloseoutEvidenceChecklistResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        PRCloseoutEvidenceChecklistResult(DOC.exists(), "checklist present" if DOC.exists() else "checklist missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            PRCloseoutEvidenceChecklistResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("PR closeout evidence checklist check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
