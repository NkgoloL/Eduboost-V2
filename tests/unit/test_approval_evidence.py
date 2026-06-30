from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.approval_evidence import (
    APPROVALS,
    ApprovalEvidence,
    blockers_for,
    build_status,
    write_status,
    write_templates,
)


ROOT = Path(__file__).resolve().parents[2]


def test_approval_evidence_tracks_legal_security_content_only():
    assert set(APPROVALS) == {"LEGAL-001", "SEC-001", "CONTENT-001"}


def test_approval_template_text_is_pending_by_default():
    from scripts.approval_evidence import template_for

    for approval_id in APPROVALS:
        text = template_for(approval_id).lower()
        assert "**decision:** pending" in text
        assert "**approver:** pending" in text
        assert "**evidence url:** pending" in text


def test_valid_approval_evidence_has_no_blockers():
    evidence = ApprovalEvidence(
        id="SEC-001",
        title="Security release approval",
        owner="security",
        decision="approved",
        approver="security-owner",
        evidence_url="https://security-proof.internal/security-report",
        date_verified="2026-05-19",
        scope="beta release security review",
        notes="fixture",
        file="docs/release/external_approvals/security_approval.md",
    )

    assert blockers_for(evidence) == []


def test_pending_approval_status_remains_external_blocked():
    write_templates()
    status = build_status()

    assert status.status in {"external-blocked", "approvals-complete"}
    if status.blockers:
        assert status.status == "external-blocked"


def test_approval_evidence_status_writes_reports():
    status = write_status()

    assert (ROOT / "docs/release/approval_evidence_status.json").exists()
    assert (ROOT / "docs/release/approval_evidence_status.md").exists()
    assert len(status.approvals) == 3


def test_patch_approval_evidence_registry_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_approval_evidence_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_approval_evidence_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_approval_evidence.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_approval_evidence_release_mode_fails_when_pending():
    status = build_status()
    if status.status == "approvals-complete":
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_approval_evidence.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires all legal/security/content approvals complete" in result.stdout


def test_makefile_contains_approval_evidence_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "approval-evidence-status:" in source
    assert "approval-evidence-local-check:" in source
    assert "backend-implementation-1991-2030-full-check:" in source
