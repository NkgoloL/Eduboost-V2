#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.proof_pytest import run_pytest_proof  # noqa: E402

CRITICAL = [
    "app/services/diagnostic_route_integrity.py",
    "app/services/diagnostic_session_integrity.py",
    "app/api_v2_routers/diagnostics.py",
    "scripts/check_diagnostics_session_binding.py",
    "scripts/proof_pytest.py",
    "tests/unit/test_diagnostic_route_integrity.py",
    "tests/integration/test_diagnostics_session_binding_routes.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("Diagnostics session binding check")

    route_source = read("app/api_v2_routers/diagnostics.py")
    for token in ("validate_adaptive_diagnostic_response", "caps_ref", "diagnostic_respond", "diagnostic_next_item"):
        if token in route_source:
            print(f"- PASS diagnostics.py contains {token}")
        else:
            failures.append(f"diagnostics.py missing {token}")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("IN_SUBPROCESS_CHECK"):
        try:
            run_pytest_proof(
                [
                    "-c",
                    "pytest.ini",
                    "tests/unit/test_diagnostic_route_integrity.py",
                    "tests/integration/test_diagnostics_session_binding_routes.py",
                    "-q",
                    "--no-cov",
                    "--tb=short",
                ],
                root=ROOT,
                require_no_skips=True,
                extra_env={"IN_SUBPROCESS_CHECK": "1"},
            )
            print("- PASS diagnostics session binding tests with zero skips")
        except Exception as exc:
            failures.append(str(exc))

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff diagnostics session binding check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS diagnostics session binding check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
