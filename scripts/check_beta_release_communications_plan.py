#!/usr/bin/env python3
"""Validate beta release communications plan."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_release_communications_plan.md"

REQUIRED_SNIPPETS = (
    "Beta Release Communications Plan",
    "release operator",
    "technical approver",
    "privacy/POPIA approver",
    "rollback owner",
    "post-deploy verification owner",
    "incident contact",
    "beta support contact",
    "project owner",
    "release candidate identifier",
    "merged commit SHA",
    "release window",
    "beta boundary and non-production scope",
    "rollback runbook link",
    "post-deploy staging smoke checklist link",
    "release start notification",
    "deployment status notification",
    "smoke verification status notification",
    "rollback trigger notification if applicable",
    "approval or rejection outcome",
    "release completion or rollback outcome",
    "beta release decision log update",
    "release audit trail index link",
    "post-deploy smoke checklist result",
    "follow-up owner assignment",
    "does not approve release, execute deployment, create release tags, or replace the beta release decision log",
    "make beta-release-communications-plan-check",
)


@dataclass(frozen=True)
class BetaReleaseCommunicationsPlanResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaReleaseCommunicationsPlanResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaReleaseCommunicationsPlanResult(DOC.exists(), "plan present" if DOC.exists() else "plan missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaReleaseCommunicationsPlanResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta release communications plan check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
