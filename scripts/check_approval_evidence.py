#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.approval_evidence import APPROVALS, build_status, write_status  # noqa: E402


CRITICAL = [
    "scripts/approval_evidence.py",
    "scripts/patch_approval_evidence_registry.py",
    "scripts/check_approval_evidence.py",
    "tests/unit/test_approval_evidence.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Approval evidence check")

    status = write_status()
    print(f"- INFO approval evidence status: {status.status}")

    if len(status.approvals) == len(APPROVALS):
        print("- PASS all tracked approval records evaluated")
    else:
        failures.append("not all approval records evaluated")

    if status.status == "external-blocked":
        print("- PASS approvals remain external-blocked until metadata is complete")
    elif status.status == "approvals-complete":
        print("- PASS approval metadata complete")
    else:
        failures.append(f"unexpected approval evidence status: {status.status}")

    if release_mode and build_status().status != "approvals-complete":
        failures.append("release mode requires all legal/security/content approvals complete")

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
                "tests/unit/test_approval_evidence.py",
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
            print("- PASS approval evidence tests")
        else:
            failures.append("approval evidence tests failed")

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
        print("- PASS focused Ruff approval evidence check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS approval evidence check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
