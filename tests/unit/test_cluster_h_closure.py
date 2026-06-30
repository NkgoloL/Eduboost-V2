from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_h_closure import REQUIRED_FILES, run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md"


@pytest.mark.unit
def test_cluster_h_closure_report_exists_and_documents_boundary() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "Cluster H Staging and Beta Release Closure" in text
    assert "make cluster-h-closure-check" in text
    assert "does not authorize unrestricted production launch" in text


@pytest.mark.unit
def test_cluster_h_closure_required_files_are_registered() -> None:
    assert "docs/operations/CLUSTER_H_CLOSURE.md" in REQUIRED_FILES
    assert "docs/operations/beta_release_evidence_bundle.md" in REQUIRED_FILES
    assert ".github/workflows/beta-release-approval.yml" in REQUIRED_FILES


@pytest.mark.unit
def test_cluster_h_closure_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_h_closure_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_h_closure.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster H closure check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_cluster_h_closure_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "cluster-h-closure-check:" in text
    assert "scripts/check_cluster_h_closure.py" in text
