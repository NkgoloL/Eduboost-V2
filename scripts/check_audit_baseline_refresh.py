#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.audit_baseline_refresh import OUT_JSON, write_status  # noqa: E402

CRITICAL = [
    "scripts/audit_baseline_refresh.py",
    "scripts/patch_audit_baseline_refresh_registry.py",
    "scripts/check_audit_baseline_refresh.py",
    "tests/unit/test_audit_baseline_refresh.py",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    status = write_status()

    print("Audit baseline refresh check")
    print(f"- INFO status: {status.status}")
    print(f"- INFO beta decision: {status.beta_decision}")
    print(f"- INFO beta blocker count: {status.beta_blocker_count}")

    for path in CRITICAL:
        ast.parse(_read(path))
        print(f"- PASS syntax {path}")

    if status.current_branch != "codex/production_readiness":
        failures.append(f"unexpected branch {status.current_branch}")

    if status.beta_decision != "NO-GO" and status.remaining_beta_blockers:
        failures.append("beta decision is GO while beta blockers remain")

    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if data.get("current_commit") != status.current_commit:
        failures.append("audit status JSON commit does not match current commit")

    required_surfaces = {
        "final_beta_gate_refresh",
        "release_go_no_go_status",
    }
    surfaces = {surface.name: surface for surface in status.surfaces}
    for name in required_surfaces:
        surface = surfaces.get(name)
        if surface is None or not surface.exists:
            failures.append(f"missing required surface {name}")
        elif surface.stale:
            failures.append(f"surface {name} is stale")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/unit/test_audit_baseline_refresh.py",
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
        if result.returncode != 0:
            failures.append("audit baseline refresh unit tests failed")

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
        print("- PASS focused Ruff audit baseline refresh check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS audit baseline refresh check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
