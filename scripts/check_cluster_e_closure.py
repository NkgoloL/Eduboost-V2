#!/usr/bin/env python3
"""Run the full Cluster E data-resilience closure suite."""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

COMMANDS = (
    ("production restore approval", ["make", "production-restore-approval-check"]),
    ("database resilience env matrix", ["make", "database-resilience-env-matrix-check"]),
    ("database backup contract", ["make", "database-backup-contract-check"]),
    ("database restore drill docs", ["make", "database-restore-drill-docs-check"]),
    ("database backup dry-run", ["make", "database-backup-dry-run"]),
    ("database restore dry-run", ["make", "database-restore-dry-run"]),
    ("database backup manifest", ["make", "database-backup-manifest"]),
    ("database restore evidence", ["make", "database-restore-evidence"]),
    ("database backup integrity", ["make", "database-backup-integrity-check"]),
    ("database restore integrity", ["make", "database-restore-integrity-check"]),
    ("cluster e data resilience evidence", ["make", "cluster-e-data-resilience-check"]),
    (
        "cluster e unit tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_database_backup_contract.py",
            "tests/unit/test_database_restore_drill_docs.py",
            "tests/unit/test_database_backup_command.py",
            "tests/unit/test_database_restore_command.py",
            "tests/unit/test_generate_database_backup_manifest.py",
            "tests/unit/test_generate_database_restore_evidence.py",
            "tests/unit/test_database_backup_integrity.py",
            "tests/unit/test_database_restore_integrity.py",
            "tests/unit/test_cluster_e_data_resilience_evidence.py",
            "tests/unit/test_cluster_e_backup_restore_commands_evidence.py",
            "tests/unit/test_cluster_e_backup_restore_evidence_records.py",
            "tests/unit/test_cluster_e_integrity_evidence.py",
            "-q",
            "--no-cov",
        ],
    ),
)


@dataclass(frozen=True)
class ClusterEClosureResult:
    name: str
    ok: bool
    returncode: int
    output: str


def run_command(name: str, command: list[str]) -> ClusterEClosureResult:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return ClusterEClosureResult(
        name=name,
        ok=result.returncode == 0,
        returncode=result.returncode,
        output=(result.stdout + result.stderr).strip(),
    )


def run_checks() -> list[ClusterEClosureResult]:
    return [run_command(name, command) for name, command in COMMANDS]


def main() -> int:
    results = run_checks()
    print("Cluster E closure check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.name}: exit {result.returncode}")
        if not result.ok and result.output:
            print(result.output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
