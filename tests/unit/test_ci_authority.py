from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.ci_authority import REQUIRED_LOCAL_TARGETS, build_status, write_ci_evidence_template, write_status


ROOT = Path(__file__).resolve().parents[2]


def test_ci_authority_tracks_required_local_targets():
    assert "backend-implementation-1631-1670-full-check" in REQUIRED_LOCAL_TARGETS
    assert "backend-implementation-1591-1630-full-check" in REQUIRED_LOCAL_TARGETS


def test_ci_authority_writes_evidence_template_without_claiming_remote_success():
    write_ci_evidence_template()

    text = (ROOT / "docs/release/ci_evidence.md").read_text(encoding="utf-8")
    assert "CI-001" in text
    assert "GitHub Actions run URL: `PENDING`" in text
    assert "Local command success is not remote CI authority" in text


def test_ci_authority_status_is_external_blocked_without_run_url():
    status = build_status()

    assert status.ci_status in {"external-blocked", "remote-ci-authoritative"}
    if not status.ci_run_url_present:
        assert status.ci_status == "external-blocked"


def test_ci_authority_writes_status_reports():
    status = write_status()

    assert (ROOT / "docs/release/ci_authority_status.json").exists()
    assert (ROOT / "docs/release/ci_authority_status.md").exists()
    assert status.remaining_blockers or status.ci_run_url_present


def test_ci_authority_checker_runs_in_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_ci_authority.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_ci_authority_release_mode_requires_run_url_when_missing():
    text = (ROOT / "docs/release/ci_evidence.md").read_text(encoding="utf-8") if (ROOT / "docs/release/ci_evidence.md").exists() else ""
    if "https://github.com/" in text and "/actions/runs/" in text:
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_ci_authority.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires real GitHub Actions run URL" in result.stdout
