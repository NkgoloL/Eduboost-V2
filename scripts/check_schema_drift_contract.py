#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    print("Schema drift contract check")

    required = [
        Path("scripts/compare_orm_tables_to_database.py"),
        Path("docs/release/schema_drift_evidence_contract.md"),
    ]
    failures: list[str] = []

    for path in required:
        if (REPO_ROOT / path).exists():
            print(f"- PASS [file] {path}: present")
        else:
            print(f"- FAIL [file] {path}: missing")
            failures.append(f"missing {path}")

    result = subprocess.run(
        [sys.executable, "scripts/compare_orm_tables_to_database.py"],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        print("- FAIL [command] ORM-only schema drift check failed")
        failures.append("compare_orm_tables_to_database.py failed without DB")
    else:
        print("- PASS [command] ORM-only schema drift check runs without DB")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
