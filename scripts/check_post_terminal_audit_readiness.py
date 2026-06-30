#!/usr/bin/env python3
"""Validate post-terminal audit readiness assertion."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "post_terminal_audit_readiness_assertion.md"

REQUIRED_SNIPPETS = (
    "Post-Terminal Audit Readiness Assertion",
    "final release handoff package is present",
    "evidence archive completeness guard is present",
    "beta governance seal checklist is present",
    "beta release final index is present",
    "Cluster H terminal closure assertion is present",
    "post-beta evidence archive manifest is present",
    "beta outcome report template is present",
    "beta retrospective action register is present",
    "release audit trail index is present",
    "release owner accountability matrix is present",
    "audit readiness must reference release candidate and commit SHA",
    "audit readiness must preserve decision chain from readiness to outcome",
    "audit readiness must preserve governance reviewer responsibilities",
    "audit readiness must preserve unresolved follow-up ownership",
    "audit readiness must preserve support and monitoring evidence",
    "audit readiness must avoid unnecessary learner personal information",
    "audit readiness must remain controlled staging/beta evidence",
    "no production launch is authorized by audit readiness",
    "no deployment is executed by audit readiness",
    "no release tag is created by audit readiness",
    "no workflow log is replaced by audit readiness",
    "no manual approval is replaced by audit readiness",
    "does not approve production launch, execute deployment, create release tags, or replace manual approvals",
    "make post-terminal-audit-readiness-check",
)


@dataclass(frozen=True)
class PostTerminalAuditReadinessResult:
    ok: bool
    detail: str


def run_checks() -> list[PostTerminalAuditReadinessResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [PostTerminalAuditReadinessResult(DOC.exists(), "assertion present" if DOC.exists() else "assertion missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(PostTerminalAuditReadinessResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))
    return results


def main() -> int:
    results = run_checks()
    print("Post-terminal audit readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
