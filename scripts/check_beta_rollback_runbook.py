#!/usr/bin/env python3
"""Validate beta rollback runbook evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_rollback_runbook.md"

REQUIRED_SNIPPETS = (
    "Beta Rollback Runbook",
    "Rollback Triggers",
    "OpenAPI contract drift",
    "authentication or authorization regression",
    "consent gate or POPIA audit regression",
    "database backup/restore integrity failure",
    "AI safety fixture or prompt leakage failure",
    "frontend journey, denial UX, or accessibility regression",
    "last known good commit is identified",
    "database backup manifest is available",
    "rollback owner is assigned",
    "Freeze new deployments",
    "Deploy last known good artifact or revert the release commit",
    "Run staging smoke checks",
    "Verify learner and parent journey availability",
    "Verify consent/audit behavior",
    "Post-Rollback Evidence",
    "make beta-rollback-runbook-check",
)


@dataclass(frozen=True)
class BetaRollbackRunbookResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaRollbackRunbookResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaRollbackRunbookResult(DOC.exists(), "runbook present" if DOC.exists() else "runbook missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaRollbackRunbookResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Beta rollback runbook check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
