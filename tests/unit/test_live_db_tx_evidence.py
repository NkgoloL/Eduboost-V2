from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.live_db_tx_evidence import (
    SLICES,
    LiveDBEvidence,
    blockers_for,
    build_status,
    write_status,
    write_templates,
)


ROOT = Path(__file__).resolve().parents[2]


def test_live_db_tx_evidence_tracks_all_route_slices():
    assert set(SLICES) == {"auth", "popia", "diagnostics"}


def test_live_db_tx_evidence_templates_exist():
    write_templates()

    for meta in SLICES.values():
        text = (ROOT / meta["evidence_file"]).read_text(encoding="utf-8")
        assert "**Live DB evidence URL:**" in text
        assert "**Test result:**" in text
        assert "**Database:**" in text


def test_valid_live_db_evidence_has_no_blockers():
    evidence = LiveDBEvidence(
        slice="auth",
        item="ROUTE-TX-AUTH-001",
        route_slice="auth",
        live_db_evidence_url="https://example.com/live-db-auth-proof",
        test_result="passed",
        database="postgresql://staging",
        commit_sha="abcdef1",
        verified_by="release-owner",
        date_verified="2026-05-19",
        notes="fixture",
        evidence_file="docs/release/auth_route_transaction_live_db_evidence.md",
    )

    assert blockers_for(evidence) == []


def test_pending_live_db_evidence_status_is_external_blocked():
    write_templates()
    status = build_status()

    assert status.status in {"external-blocked", "live-db-evidence-complete"}
    if status.blockers:
        assert status.status == "external-blocked"


def test_live_db_tx_evidence_status_writes_reports():
    status = write_status()

    assert (ROOT / "docs/release/live_db_transaction_evidence_status.json").exists()
    assert (ROOT / "docs/release/live_db_transaction_evidence_status.md").exists()
    assert len(status.records) == 3


def test_live_db_tx_evidence_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_live_db_tx_evidence_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_live_db_tx_evidence_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_live_db_tx_evidence.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_live_db_tx_evidence_release_mode_fails_when_pending():
    status = build_status()
    if status.status == "live-db-evidence-complete":
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_live_db_tx_evidence.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires complete live DB transaction evidence" in result.stdout


def test_makefile_contains_live_db_tx_evidence_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "live-db-tx-evidence-status:" in source
    assert "live-db-tx-evidence-local-check:" in source
    assert "backend-implementation-2231-2270-full-check:" in source
