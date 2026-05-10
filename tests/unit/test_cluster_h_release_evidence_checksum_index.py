from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_h_release_evidence_checksum_index import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_cluster_h_release_evidence_checksum_index_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_release_evidence_checksum_index_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_h_release_evidence_checksum_index.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster H release evidence checksum index check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_cluster_h_release_evidence_checksum_index_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "cluster-h-release-evidence-checksum-index-check:" in text
    assert "scripts/check_cluster_h_release_evidence_checksum_index.py" in text
