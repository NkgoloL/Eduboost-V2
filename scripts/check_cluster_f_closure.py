#!/usr/bin/env python3
"""Run the full Cluster F AI/CAPS/safety closure suite."""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

COMMANDS = (
    ("caps alignment contract", ["make", "caps-alignment-contract-check"]),
    ("ai safety boundary", ["make", "ai-safety-boundary-check"]),
    ("ai prompt input contract", ["make", "ai-prompt-input-contract-check"]),
    ("diagnostic generation safety", ["make", "diagnostic-generation-safety-check"]),
    ("lesson generation safety", ["make", "lesson-generation-safety-check"]),
    ("remediation safety", ["make", "remediation-safety-contract-check"]),
    ("llm provider fallback", ["make", "llm-provider-fallback-contract-check"]),
    ("ai output schema", ["make", "ai-output-schema-contract-check"]),
    ("ai output fixture validation", ["make", "ai-output-fixture-validation-check"]),
    ("ai refusal fixtures", ["make", "ai-refusal-fixture-check"]),
    ("ai fixture coverage", ["make", "ai-fixture-coverage-check"]),
    ("ai prompt secret leakage", ["make", "ai-prompt-secret-leakage-check"]),
    ("ai prompt surface inventory", ["make", "ai-prompt-surface-inventory-check"]),
    ("cluster f evidence", ["make", "cluster-f-ai-safety-check"]),
    (
        "cluster f unit tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_caps_alignment_contract.py",
            "tests/unit/test_ai_safety_boundary_contract.py",
            "tests/unit/test_ai_prompt_input_contract.py",
            "tests/unit/test_diagnostic_generation_safety_contract.py",
            "tests/unit/test_lesson_generation_safety_contract.py",
            "tests/unit/test_remediation_safety_contract.py",
            "tests/unit/test_llm_provider_fallback_contract.py",
            "tests/unit/test_ai_output_schema_contract.py",
            "tests/unit/test_validate_ai_output_fixtures.py",
            "tests/unit/test_ai_refusal_fixtures.py",
            "tests/unit/test_ai_fixture_coverage_matrix.py",
            "tests/unit/test_ai_prompt_secret_leakage.py",
            "tests/unit/test_ai_prompt_surface_inventory.py",
            "tests/unit/test_ai_output_fixtures.py",
            "tests/unit/test_cluster_f_ai_safety_evidence.py",
            "tests/unit/test_cluster_f_prompt_diagnostic_evidence.py",
            "tests/unit/test_cluster_f_provider_output_evidence.py",
            "-q",
            "--no-cov",
        ],
    ),
)


@dataclass(frozen=True)
class ClusterFClosureResult:
    name: str
    ok: bool
    returncode: int
    output: str


def run_command(name: str, command: list[str]) -> ClusterFClosureResult:
    result = subprocess.run(command, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    return ClusterFClosureResult(
        name=name,
        ok=result.returncode == 0,
        returncode=result.returncode,
        output=(result.stdout + result.stderr).strip(),
    )


def run_checks() -> list[ClusterFClosureResult]:
    return [run_command(name, command) for name, command in COMMANDS]


def main() -> int:
    results = run_checks()
    print("Cluster F closure check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.name}: exit {result.returncode}")
        if not result.ok and result.output:
            print(result.output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
