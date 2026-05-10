#!/usr/bin/env python3
"""Run the full Cluster H staging/beta release closure suite."""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

GENERATORS = (
    ("staging smoke evidence manifest", [sys.executable, "scripts/generate_staging_smoke_evidence_manifest.py"]),
    ("beta signoff manifest", [sys.executable, "scripts/generate_beta_signoff_manifest.py"]),
    ("beta release evidence bundle", [sys.executable, "scripts/generate_beta_release_evidence_bundle.py"]),
    ("release candidate tag manifest", [sys.executable, "scripts/generate_release_candidate_tag_manifest.py"]),
)

COMMANDS = (
    ("beta release readiness contract", ["make", "beta-release-readiness-contract-check"]),
    ("staging smoke manifest check", ["make", "staging-smoke-evidence-manifest-check"]),
    ("beta signoff manifest check", ["make", "beta-signoff-manifest-check"]),
    ("beta release evidence bundle check", ["make", "beta-release-evidence-bundle-check"]),
    ("beta rollback runbook check", ["make", "beta-rollback-runbook-check"]),
    ("post deploy staging smoke checklist check", ["make", "post-deploy-staging-smoke-checklist-check"]),
    ("release approval workflow contract check", ["make", "release-approval-workflow-contract-check"]),
    ("release candidate tag manifest check", ["make", "release-candidate-tag-manifest-check"]),
    ("cluster h release readiness check", ["make", "cluster-h-release-readiness-check"]),
    (
        "cluster h unit tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_beta_release_readiness_contract.py",
            "tests/unit/test_staging_smoke_evidence_manifest.py",
            "tests/unit/test_cluster_h_release_readiness.py",
            "tests/unit/test_beta_signoff_manifest.py",
            "tests/unit/test_beta_rollback_runbook.py",
            "tests/unit/test_post_deploy_staging_smoke_checklist.py",
            "tests/unit/test_cluster_h_operational_release_controls.py",
            "tests/unit/test_beta_release_evidence_bundle.py",
            "tests/unit/test_release_approval_workflow_contract.py",
            "tests/unit/test_release_candidate_tag_manifest.py",
            "tests/unit/test_cluster_h_closure.py",
            "-q",
            "--no-cov",
        ],
    ),
)


@dataclass(frozen=True)
class ClusterHClosureResult:
    name: str
    ok: bool
    returncode: int
    output: str


def run_command(name: str, command: list[str]) -> ClusterHClosureResult:
    result = subprocess.run(command, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    return ClusterHClosureResult(
        name=name,
        ok=result.returncode == 0,
        returncode=result.returncode,
        output=(result.stdout + result.stderr).strip(),
    )


def run_checks() -> list[ClusterHClosureResult]:
    return [run_command(name, command) for name, command in (*GENERATORS, *COMMANDS)]


def main() -> int:
    results = run_checks()
    print("Cluster H closure check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.name}: exit {result.returncode}")
        if not result.ok and result.output:
            print(result.output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
