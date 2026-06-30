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

from scripts.db_live_only_table_ownership import EXPECTED_LIVE_ONLY_TABLES, write_status  # noqa: E402

CRITICAL = [
    "scripts/db_live_only_table_ownership.py",
    "scripts/patch_db_live_only_table_ownership_registry.py",
    "scripts/check_db_live_only_table_ownership.py",
    "tests/unit/test_db_live_only_table_ownership.py",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    status = write_status()

    print("DB live-only table ownership check")
    print(f"- INFO status: {status.status}")
    print(f"- INFO accepted records: {status.accepted_count}/{status.required_count}")

    if status.status != "db-live-only-table-ownership-accepted":
        failures.extend(status.blockers)
    else:
        print("- PASS live-only table ownership policy accepted")

    for path in CRITICAL:
        ast.parse(_read(path))
        print(f"- PASS syntax {path}")

    record_tables = {record.table for record in status.records}
    for table in EXPECTED_LIVE_ONLY_TABLES:
        if table not in record_tables:
            failures.append(f"missing ownership record for {table}")

    registry = ROOT / "docs/release/evidence_status_registry.yml"
    if registry.exists():
        text = registry.read_text(encoding="utf-8")
        match = re.search(
            r"(?ms)(^  - id: DB-OWNERSHIP-001R\n.*?)(?=^  - id: |\Z)",
            text,
        )
        if match and "blocks_beta: true" in match.group(1):
            failures.append("DB-OWNERSHIP-001R should not block beta unless ownership is migration-required")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/unit/test_db_live_only_table_ownership.py",
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
            failures.append("DB live-only table ownership unit tests failed")

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
        print("- PASS focused Ruff DB live-only table ownership check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS DB live-only table ownership check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
