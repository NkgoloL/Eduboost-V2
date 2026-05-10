#!/usr/bin/env python3
"""Validate Cluster H release readiness baseline evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "tests/unit/test_cluster_h_final_project_closure_wiring.py",
    "tests/unit/test_project_release_closure_index.py",
    "tests/unit/test_beta_release_final_checklist.py",
    "tests/unit/test_release_artifact_retention_contract.py",
    "scripts/check_project_release_closure_index.py",
    "scripts/check_beta_release_final_checklist.py",
    "scripts/check_release_artifact_retention_contract.py",
    "docs/operations/project_release_closure_index.md",
    "docs/operations/beta_release_final_checklist.md",
    "docs/operations/release_artifact_retention_contract.md",
    "tests/unit/test_cluster_h_bundle_approval_closure.py",
    "tests/unit/test_cluster_h_closure.py",
    "tests/unit/test_release_candidate_tag_manifest.py",
    "tests/unit/test_release_approval_workflow_contract.py",
    "tests/unit/test_beta_release_evidence_bundle.py",
    ".github/workflows/beta-release-approval.yml",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "docs/operations/release_candidate_tag_manifest.md",
    "docs/operations/release_approval_workflow_contract.md",
    "docs/operations/beta_release_evidence_bundle.md",
    "scripts/check_cluster_h_closure.py",
    "scripts/check_release_candidate_tag_manifest.py",
    "scripts/generate_release_candidate_tag_manifest.py",
    "scripts/check_release_approval_workflow_contract.py",
    "scripts/check_beta_release_evidence_bundle.py",
    "scripts/generate_beta_release_evidence_bundle.py",
    "tests/unit/test_cluster_h_operational_release_controls.py",
    "tests/unit/test_post_deploy_staging_smoke_checklist.py",
    "tests/unit/test_beta_rollback_runbook.py",
    "tests/unit/test_beta_signoff_manifest.py",
    "docs/operations/post_deploy_staging_smoke_checklist.md",
    "docs/operations/beta_rollback_runbook.md",
    "docs/operations/beta_signoff_manifest.md",
    "scripts/check_post_deploy_staging_smoke_checklist.py",
    "scripts/check_beta_rollback_runbook.py",
    "scripts/check_beta_signoff_manifest.py",
    "scripts/generate_beta_signoff_manifest.py",
    "docs/operations/beta_release_readiness_contract.md",
    "docs/operations/staging_smoke_evidence_manifest.md",
    "scripts/check_beta_release_readiness_contract.py",
    "scripts/generate_staging_smoke_evidence_manifest.py",
    "scripts/check_staging_smoke_evidence_manifest.py",
    "tests/unit/test_beta_release_readiness_contract.py",
    "tests/unit/test_staging_smoke_evidence_manifest.py",
)

CONTENT_REQUIREMENTS = {
    "docs/operations/project_release_closure_index.md": (
        "Project Release Closure Index",
        "Staging and Beta Release Closure",
    ),
    "docs/operations/beta_release_final_checklist.md": (
        "Beta Release Final Checklist",
        "no unrestricted production launch",
    ),
    "docs/operations/release_artifact_retention_contract.md": (
        "Release Artifact Retention Contract",
        "generated coverage output is not treated as release evidence",
    ),
    ".github/workflows/beta-release-approval.yml": (
        "workflow_dispatch:",
        "make beta-release-evidence-bundle",
        "make cluster-h-release-readiness-check",
    ),
    "docs/operations/CLUSTER_H_CLOSURE.md": (
        "Cluster H Staging and Beta Release Closure",
        "does not authorize unrestricted production launch",
    ),
    "docs/operations/release_candidate_tag_manifest.md": (
        "Release Candidate Tag Manifest",
        "Do not create or push the release tag until Cluster H checks pass",
    ),
    "docs/operations/release_approval_workflow_contract.md": (
        "Release Approval Workflow Contract",
        "manual workflow dispatch",
    ),
    "docs/operations/beta_release_evidence_bundle.md": (
        "Beta Release Evidence Bundle",
        "Cluster G closure",
    ),
    "docs/operations/post_deploy_staging_smoke_checklist.md": (
        "Post-Deploy Staging Smoke Checklist",
        "auth/consent denial UX contract passes",
    ),
    "docs/operations/beta_rollback_runbook.md": (
        "Beta Rollback Runbook",
        "Deploy last known good artifact or revert the release commit",
    ),
    "docs/operations/beta_signoff_manifest.md": (
        "Beta Sign-Off Manifest",
        "rollback owner sign-off",
        "valid only for the referenced commit and release candidate",
    ),
    "Makefile": (
        "beta-release-readiness-contract-check:",
        "staging-smoke-evidence-manifest:",
        "staging-smoke-evidence-manifest-check:",
        "cluster-h-release-readiness-check:",
        "beta-signoff-manifest:",
        "beta-signoff-manifest-check:",
        "beta-rollback-runbook-check:",
        "post-deploy-staging-smoke-checklist-check:",
        "beta-release-evidence-bundle:",
        "beta-release-evidence-bundle-check:",
        "release-approval-workflow-contract-check:",
        "release-candidate-tag-manifest:",
        "release-candidate-tag-manifest-check:",
        "cluster-h-closure-check:",
        "release-artifact-retention-contract-check:",
        "beta-release-final-checklist-check:",
        "project-release-closure-index-check:",
    ),
    "docs/operations/beta_release_readiness_contract.md": (
        "Beta Release Readiness Contract",
        "Cluster G frontend vertical journey closure",
        "controlled validation with limited users",
    ),
    "docs/operations/staging_smoke_evidence_manifest.md": (
        "Staging Smoke Evidence Manifest",
        "Cluster G frontend journey closure",
        "make staging-smoke-evidence-manifest",
    ),
}


@dataclass(frozen=True)
class ClusterHReadinessResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ClusterHReadinessResult]:
    results: list[ClusterHReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            ClusterHReadinessResult(
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
                ClusterHReadinessResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Cluster H release readiness check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
