#!/usr/bin/env python3
"""Validate final release verification bundle."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_release_verification_bundle.md"

COMMANDS = (
    ("generated artifact hygiene", ["make", "generated-artifact-hygiene-check"]),
    ("branch sync rebase checklist", ["make", "branch-sync-rebase-checklist-check"]),
    ("beta release final checklist", ["make", "beta-release-final-checklist-check"]),
    ("project release closure index", ["make", "project-release-closure-index-check"]),
    ("beta release execution plan", ["make", "beta-release-execution-plan-check"]),
    ("beta pr body", ["make", "beta-pr-body-check"]),
    ("cluster h release readiness", ["make", "cluster-h-release-readiness-check"]),
    ("cluster h closure", ["make", "cluster-h-closure-check"]),
)

DOC_SNIPPETS = (
    "Final Release Verification Bundle",
    "make generated-artifact-hygiene-check",
    "make branch-sync-rebase-checklist-check",
    "make beta-release-final-checklist-check",
    "make project-release-closure-index-check",
    "make beta-release-execution-plan-check",
    "make beta-pr-body-check",
    "make cluster-h-release-readiness-check",
    "make cluster-h-closure-check",
    "operator-controlled actions",
    "make final-release-verification",
)


@dataclass(frozen=True)
class FinalReleaseVerificationResult:
    name: str
    ok: bool
    detail: str


def run_static_checks() -> list[FinalReleaseVerificationResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        FinalReleaseVerificationResult("document", DOC.exists(), "bundle document present" if DOC.exists() else "bundle document missing")
    ]
    for snippet in DOC_SNIPPETS:
        results.append(
            FinalReleaseVerificationResult(
                "document",
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def run_command_bundle() -> list[FinalReleaseVerificationResult]:
    results: list[FinalReleaseVerificationResult] = []
    for name, command in COMMANDS:
        result = subprocess.run(command, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
        results.append(
            FinalReleaseVerificationResult(
                name,
                result.returncode == 0,
                f"exit {result.returncode}",
            )
        )
    return results


def run_checks(execute: bool = False) -> list[FinalReleaseVerificationResult]:
    results = run_static_checks()
    if execute:
        results.extend(run_command_bundle())
    return results


def main() -> int:
    execute = "--execute" in __import__("sys").argv
    results = run_checks(execute=execute)
    print("Final release verification bundle check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.name}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
