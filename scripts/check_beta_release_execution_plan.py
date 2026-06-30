#!/usr/bin/env python3
"""Validate beta release execution plan."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_release_execution_plan.md"

REQUIRED_SNIPPETS = (
    "Beta Release Execution Plan",
    "branch sync and rebase checklist passes",
    "generated artifact hygiene check passes",
    "beta release final checklist passes",
    "project release closure index check passes",
    "Cluster H release readiness check passes",
    "Cluster H closure check passes",
    "rollback owner is assigned",
    "post-deploy verification owner is assigned",
    "Confirm clean working tree",
    "Fetch and rebase on the remote branch",
    "Regenerate staging smoke evidence",
    "Regenerate beta sign-off manifest",
    "Regenerate beta release evidence bundle",
    "Regenerate release candidate tag manifest",
    "Run final release verification bundle",
    "Update PR body with generated evidence summary",
    "Request manual approval",
    "create release candidate tag",
    "Run post-deploy staging smoke checklist",
    "unresolved merge conflict",
    "generated artifact conflict such as `coverage.xml`",
    "manual approval not recorded",
    "make beta-release-execution-plan-check",
)


@dataclass(frozen=True)
class BetaReleaseExecutionPlanResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaReleaseExecutionPlanResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaReleaseExecutionPlanResult(DOC.exists(), "plan present" if DOC.exists() else "plan missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaReleaseExecutionPlanResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Beta release execution plan check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
