#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.final_gate_classifier import write_refresh  # noqa: E402

CRITICAL = [
    "scripts/final_gate_classifier.py",
    "scripts/final_gate_refresh.py",
    "scripts/patch_final_gate_refresh_classifier_registry.py",
    "scripts/check_final_gate_refresh_classifier.py",
    "tests/unit/test_final_gate_refresh_classifier.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    refresh = write_refresh()
    print("Final gate refresh classifier check")
    print(f"- INFO beta decision: {refresh.beta_decision}")
    print(f"- INFO beta blocker count: {refresh.beta_blocker_count}")

    accepted_ids = {finding.id for finding in refresh.resolved_non_blocking_findings}
    for item_id in {"AUTH-REFRESH-DB-PROOF-001", "AUTH-REFRESH-DB-EVIDENCE-001"}:
        if item_id not in accepted_ids:
            failures.append(f"{item_id} is not classified as resolved non-blocking accepted finding")

    beta_ids = {finding.id for finding in refresh.beta_critical_findings}
    for item_id in {"POPIA-001", "CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001", "EXT-GATE-001"}:
        if item_id not in beta_ids:
            failures.append(f"{item_id} must remain beta-blocking")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_final_gate_refresh_classifier.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append("final gate refresh classifier unit tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff final gate refresh classifier check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS final gate refresh classifier check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
