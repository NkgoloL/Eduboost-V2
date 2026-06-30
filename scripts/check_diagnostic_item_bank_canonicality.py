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

from scripts.diagnostic_item_bank_canonicality import write_status  # noqa: E402

CRITICAL = [
    "scripts/diagnostic_item_bank_canonicality.py",
    "scripts/patch_diagnostic_item_bank_canonicality_registry.py",
    "scripts/check_diagnostic_item_bank_canonicality.py",
    "tests/unit/test_diagnostic_item_bank_canonicality.py",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _entry(text: str, item_id: str) -> str:
    match = re.search(
        rf"(?ms)(^  - id: {re.escape(item_id)}\n.*?)(?=^  - id: |\Z)",
        text,
    )
    if not match:
        raise AssertionError(f"missing registry entry {item_id}")
    return match.group(1)


def main() -> int:
    failures: list[str] = []
    status = write_status()

    print("Diagnostic item-bank policy check")
    print(f"- INFO status: {status.status}")
    print(f"- INFO decision: {status.decision}")
    print(f"- INFO runtime diagnostic_items refs: {len(status.runtime_diagnostic_items_references)}")

    if status.status != "diagnostic-item-bank-policy-accepted":
        failures.extend(status.blockers)
    else:
        print("- PASS diagnostic item-bank runtime-required policy accepted")

    for path in CRITICAL:
        ast.parse(_read(path))
        print(f"- PASS syntax {path}")

    registry = ROOT / "docs/release/evidence_status_registry.yml"
    if registry.exists():
        text = registry.read_text(encoding="utf-8")
        diag_items = _entry(text, "DIAG-ITEMS-001R")
        diag_score = _entry(text, "DIAG-SCORE-001")

        for required in [
            "proof_status: policy-accepted",
            "closure_blocker: none",
            "blocks_beta: false",
        ]:
            if required not in diag_items:
                failures.append(f"DIAG-ITEMS-001R missing {required}")

        for required in [
            "proof_status: not-proven",
            "release_ready: false",
            "blocks_beta: true",
        ]:
            if required not in diag_score:
                failures.append(f"DIAG-SCORE-001 missing {required}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/unit/test_diagnostic_item_bank_canonicality.py",
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
            failures.append("diagnostic item-bank policy unit tests failed")

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
        print("- PASS focused Ruff diagnostic item-bank policy check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS diagnostic item-bank policy check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
