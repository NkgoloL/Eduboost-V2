#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.db_migration_seed_repeatability import (  # noqa: E402
    EXPECTED_IRT_ROWS,
    SUPABASE_SQL,
    IRT_SEED_SQL,
    write_status,
)

CRITICAL = [
    "scripts/db_migration_seed_repeatability.py",
    "scripts/patch_db_migration_seed_repeatability_registry.py",
    "scripts/check_db_migration_seed_repeatability.py",
    "tests/unit/test_db_migration_seed_repeatability.py",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    status = write_status()

    print("DB migration + seed repeatability check")
    print(f"- INFO status: {status.status}")
    print(f"- INFO unique IRT rows: {status.unique_irt_seed_rows}")
    print(f"- INFO Supabase SQL: {status.supabase_sql_path}")

    if status.status != "db-migration-seed-repeatability-passing":
        failures.extend(status.blockers)
    else:
        print("- PASS repeatable migration/seed generation status")

    for path in CRITICAL:
        ast.parse(_read(path))
        print(f"- PASS syntax {path}")

    supabase_sql = SUPABASE_SQL.read_text(encoding="utf-8")
    seed_sql = IRT_SEED_SQL.read_text(encoding="utf-8")

    forbidden = ["DEBUG:", "INFO [", "CAST(NULL AS JSONB)", "eduboost_app"]
    for token in forbidden:
        if token in supabase_sql:
            failures.append(f"Supabase SQL still contains forbidden token: {token}")

    if seed_sql.count("INSERT INTO public.irt_items") != EXPECTED_IRT_ROWS:
        failures.append("IRT seed SQL insert count does not match expected row count")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/unit/test_db_migration_seed_repeatability.py",
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
            failures.append("DB repeatability unit tests failed")

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
        print("- PASS focused Ruff DB repeatability check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS DB migration + seed repeatability check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
