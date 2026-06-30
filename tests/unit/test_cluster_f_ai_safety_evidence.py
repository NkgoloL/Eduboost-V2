from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_f_ai_safety_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-f-ai-safety.yml"


@pytest.mark.unit
def test_cluster_f_ai_safety_evidence_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_f_ai_safety_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_f_ai_safety_evidence.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster F AI safety evidence check" in result.stdout


@pytest.mark.unit
def test_cluster_f_workflow_runs_ai_safety_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make caps-alignment-contract-check" in text
    assert "make ai-safety-boundary-check" in text
    assert "make cluster-f-ai-safety-check" in text


@pytest.mark.unit
def test_makefile_exposes_cluster_f_ai_safety_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "cluster-f-ai-safety-check:" in text
    assert "scripts/check_cluster_f_ai_safety_evidence.py" in text
