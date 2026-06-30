#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.prod_frontend_runtime import write_status  # noqa: E402


CRITICAL = [
    "scripts/prod_frontend_runtime.py",
    "scripts/repair_prod_frontend_runtime.py",
    "scripts/check_prod_frontend_runtime.py",
    "scripts/patch_prod_frontend_runtime_registry.py",
    "tests/unit/test_prod_frontend_runtime.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Production frontend runtime check")

    status = write_status()
    print(f"- INFO status: {status.status}")
    print(f"- INFO compose config: {status.compose_config.status}")

    local_ok = status.status in {
        "runtime-preflight-passing",
        "runtime-preflight-static-passing-compose-tool-unavailable",
        "runtime-evidence-accepted",
    }
    if local_ok:
        print("- PASS production frontend runtime preflight is locally acceptable")
    else:
        failures.extend(blocker for blocker in status.blockers if not blocker.startswith("runtime evidence:"))

    if release_mode and status.status != "runtime-evidence-accepted":
        failures.append("release mode requires accepted production frontend runtime evidence")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        venv_py = str((ROOT / ".venv" / "bin" / "python")) if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [
                venv_py,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/unit/test_prod_frontend_runtime.py",
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
            print("- PASS production frontend runtime tests")
        else:
            failures.append("production frontend runtime tests failed")

    venv_py = str((ROOT / ".venv" / "bin" / "python")) if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
    ruff = subprocess.run(
        [
            venv_py,
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
        print("- PASS focused Ruff production frontend runtime check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS production frontend runtime check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
