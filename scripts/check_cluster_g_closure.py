#!/usr/bin/env python3
"""Run the full Cluster G frontend journey closure suite."""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

GENERATORS = (
    ("frontend route inventory", [sys.executable, "scripts/generate_frontend_route_inventory.py"]),
    ("frontend api client inventory", [sys.executable, "scripts/generate_frontend_api_client_inventory.py"]),
    ("frontend runtime inventory", [sys.executable, "scripts/generate_frontend_runtime_inventory.py"]),
)

COMMANDS = (
    ("frontend route inventory check", ["make", "frontend-route-inventory-check"]),
    ("frontend api client inventory check", ["make", "frontend-api-client-inventory-check"]),
    ("frontend runtime inventory check", ["make", "frontend-runtime-inventory-check"]),
    ("frontend journey fixture check", ["make", "frontend-journey-fixture-check"]),
    ("frontend mock api fixture check", ["make", "frontend-mock-api-fixture-check"]),
    ("frontend playwright scaffold check", ["make", "frontend-playwright-scaffold-check"]),
    ("frontend playwright specs check", ["make", "frontend-playwright-specs-check"]),
    ("frontend playwright mock helper check", ["make", "frontend-playwright-mock-helper-check"]),
    ("frontend playwright mocked specs check", ["make", "frontend-playwright-mocked-specs-check"]),
    ("frontend e2e env contract check", ["make", "frontend-e2e-env-contract-check"]),
    ("frontend e2e runtime command check", ["make", "frontend-e2e-runtime-command-check"]),
    ("frontend build test lint contract check", ["make", "frontend-build-test-lint-contract-check"]),
    ("frontend e2e opt-in workflow check", ["make", "frontend-e2e-opt-in-workflow-check"]),
    ("frontend accessibility contract check", ["make", "frontend-accessibility-contract-check"]),
    ("frontend accessibility static check", ["make", "frontend-accessibility-static-check"]),
    ("learner vertical journey contract check", ["make", "learner-vertical-journey-contract-check"]),
    ("parent vertical journey contract check", ["make", "parent-vertical-journey-contract-check"]),
    ("frontend auth consent denial check", ["make", "frontend-auth-consent-denial-check"]),
    ("cluster g frontend evidence", ["make", "cluster-g-frontend-check"]),
    (
        "cluster g unit tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_frontend_route_inventory.py",
            "tests/unit/test_frontend_api_client_inventory.py",
            "tests/unit/test_frontend_runtime_inventory.py",
            "tests/unit/test_frontend_journey_fixtures.py",
            "tests/unit/test_frontend_mock_api_fixtures.py",
            "tests/unit/test_frontend_playwright_scaffold.py",
            "tests/unit/test_frontend_playwright_specs.py",
            "tests/unit/test_frontend_playwright_mock_helpers.py",
            "tests/unit/test_frontend_playwright_mocked_specs.py",
            "tests/unit/test_frontend_e2e_environment_contract.py",
            "tests/unit/test_frontend_e2e_runtime_commands.py",
            "tests/unit/test_frontend_build_test_lint_contract.py",
            "tests/unit/test_frontend_e2e_opt_in_workflow.py",
            "tests/unit/test_frontend_accessibility_contract.py",
            "tests/unit/test_frontend_accessibility_static.py",
            "tests/unit/test_learner_vertical_journey_contract.py",
            "tests/unit/test_parent_vertical_journey_contract.py",
            "tests/unit/test_frontend_auth_consent_denial_contract.py",
            "tests/unit/test_cluster_g_frontend_evidence.py",
            "tests/unit/test_cluster_g_parent_denial_evidence.py",
            "tests/unit/test_cluster_g_api_fixture_evidence.py",
            "tests/unit/test_cluster_g_playwright_evidence.py",
            "tests/unit/test_cluster_g_accessibility_evidence.py",
            "tests/unit/test_cluster_g_runtime_mock_evidence.py",
            "tests/unit/test_cluster_g_mocked_playwright_evidence.py",
            "tests/unit/test_cluster_g_e2e_runtime_evidence.py",
            "tests/unit/test_cluster_g_build_e2e_workflow_evidence.py",
            "-q",
            "--no-cov",
        ],
    ),
)


@dataclass(frozen=True)
class ClusterGClosureResult:
    name: str
    ok: bool
    returncode: int
    output: str


def run_command(name: str, command: list[str]) -> ClusterGClosureResult:
    result = subprocess.run(command, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    return ClusterGClosureResult(
        name=name,
        ok=result.returncode == 0,
        returncode=result.returncode,
        output=(result.stdout + result.stderr).strip(),
    )


def run_checks() -> list[ClusterGClosureResult]:
    return [run_command(name, command) for name, command in (*GENERATORS, *COMMANDS)]


def main() -> int:
    results = run_checks()
    print("Cluster G closure check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.name}: exit {result.returncode}")
        if not result.ok and result.output:
            print(result.output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
