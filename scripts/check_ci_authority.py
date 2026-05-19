#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.ci_authority import registry_ci_status, write_status  # noqa: E402


CRITICAL = [
    "scripts/ci_authority.py",
    "scripts/patch_ci_authority_registry.py",
    "scripts/check_ci_authority.py",
    "tests/unit/test_ci_authority.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("CI authority check")

    status = write_status()
    print(f"- INFO CI status: {status.ci_status}")

    if status.workflow_present:
        print("- PASS GitHub workflow file exists")
    else:
        failures.append("No GitHub workflow file found")

    if status.required_local_targets_present:
        print(f"- PASS local CI-equivalent targets present: {len(status.required_local_targets_present)}")
    else:
        failures.append("No required local CI-equivalent targets found")

    if status.ci_evidence_file_exists:
        print("- PASS ci_evidence.md exists")
    else:
        failures.append("ci_evidence.md missing")

    registry_status = registry_ci_status()
    if registry_status == "external-blocked":
        print("- PASS CI-001 registry status remains external-blocked")
    elif registry_status == "runtime-passing" and status.ci_run_url_present:
        print("- PASS CI-001 registry status has run URL support")
    else:
        failures.append(f"Unexpected CI-001 registry proof_status: {registry_status}")

    if status.ci_run_url_present:
        print(f"- PASS GitHub Actions run URL present: {status.ci_run_url}")
    else:
        print("- INFO GitHub Actions run URL not present; CI-001 remains external-blocked")

    if release_mode and not status.ci_run_url_present:
        failures.append("release mode requires real GitHub Actions run URL")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/unit/test_ci_authority.py",
                "-q",
                "--no-cov",
                "--tb=short",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode == 0:
            print("- PASS CI authority unit tests")
        else:
            failures.append("CI authority unit tests failed")

    ruff = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            *CRITICAL,
            "--select",
            "F821,F401,F811,E402",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff CI authority check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS CI authority check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
