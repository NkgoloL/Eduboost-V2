#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.audit_write_runtime_evidence import ACCEPTED_STATUS, write_status  # noqa: E402

CRITICAL = [
    "scripts/audit_write_runtime_evidence.py",
    "scripts/patch_audit_write_runtime_registry.py",
    "scripts/check_audit_write_runtime_evidence.py",
    "tests/unit/test_audit_write_runtime_evidence.py",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _entry(text: str, item_id: str) -> str:
    match = re.search(rf"(?ms)(^  - id: {re.escape(item_id)}\n.*?)(?=^  - id: |\Z)", text)
    if not match:
        raise AssertionError(f"missing registry entry {item_id}")
    return match.group(1)


def main() -> int:
    failures: list[str] = []
    run_flow = os.getenv("AUDIT_WRITE_RUN_FLOW") == "1" or os.getenv("AUDIT_WRITE_ACCEPT") == "1"
    status = write_status(run_flow=run_flow)
    print("Audit write runtime evidence check")
    print(f"- INFO status: {status.status}")
    print(f"- INFO audit_events before: {status.audit_events_count_before}")
    print(f"- INFO audit_events after: {status.audit_events_count_after}")
    print(f"- INFO audit_events delta: {status.audit_events_delta}")

    for path in CRITICAL:
        ast.parse(_read(path))
        print(f"- PASS syntax {path}")

    if os.getenv("AUDIT_WRITE_ACCEPT") == "1":
        if status.status != ACCEPTED_STATUS:
            failures.extend(status.blockers)
        else:
            registry = ROOT / "docs/release/evidence_status_registry.yml"
            if registry.exists():
                text = registry.read_text(encoding="utf-8")
                for item_id in ["AUDIT-WRITE-001", "AUDIT-WRITE-001R"]:
                    entry = _entry(text, item_id)
                    for required in ["proof_status: runtime-passing", "closure_blocker: none", "release_ready: true", "blocks_beta: false"]:
                        if required not in entry:
                            failures.append(f"{item_id} missing {required}")
    else:
        print("- INFO acceptance not requested; tooling check only")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_audit_write_runtime_evidence.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append("audit write runtime evidence unit tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff audit write runtime evidence check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS audit write runtime evidence tooling check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
