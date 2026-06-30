#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.external_approval_gate import REQUIRED_APPROVALS, registry_statuses, write_status  # noqa: E402


CRITICAL = [
    "scripts/external_approval_gate.py",
    "scripts/patch_external_approval_registry.py",
    "scripts/check_external_approval_gate.py",
    "tests/unit/test_external_approval_gate.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("External approval gate check")

    status = write_status()
    print(f"- INFO external approval status: {status.status}")

    if len(status.approvals) == len(REQUIRED_APPROVALS):
        print("- PASS all required approval records evaluated")
    else:
        failures.append("not all approval records evaluated")

    for approval in status.approvals:
        if approval.exists:
            print(f"- PASS {approval.id} evidence file exists")
        else:
            failures.append(f"{approval.id} evidence file missing")
        if approval.approved:
            print(f"- PASS {approval.id} approved")
        else:
            print(f"- INFO {approval.id} remains blocked: {approval.blockers}")

    statuses = registry_statuses()
    for approval_id in REQUIRED_APPROVALS:
        registry_status = statuses.get(approval_id)
        if registry_status == "external-blocked":
            print(f"- PASS {approval_id} registry status is external-blocked")
        elif status.status == "external-approvals-complete" and registry_status in {"runtime-passing", "production-ready"}:
            print(f"- PASS {approval_id} registry status reflects approval")
        else:
            failures.append(f"{approval_id} registry status is unexpected: {registry_status}")

    if release_mode and status.status != "external-approvals-complete":
        failures.append("release mode requires all external approvals to be complete")

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
                "tests/unit/test_external_approval_gate.py",
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
            print("- PASS external approval gate tests")
        else:
            failures.append("external approval gate tests failed")

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
        print("- PASS focused Ruff external approval gate check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS external approval gate check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
