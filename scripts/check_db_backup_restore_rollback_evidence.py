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

from scripts.db_backup_restore_rollback_evidence import ACCEPTED, write_status  # noqa: E402

CRITICAL = [
    "scripts/db_backup_restore_rollback_evidence.py",
    "scripts/patch_db_backup_restore_rollback_registry.py",
    "scripts/check_db_backup_restore_rollback_evidence.py",
    "tests/unit/test_db_backup_restore_rollback_evidence.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def entry(text: str, item_id: str) -> str:
    match = re.search(rf"(?ms)(^  - id: {re.escape(item_id)}\n.*?)(?=^  - id: |\Z)", text)
    if not match:
        raise AssertionError(f"missing registry entry {item_id}")
    return match.group(1)


def main() -> int:
    failures: list[str] = []
    run_drill = os.getenv("DB_ROLLBACK_RUN_DRILL") == "1" or os.getenv("DB_ROLLBACK_ACCEPT") == "1"
    status = write_status(run_drill=run_drill)

    print("DB backup/restore/rollback evidence check")
    print(f"- INFO status: {status['status']}")
    print(f"- INFO dump_sha256: {status['dump_sha256']}")
    print(f"- INFO source table count: {status['source_table_count']}")
    print(f"- INFO restore table count: {status['restore_table_count']}")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if os.getenv("DB_ROLLBACK_ACCEPT") == "1":
        if status["status"] != ACCEPTED:
            failures.extend(status["blockers"])
        else:
            registry = ROOT / "docs/release/evidence_status_registry.yml"
            if registry.exists():
                text = registry.read_text(encoding="utf-8")
                for item_id in ["DB-ROLLBACK-001", "DB-ROLLBACK-001R"]:
                    current = entry(text, item_id)
                    for required in [
                        "proof_status: runtime-passing",
                        "closure_blocker: none",
                        "release_ready: true",
                        "blocks_beta: false",
                    ]:
                        if required not in current:
                            failures.append(f"{item_id} missing {required}")
    else:
        print("- INFO acceptance not requested; tooling check only")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_db_backup_restore_rollback_evidence.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append("DB backup/restore/rollback unit tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff DB backup/restore/rollback check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("- PASS DB backup/restore/rollback evidence tooling check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
