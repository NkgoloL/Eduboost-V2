from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.staging_acceptance_evidence import REQUIRED_FIELDS, build_status, write_status, write_template


ROOT = Path(__file__).resolve().parents[2]


def test_staging_acceptance_template_contains_required_fields():
    write_template()
    text = (ROOT / "docs/release/staging_smoke_evidence.md").read_text(encoding="utf-8")

    for field in REQUIRED_FIELDS:
        assert f"**{field}:**" in text


def test_staging_acceptance_status_remains_blocked_with_pending_template():
    write_template()
    status = build_status()

    assert status.status in {"external-blocked", "staging-accepted"}
    if any(not field.valid for field in status.fields):
        assert status.status == "external-blocked"


def test_staging_acceptance_status_writes_reports():
    status = write_status()

    assert (ROOT / "docs/release/staging_acceptance_status.json").exists()
    assert (ROOT / "docs/release/staging_acceptance_status.md").exists()
    assert status.evidence_file == "docs/release/staging_smoke_evidence.md"


def test_staging_acceptance_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    subprocess.run(
        [sys.executable, "scripts/patch_staging_acceptance_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    result = subprocess.run(
        [sys.executable, "scripts/check_staging_acceptance.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_staging_acceptance_release_mode_fails_when_pending():
    status = build_status()
    if status.status == "staging-accepted":
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_staging_acceptance.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires accepted staging evidence" in result.stdout


def test_makefile_contains_staging_acceptance_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "staging-acceptance-status:" in source
    assert "staging-acceptance-local-check:" in source
    assert "backend-implementation-1911-1950-full-check:" in source
