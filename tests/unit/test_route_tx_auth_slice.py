from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.route_tx_auth_slice import TARGET_ROUTES, build_report, live_db_status, write_report


ROOT = Path(__file__).resolve().parents[2]


def test_auth_route_slice_tracks_register_and_dev_session():
    assert TARGET_ROUTES["register"] == "auth_service.register"
    assert TARGET_ROUTES["create_dev_session"] == "auth_service.create_dev_session"


def test_auth_route_slice_builds_report():
    report = build_report()

    assert report.route_file == "app/api_v2_routers/auth.py"
    assert report.findings
    assert report.local_status in {"route-auth-delegation-passing", "route-auth-delegation-not-proven"}


def test_auth_route_slice_has_no_direct_db_mutations_when_local_passing():
    report = build_report()

    if report.local_status == "route-auth-delegation-passing":
        for finding in report.findings:
            assert finding.direct_db_mutations == []
            assert finding.delegate_found is True
            assert finding.auth_service_dependency_found is True


def test_auth_route_slice_live_db_is_separate_from_local_delegation():
    status, blockers = live_db_status()

    assert status in {"external-blocked", "live-db-proof-accepted"}
    if blockers:
        assert status == "external-blocked"


def test_auth_route_slice_writes_reports():
    report = write_report()

    assert (ROOT / "docs/release/auth_route_transaction_slice_report.json").exists()
    assert (ROOT / "docs/release/auth_route_transaction_slice_report.md").exists()
    assert (ROOT / "docs/release/auth_route_transaction_live_db_evidence.md").exists()
    assert report.no_false_closure_rules


def test_route_tx_auth_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_route_tx_auth_slice_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_route_tx_auth_slice_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_route_tx_auth_slice.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_route_tx_auth_slice_release_mode_fails_without_live_db_evidence():
    status, _ = live_db_status()
    if status == "live-db-proof-accepted":
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_route_tx_auth_slice.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires live DB auth route transaction evidence" in result.stdout


def test_makefile_contains_route_tx_auth_slice_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "route-tx-auth-slice-report:" in source
    assert "route-tx-auth-slice-check:" in source
    assert "backend-implementation-2071-2110-full-check:" in source
