from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.auth_refresh_db_evidence_gate import build_status, has_placeholder, validate_field, write_status

ROOT = Path(__file__).resolve().parents[2]


def test_auth_refresh_db_evidence_rejects_placeholders():
    for value in ["pending", "https://example.com/proof", "placeholder", "fake-db-proof", "localhost"]:
        assert has_placeholder(value)


def test_auth_refresh_db_evidence_validates_realistic_values():
    assert validate_field("Evidence URL", "https://github.com/NkgoloL/Eduboost-V2/actions/runs/123456789").valid
    assert validate_field("Commit SHA", "abcdef123456").valid
    assert validate_field("Test result", "passed").valid
    assert not validate_field("Test result", "failed").valid


def test_auth_refresh_db_evidence_defaults_external_blocked():
    status = build_status()
    assert status.status in {"auth-refresh-db-evidence-external-blocked", "auth-refresh-db-evidence-accepted"}


def test_auth_refresh_db_evidence_status_writes_reports():
    status = write_status()
    assert (ROOT / "docs/release/auth_refresh_db_evidence_status.json").exists()
    assert (ROOT / "docs/release/auth_refresh_db_evidence_status.md").exists()
    assert status.status in {"auth-refresh-db-evidence-external-blocked", "auth-refresh-db-evidence-accepted"}


def test_auth_refresh_db_evidence_release_check_fails_without_accepted_evidence():
    status = build_status()
    if status.accepted:
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_refresh_db_evidence_gate.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode != 0
    assert "release mode requires accepted auth refresh DB evidence" in result.stdout


def test_auth_refresh_db_evidence_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_refresh_db_evidence_gate.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_makefile_contains_auth_refresh_db_evidence_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-refresh-db-evidence-status:" in source
    assert "auth-refresh-db-evidence-check:" in source
    assert "backend-implementation-2711-2750-full-check:" in source
