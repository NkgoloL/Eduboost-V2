#!/usr/bin/env python3
"""Run the full Cluster D CI/deployment/environment closure suite."""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

COMMANDS = (
    ("release evidence artifacts", ["make", "release-evidence-artifacts-check"]),
    ("staging release gate", ["make", "staging-release-gate-check"]),
    ("generate release evidence manifest", [sys.executable, "scripts/generate_release_evidence_manifest.py"]),
    ("environment security contract", ["make", "environment-security-check"]),
    ("production secret placeholder guard", ["make", "production-secret-placeholder-check"]),
    ("dev-only endpoint guard", ["make", "dev-only-endpoint-check"]),
    ("deployment readiness docs", ["make", "deployment-readiness-docs-check"]),
    ("cluster d evidence", ["make", "cluster-d-ci-check"]),
    (
        "cluster d unit tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_environment_security_contract.py",
            "tests/unit/test_production_secret_placeholders.py",
            "tests/unit/test_production_key_vault_behavior.py",
            "tests/unit/test_dev_only_endpoint_exposure.py",
            "tests/unit/test_deployment_readiness_docs.py",
            "tests/unit/test_cluster_d_ci_evidence.py",
            "tests/unit/test_cluster_d_runtime_gates_evidence.py",
            "-q",
            "--no-cov",
        ],
    ),
)


@dataclass(frozen=True)
class ClusterDClosureResult:
    name: str
    ok: bool
    returncode: int
    output: str


def run_command(name: str, command: list[str]) -> ClusterDClosureResult:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return ClusterDClosureResult(
        name=name,
        ok=result.returncode == 0,
        returncode=result.returncode,
        output=(result.stdout + result.stderr).strip(),
    )


def run_checks() -> list[ClusterDClosureResult]:
    return [run_command(name, command) for name, command in COMMANDS]


def main() -> int:
    results = run_checks()
    print("Cluster D closure check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.name}: exit {result.returncode}")
        if not result.ok and result.output:
            print(result.output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
