#!/usr/bin/env python3
"""Validate release change-control exception log."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_change_control_exception_log.md"

REQUIRED_SNIPPETS = (
    "Release Change-Control Exception Log",
    "Exception ID",
    "Change Type",
    "literal repair / evidence refresh / approval completion / prohibited change",
    "Requested By",
    "Approved By",
    "Commit SHA",
    "Release Candidate",
    "Affected Evidence",
    "Required Rerun",
    "final release verification",
    "literal evidence phrase repair may be recorded as low-risk",
    "generated snapshot refresh may be recorded as evidence refresh",
    "prohibited change must identify affected release boundary",
    "prohibited change requires explicit approval before merge",
    "prohibited change requires final release verification rerun",
    "authorization, consent, API, AI safety, deployment, or data-resilience changes require owner approval",
    "each exception must reference commit SHA and release candidate",
    "unresolved exception blocks beta execution",
    "does not approve prohibited changes, execute deployment, create release tags, or bypass required reruns",
    "make release-change-control-exception-log-check",
)


@dataclass(frozen=True)
class ReleaseChangeControlExceptionLogResult:
    ok: bool
    detail: str


def run_checks() -> list[ReleaseChangeControlExceptionLogResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        ReleaseChangeControlExceptionLogResult(DOC.exists(), "log present" if DOC.exists() else "log missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseChangeControlExceptionLogResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Release change-control exception log check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
