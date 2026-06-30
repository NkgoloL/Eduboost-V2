#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRITICAL = [
    "app/services/diagnostic_scoring_snapshot.py",
    "app/modules/diagnostics/diagnostic_session_service.py",
    "scripts/patch_diagnostics_scoring_snapshot.py",
    "scripts/check_diagnostics_scoring_snapshot.py",
    "tests/unit/test_diagnostics_scoring_snapshot.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("Diagnostics scoring snapshot check")
    service_source = read("app/modules/diagnostics/diagnostic_session_service.py")
    if 'responses = [(item, bool(row["correct"])) for row in snap.responses]' in service_source:
        failures.append("diagnostic session service still scores all history with current item")
    if "diagnostic_item_from_response(row, fallback_item=item)" in service_source:
        print("- PASS historical response item reconstruction is used")
    else:
        failures.append("diagnostic item reconstruction missing")
    if "diagnostic_response_snapshot(item, item_id=item_id)" in service_source:
        print("- PASS per-response scoring snapshot is persisted")
    else:
        failures.append("diagnostic response scoring snapshot missing")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_diagnostics_scoring_snapshot.py",
            "-q",
            "--no-cov",
            "--tb=short",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={"PYTHONPATH": str(ROOT), **__import__("os").environ},
        check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        failures.append("diagnostics scoring snapshot tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff diagnostics scoring snapshot check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS diagnostics scoring snapshot check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
