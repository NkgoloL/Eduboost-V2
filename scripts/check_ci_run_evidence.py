#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.ci_run_evidence import build_status, validate_run_url, write_status  # noqa: E402


CRITICAL = [
    "scripts/ci_run_evidence.py",
    "scripts/patch_ci_run_evidence_registry.py",
    "scripts/check_ci_run_evidence.py",
    "tests/unit/test_ci_run_evidence.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("CI run evidence check")

    status = write_status()
    print(f"- INFO CI run evidence status: {status.status}")

    if validate_run_url("https://github.com/NkgoloL/Eduboost-V2/actions/runs/123456789"):
        print("- PASS GitHub Actions run URL validator accepts canonical URL")
    else:
        failures.append("GitHub Actions run URL validator rejected canonical URL")

    if status.status == "external-blocked":
        print("- PASS CI-001 remains external-blocked without accepted evidence")
    elif status.status == "ci-evidence-accepted":
        print("- PASS CI evidence metadata accepted")
    else:
        failures.append(f"unexpected CI run evidence status: {status.status}")

    if release_mode and build_status().status != "ci-evidence-accepted":
        failures.append("release mode requires accepted CI run evidence")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_ci_run_evidence.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode == 0:
            print("- PASS CI run evidence tests")
        else:
            failures.append("CI run evidence tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff CI run evidence check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS CI run evidence check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
