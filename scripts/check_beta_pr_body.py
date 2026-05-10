#!/usr/bin/env python3
"""Validate beta release PR body template."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_release_pr_body.md"
GENERATOR = REPO_ROOT / "scripts" / "generate_beta_pr_body.py"

REQUIRED_SNIPPETS = (
    "Beta Release PR Body",
    "## Summary",
    "## Verification",
    "make final-release-verification",
    "make cluster-h-release-readiness-check",
    "make cluster-h-closure-check",
    "## Release Boundary",
    "controlled staging/beta validation only",
    "does not authorize unrestricted production launch",
    "## Rollback",
    "docs/operations/beta_rollback_runbook.md",
    "## Evidence Index",
    "docs/operations/project_release_closure_index.md",
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "## Known Follow-Ups",
    "normalize frontend package scripts",
)

GENERATOR_SNIPPETS = (
    "generate_beta_pr_body",
    "RELEASE_CANDIDATE",
    "render_pr_body",
)


@dataclass(frozen=True)
class BetaPRBodyResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[BetaPRBodyResult]:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""
    results = [
        BetaPRBodyResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "PR body present" if DOC.exists() else "PR body missing"),
        BetaPRBodyResult(str(GENERATOR.relative_to(REPO_ROOT)), GENERATOR.exists(), "generator present" if GENERATOR.exists() else "generator missing"),
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaPRBodyResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in GENERATOR_SNIPPETS:
        results.append(
            BetaPRBodyResult(
                str(GENERATOR.relative_to(REPO_ROOT)),
                snippet in generator_text,
                f"contains {snippet!r}" if snippet in generator_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Beta PR body check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
