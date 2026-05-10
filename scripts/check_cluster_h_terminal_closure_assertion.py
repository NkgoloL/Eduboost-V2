#!/usr/bin/env python3
"""Validate Cluster H terminal closure assertion."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "cluster_h_terminal_closure_assertion.md"

REQUIRED_SNIPPETS = (
    "Cluster H Terminal Closure Assertion",
    "Cluster H release readiness check is green",
    "Cluster H closure check is green",
    "beta governance seal check is green",
    "beta release final index check is green",
    "post-beta evidence archive manifest check is green",
    "final Cluster H closeout rollup check is green",
    "beta acceptance exit criteria check is green",
    "final beta operator packet check is green",
    "release audit trail index check is green",
    "all Cluster H evidence is controlled staging/beta evidence",
    "no unrestricted production launch is authorized",
    "no deployment is executed by this assertion",
    "no release tag is created by this assertion",
    "no manual approval is replaced by this assertion",
    "no unresolved blocker issue is overridden by this assertion",
    "no workflow logs are replaced by this assertion",
    "Cluster H is terminally closed for controlled staging/beta evidence",
    "every registered Cluster H checker passes",
    "release owner records a matching decision log entry",
    "does not approve production launch, execute deployment, create release tags, or override manual approval",
    "make cluster-h-terminal-closure-assertion-check",
)


@dataclass(frozen=True)
class ClusterHTerminalClosureAssertionResult:
    ok: bool
    detail: str


def run_checks() -> list[ClusterHTerminalClosureAssertionResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [ClusterHTerminalClosureAssertionResult(DOC.exists(), "assertion present" if DOC.exists() else "assertion missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(ClusterHTerminalClosureAssertionResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))
    return results


def main() -> int:
    results = run_checks()
    print("Cluster H terminal closure assertion check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
