#!/usr/bin/env python3
"""Validate release owner execution guardrail."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_owner_execution_guardrail.md"

REQUIRED_SNIPPETS = (
    "Release Owner Execution Guardrail",
    "evidence completion is not deployment authorization",
    "release owner must review final release handoff package",
    "release owner must review beta governance seal checklist",
    "release owner must review release owner accountability matrix",
    "release owner must review beta release decision log",
    "release owner must verify unresolved blocker issue status",
    "release owner must verify release candidate and commit SHA",
    "release owner must verify manual approval workflow evidence",
    "release owner must verify rollback owner readiness",
    "release owner must verify post-deploy verification owner readiness",
    "make cluster-h-release-readiness-check",
    "make cluster-h-terminal-closure-assertion-check",
    "make beta-governance-seal-check",
    "make final-release-handoff-package-check",
    "make post-terminal-audit-readiness-check",
    "make evidence-archive-completeness-guard-check",
    "this guardrail does not trigger deployment",
    "this guardrail does not create release tags",
    "this guardrail does not approve production launch",
    "this guardrail does not override manual approval",
    "this guardrail does not resolve blocker issues",
    "this guardrail does not replace platform workflow logs",
    "does not approve production launch, execute deployment, create release tags, or override manual approval",
    "make release-owner-execution-guardrail-check",
)


@dataclass(frozen=True)
class ReleaseOwnerExecutionGuardrailResult:
    ok: bool
    detail: str


def run_checks() -> list[ReleaseOwnerExecutionGuardrailResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [ReleaseOwnerExecutionGuardrailResult(DOC.exists(), "guardrail present" if DOC.exists() else "guardrail missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseOwnerExecutionGuardrailResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Release owner execution guardrail check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
