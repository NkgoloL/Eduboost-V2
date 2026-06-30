#!/usr/bin/env python3
"""Validate project release closure index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "project_release_closure_index.md"

REQUIRED_SNIPPETS = (
    "Project Release Closure Index",
    "Backend and API Closure",
    "Authorization and Consent Closure",
    "Deployment and Environment Closure",
    "Data Resilience Closure",
    "AI Safety Closure",
    "Frontend Journey Closure",
    "Staging and Beta Release Closure",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/beta_release_final_checklist.md",
    "docs/operations/release_artifact_retention_contract.md",
    "make staging-release-gate-check",
    "make release-evidence-artifacts-check",
    "make cluster-g-closure-check",
    "make cluster-h-closure-check",
    "make project-release-closure-index-check",
)


@dataclass(frozen=True)
class ProjectReleaseClosureIndexResult:
    ok: bool
    detail: str


def run_checks() -> list[ProjectReleaseClosureIndexResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        ProjectReleaseClosureIndexResult(DOC.exists(), "index present" if DOC.exists() else "index missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ProjectReleaseClosureIndexResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Project release closure index check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
