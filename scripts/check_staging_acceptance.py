#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.staging_acceptance_evidence import registry_staging_status, write_status  # noqa: E402


CRITICAL = [
    "scripts/staging_acceptance_evidence.py",
    "scripts/patch_staging_acceptance_registry.py",
    "scripts/check_staging_acceptance.py",
    "tests/unit/test_staging_acceptance_evidence.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Staging acceptance evidence check")

    status = write_status()
    print(f"- INFO staging status: {status.status}")

    if status.status == "external-blocked":
        print("- PASS staging remains external-blocked without real evidence")
    elif status.status == "staging-accepted":
        print("- PASS staging evidence accepted")
    else:
        failures.append(f"unexpected staging status: {status.status}")

    registry_status = registry_staging_status()
    if registry_status == "external-blocked":
        print("- PASS STAGING-001 registry status remains external-blocked")
    elif status.status == "staging-accepted" and registry_status in {"runtime-passing", "production-ready"}:
        print("- PASS STAGING-001 registry status has evidence support")
    else:
        failures.append(f"unexpected STAGING-001 registry status: {registry_status}")

    if release_mode and status.status != "staging-accepted":
        failures.append("release mode requires accepted staging evidence")

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
                "tests/unit/test_staging_acceptance_evidence.py",
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
            print("- PASS staging acceptance evidence tests")
        else:
            failures.append("staging acceptance evidence tests failed")

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
        print("- PASS focused Ruff staging acceptance check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS staging acceptance evidence check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
