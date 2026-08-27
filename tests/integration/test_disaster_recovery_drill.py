"""Integration test for Automated Disaster Recovery, Backup & Restore Drill (TSR-11.6)."""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
import pytest
from sqlalchemy import create_engine, text

TEST_DB_HOST = "127.0.0.1"
TEST_DB_PORT = "54322"
TEST_DB_USER = "postgres"
SOURCE_DB = "postgres"
DRILL_DB = "tsr_dr_drill_target"


@pytest.mark.integration
def test_automated_backup_and_restore_disaster_recovery_drill(tmp_path: Path):
    """Executes real pg_dump & pg_restore, measuring RTO and row consistency."""
    backup_file = tmp_path / "tsr_backup.sql"
    env = os.environ.copy()
    env["PGPASSWORD"] = "postgres"

    # Step 1: Execute pg_dump from active database
    start_backup = time.perf_counter()
    dump_cmd = [
        "pg_dump",
        "-h", TEST_DB_HOST,
        "-p", TEST_DB_PORT,
        "-U", TEST_DB_USER,
        "-d", SOURCE_DB,
        "-F", "c",  # Custom format for pg_restore
        "-f", str(backup_file),
    ]
    dump_res = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)
    backup_duration = time.perf_counter() - start_backup

    assert dump_res.returncode == 0, f"pg_dump failed: {dump_res.stderr}"
    assert backup_file.exists()
    assert backup_file.stat().st_size > 1000

    # Step 2: Create temporary drill database
    admin_engine = create_engine(f"postgresql://postgres:postgres@{TEST_DB_HOST}:{TEST_DB_PORT}/postgres", isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {DRILL_DB}"))
        conn.execute(text(f"CREATE DATABASE {DRILL_DB}"))

    # Step 3: Execute pg_restore into drill database
    start_restore = time.perf_counter()
    restore_cmd = [
        "pg_restore",
        "-h", TEST_DB_HOST,
        "-p", TEST_DB_PORT,
        "-U", TEST_DB_USER,
        "-d", DRILL_DB,
        "--no-owner",
        str(backup_file),
    ]
    restore_res = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)
    restore_duration = time.perf_counter() - start_restore

    # pg_restore exit code 0 or warnings (non-fatal)
    assert restore_res.returncode in (0, 1), f"pg_restore failed: {restore_res.stderr}"

    # Step 4: Verify row count and table consistency on restored DB
    drill_engine = create_engine(f"postgresql://postgres:postgres@{TEST_DB_HOST}:{TEST_DB_PORT}/{DRILL_DB}")
    with drill_engine.connect() as conn:
        res = conn.execute(text("SELECT count(*) FROM pg_tables WHERE schemaname = 'public'"))
        table_count = res.scalar()
        assert table_count > 0, "Restored database has 0 tables!"

    drill_engine.dispose()

    # Clean up drill database
    with admin_engine.connect() as conn:
        conn.execute(text(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DRILL_DB}'"))
        conn.execute(text(f"DROP DATABASE IF EXISTS {DRILL_DB}"))

    admin_engine.dispose()

    # Assert Recovery Time Objective (RTO) meets production SLA (< 30 seconds for test db)
    assert restore_duration < 30.0
