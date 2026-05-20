#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.live_db_tx_evidence import SLICES, build_status, write_status  # noqa: E402


CRITICAL = [
    "scripts/live_db_tx_evidence.py",
    "scripts/patch_live_db_tx_evidence_registry.py",
    "scripts/check_live_db_tx_evidence.py",
    "tests/unit/test_live_db_tx_evidence.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Live DB transaction evidence check")

    status = write_status()
    print(f"- INFO live DB evidence status: {status.status}")

    if len(status.records) == len(SLICES):
        print("- PASS all route transaction slices evaluated")
    else:
        failures.append("not all route transaction slices evaluated")

    if status.status == "external-blocked":
        print("- PASS live DB evidence remains blocked while metadata is pending")
    elif status.status == "live-db-evidence-complete":
        print("- PASS live DB evidence metadata complete")
    else:
        failures.append(f"unexpected live DB evidence status: {status.status}")

    if release_mode and build_status().status != "live-db-evidence-complete":
        failures.append("release mode requires complete live DB transaction evidence")

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
                "tests/unit/test_live_db_tx_evidence.py",
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
            print("- PASS live DB transaction evidence tests")
        else:
            failures.append("live DB transaction evidence tests failed")

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
        print("- PASS focused Ruff live DB transaction evidence check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS live DB transaction evidence check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
