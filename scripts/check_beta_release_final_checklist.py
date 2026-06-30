#!/usr/bin/env python3
"""Validate beta release final checklist."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_release_final_checklist.md"

REQUIRED_SNIPPETS = (
    "Beta Release Final Checklist",
    "working tree is clean except intentional release evidence files",
    "branch is rebased on remote target branch",
    "OpenAPI drift check passes",
    "staging release gate check passes",
    "release evidence artifacts check passes",
    "Cluster C POPIA consent closure check passes",
    "Cluster D deployment closure check passes",
    "Cluster E data resilience closure check passes",
    "Cluster F AI safety closure check passes",
    "Cluster G frontend journey closure check passes",
    "Cluster H closure check passes",
    "staging smoke evidence manifest generated",
    "beta sign-off manifest generated",
    "beta release evidence bundle generated",
    "release candidate tag manifest generated",
    "privacy/POPIA approval recorded",
    "rollback owner approval recorded",
    "no unrestricted production launch",
    "no release tag push before approval",
    "no generated `coverage.xml` conflict carried into release commit",
    "make beta-release-final-checklist-check",
)


@dataclass(frozen=True)
class BetaReleaseFinalChecklistResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaReleaseFinalChecklistResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaReleaseFinalChecklistResult(DOC.exists(), "checklist present" if DOC.exists() else "checklist missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaReleaseFinalChecklistResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Beta release final checklist check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
