#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.popia_response_contract_no_skips import write_status  # noqa: E402

CRITICAL = [
    "scripts/popia_response_contract_no_skips.py",
    "scripts/check_popia_response_contract_no_skips.py",
    "scripts/patch_popia_response_contract_no_skip_registry.py",
    "tests/unit/test_popia_lifecycle_response_no_skip_proof.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    status = write_status(run_tests=not bool(os.getenv("SKIP_PYTEST_RECURSION")))
    print("POPIA response-contract no-skip proof check")
    print(f"- INFO status: {status.status}")
    print(f"- INFO pytest return code: {status.pytest_return_code}")
    print(f"- INFO skipped detected: {status.skipped_detected}")

    if status.pytest_output:
        print(status.pytest_output)

    if status.status == "popia-response-contract-no-skip-passing":
        print("- PASS POPIA response-contract no-skip proof")
    else:
        failures.extend(status.blockers)

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    venv_py = str((ROOT / ".venv" / "bin" / "python")) if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
    ruff = subprocess.run(
        [
            venv_py,
            "-m",
            "ruff",
            "check",
            *CRITICAL,
            "app/api_v2_routers/popia.py",
            "app/services/popia_consent_lifecycle_adapter.py",
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
        print("- PASS focused Ruff POPIA no-skip response-contract check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS POPIA response-contract no-skip proof check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
