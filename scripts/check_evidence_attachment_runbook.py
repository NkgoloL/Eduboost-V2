#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.evidence_attachment_runbook import COMMANDS, RELEASE_MODE_SEQUENCE, write_runbook  # noqa: E402

CRITICAL = [
    "scripts/evidence_attachment_runbook.py",
    "scripts/check_evidence_attachment_runbook.py",
    "scripts/patch_evidence_attachment_runbook_registry.py",
    "tests/unit/test_evidence_attachment_runbook.py",
]
RUNBOOK = ROOT / "docs/release/evidence_attachment_runbook.md"

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def main() -> int:
    failures: list[str] = []
    print("Evidence attachment runbook check")
    manifest = write_runbook()
    print(f"- INFO command count: {manifest.command_count}")

    if manifest.command_count >= 8:
        print("- PASS evidence attachment commands present")
    else:
        failures.append("too few evidence attachment commands")

    text = RUNBOOK.read_text(encoding="utf-8")
    for item in ["CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001", "ROUTE-TX-AUTH-001", "ROUTE-TX-POPIA-001", "ROUTE-TX-DIAG-001"]:
        if item in text:
            print(f"- PASS runbook includes {item}")
        else:
            failures.append(f"runbook missing {item}")

    for command in RELEASE_MODE_SEQUENCE:
        if command in text:
            print(f"- PASS release sequence includes {command}")
        else:
            failures.append(f"release sequence missing {command}")

    if all("Expected until evidence" not in cmd.command for cmd in COMMANDS):
        print("- PASS command table separates commands from expected failure notes")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run([sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_evidence_attachment_runbook.py", "-q", "--no-cov", "--tb=short"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)
        print(result.stdout)
        if result.returncode == 0:
            print("- PASS evidence attachment runbook tests")
        else:
            failures.append("evidence attachment runbook tests failed")

    ruff = subprocess.run([sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if ruff.returncode == 0:
        print("- PASS focused Ruff evidence attachment runbook check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS evidence attachment runbook check")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
