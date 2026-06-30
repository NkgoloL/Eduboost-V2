from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_beta_release_evidence_bundle import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_beta_release_evidence_bundle_generation_and_check_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_beta_release_evidence_bundle.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_beta_release_evidence_bundle_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_beta_release_evidence_bundle.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Beta release evidence bundle check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_beta_release_evidence_bundle_targets() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "beta-release-evidence-bundle:" in text
    assert "beta-release-evidence-bundle-check:" in text
