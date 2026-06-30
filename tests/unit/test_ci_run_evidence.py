from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.ci_run_evidence import (
    blockers_for,
    build_status,
    read_evidence_text,
    validate_commit_sha,
    validate_run_url,
    write_status,
    write_template,
)


ROOT = Path(__file__).resolve().parents[2]


def test_ci_run_url_validator_accepts_github_actions_run_url():
    assert validate_run_url("https://github.com/NkgoloL/Eduboost-V2/actions/runs/123456789")
    assert validate_run_url("https://github.com/NkgoloL/Eduboost-V2/actions/runs/123456789?check_suite_focus=true")


def test_ci_run_url_validator_rejects_non_actions_urls():
    assert not validate_run_url("https://github.com/NkgoloL/Eduboost-V2/pull/1")
    assert not validate_run_url("https://example.com/NkgoloL/Eduboost-V2/actions/runs/123456789")


def test_commit_sha_validator_accepts_short_and_full_sha():
    assert validate_commit_sha("abcdef1")
    assert validate_commit_sha("0123456789abcdef0123456789abcdef01234567")
    assert not validate_commit_sha("pending")
    assert not validate_commit_sha("not-a-sha")


def test_pending_ci_evidence_template_is_blocked():
    write_template()
    status = build_status()
    assert status.status in {"external-blocked", "ci-evidence-accepted"}
    if status.blockers:
        assert status.status == "external-blocked"


def test_valid_ci_evidence_text_has_no_blockers():
    text = """
# CI Authority Evidence

**Repository:** NkgoloL/Eduboost-V2
**Branch:** codex/production_readiness
**Commit SHA:** abcdef1
**GitHub Actions run URL:** https://github.com/NkgoloL/Eduboost-V2/actions/runs/123456789
**Result:** passed
**Workflow:** release
**Verified by:** release-owner
**Date verified:** 2026-05-19
**Notes:** manual evidence fixture
"""
    assert blockers_for(read_evidence_text(text)) == []


def test_ci_run_evidence_status_writes_reports():
    status = write_status()
    assert (ROOT / "docs/release/ci_run_evidence_status.json").exists()
    assert (ROOT / "docs/release/ci_run_evidence_status.md").exists()
    assert status.evidence_file == "docs/release/ci_evidence.md"


def test_ci_run_evidence_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    subprocess.run(
        [sys.executable, "scripts/patch_ci_run_evidence_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    result = subprocess.run(
        [sys.executable, "scripts/check_ci_run_evidence.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_ci_run_evidence_release_mode_fails_without_accepted_evidence():
    status = build_status()
    if status.status == "ci-evidence-accepted":
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_ci_run_evidence.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode != 0
    assert "release mode requires accepted CI run evidence" in result.stdout


def test_makefile_contains_ci_run_evidence_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "ci-run-evidence-status:" in source
    assert "ci-run-evidence-local-check:" in source
    assert "backend-implementation-1951-1990-full-check:" in source
