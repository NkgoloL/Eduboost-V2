#!/usr/bin/env python3
"""Validate beta release freeze window contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_release_freeze_window_contract.md"

REQUIRED_SNIPPETS = (
    "Beta Release Freeze Window Contract",
    "Cluster H release readiness check passes",
    "Cluster H final closeout rollup check passes",
    "final release verification check passes",
    "beta evidence consistency check passes",
    "final PR merge readiness check passes",
    "release audit trail index check passes",
    "beta release closure attestation check passes",
    "API contract evidence",
    "authorization and consent gate evidence",
    "Cluster H release-readiness evidence",
    "release candidate tag manifest",
    "beta release evidence bundle",
    "literal evidence phrase repair",
    "generated snapshot refresh",
    "manual approval field completion",
    "decision log entry completion",
    "new feature behavior",
    "schema or API contract change",
    "authorization boundary change",
    "consent boundary change",
    "deployment workflow semantic change",
    "AI safety boundary change",
    "Any prohibited change requires a release change-control exception log entry",
    "rerun of final release verification",
    "does not approve release, execute deployment, create release tags, or override manual approval",
    "make beta-release-freeze-window-check",
)


@dataclass(frozen=True)
class BetaReleaseFreezeWindowResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaReleaseFreezeWindowResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaReleaseFreezeWindowResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaReleaseFreezeWindowResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta release freeze window check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
