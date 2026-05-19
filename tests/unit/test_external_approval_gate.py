from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.external_approval_gate import REQUIRED_APPROVALS, build_status, write_status, write_templates


ROOT = Path(__file__).resolve().parents[2]


def test_external_approval_gate_tracks_all_required_approvals():
    assert {"LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"} == set(REQUIRED_APPROVALS)


def test_external_approval_templates_are_pending_by_default():
    write_templates()
    for meta in REQUIRED_APPROVALS.values():
        path = ROOT / "docs/release/external_approvals" / meta["file"]
        assert path.exists()
        text = path.read_text(encoding="utf-8").lower()
        assert "**decision:** pending" in text
        assert "**approver:** pending" in text


def test_external_approval_status_is_blocked_when_metadata_pending():
    status = build_status()

    assert status.status in {"external-blocked", "external-approvals-complete"}
    if any(not approval.approved for approval in status.approvals):
        assert status.status == "external-blocked"


def test_external_approval_status_writes_reports():
    status = write_status()

    assert (ROOT / "docs/release/external_approval_status.json").exists()
    assert (ROOT / "docs/release/external_approval_status.md").exists()
    assert len(status.approvals) == 4


def test_external_approval_local_checker_runs():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    subprocess.run(
        [sys.executable, "scripts/patch_external_approval_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    result = subprocess.run(
        [sys.executable, "scripts/check_external_approval_gate.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_external_approval_release_checker_fails_when_pending():
    status = build_status()
    if status.status == "external-approvals-complete":
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_external_approval_gate.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires all external approvals to be complete" in result.stdout
