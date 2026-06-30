from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.auth_refresh_db_evidence_gate import build_status, has_placeholder, validate_field, write_status

ROOT = Path(__file__).resolve().parents[2]


def test_auth_refresh_db_evidence_rejects_real_symbolic_placeholders():
    values = [
        "REAL_RUN_ID",
        "https://github.com/NkgoloL/Eduboost-V2/actions/runs/REAL_RUN_ID",
        "$REAL_AUTH_REFRESH_DB_PROOF_DSN",
        "${REAL_AUTH_REFRESH_DB_PROOF_DSN}",
        "AUTH_REFRESH_DB_PROOF_DSN=...",
        "YYYY-MM-DD",
        "<sha>",
        "<name>",
        "[redacted]",
    ]
    for value in values:
        assert has_placeholder(value), value


def test_auth_refresh_db_evidence_rejects_placeholder_command():
    field = validate_field(
        "Test command",
        'AUTH_REFRESH_DB_PROOF_DSN="$REAL_AUTH_REFRESH_DB_PROOF_DSN" make auth-refresh-db-proof-release-check',
    )
    assert not field.valid


def test_auth_refresh_db_evidence_rejects_non_concrete_run_url():
    field = validate_field("Evidence URL", "https://github.com/NkgoloL/Eduboost-V2/actions/runs/REAL_RUN_ID")
    assert not field.valid


def test_auth_refresh_db_evidence_accepts_concrete_run_url_shape():
    field = validate_field("Evidence URL", "https://github.com/NkgoloL/Eduboost-V2/actions/runs/123456789")
    assert field.valid


def test_existing_placeholder_attachment_is_reclassified_external_blocked_if_present():
    status = build_status()
    if any("REAL_RUN_ID" in field.value or "$REAL_" in field.value for field in status.fields):
        assert status.status == "auth-refresh-db-evidence-external-blocked"
        assert not status.accepted


def test_auth_refresh_db_evidence_placeholder_repair_writes_reports():
    status = write_status()
    assert (ROOT / "docs/release/auth_refresh_db_evidence_status.json").exists()
    assert (ROOT / "docs/release/auth_refresh_db_evidence_status.md").exists()
    assert status.status in {"auth-refresh-db-evidence-external-blocked", "auth-refresh-db-evidence-accepted"}


def test_placeholder_repair_check_runs_local_mode():
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
