#!/usr/bin/env python3
"""Validate Cluster H closure evidence without recursively executing itself."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "docs/operations/beta_release_readiness_contract.md",
    "docs/operations/staging_smoke_evidence_manifest.md",
    "docs/operations/beta_signoff_manifest.md",
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/beta_rollback_runbook.md",
    "docs/operations/post_deploy_staging_smoke_checklist.md",
    "docs/operations/release_approval_workflow_contract.md",
    "docs/operations/release_candidate_tag_manifest.md",
    "scripts/check_cluster_h_release_readiness.py",
    "scripts/check_cluster_h_closure.py",
    ".github/workflows/cluster-h-release-readiness.yml",
    ".github/workflows/beta-release-approval.yml",
)

CONTENT_REQUIREMENTS = {
    "docs/operations/CLUSTER_H_CLOSURE.md": (
        "Cluster H Staging and Beta Release Closure",
        "make cluster-h-closure-check",
        "does not authorize unrestricted production launch",
    ),
    "Makefile": (
        "cluster-h-closure-check:",
        "cluster-h-release-readiness-check:",
        "beta-release-evidence-bundle-check:",
        "release-approval-workflow-contract-check:",
        "release-candidate-tag-manifest-check:",
    ),
    ".github/workflows/cluster-h-release-readiness.yml": (
        "make cluster-h-closure-check",
        "make cluster-h-release-readiness-check",
    ),
}


@dataclass(frozen=True)
class ClusterHClosureResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ClusterHClosureResult]:
    results: list[ClusterHClosureResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            ClusterHClosureResult(
                "file",
                rel_path,
                path.exists(),
                "present" if path.exists() else "missing",
            )
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                ClusterHClosureResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Cluster H closure check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
