from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_observability_ops_evidence import REQUIRED, check_all

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_observability_required_files_cover_metrics_alerts_and_support() -> None:
    assert "app/core/metrics.py" in REQUIRED
    assert "prometheus/alerts.yml" in REQUIRED
    assert "docs/operations/support_model.md" in REQUIRED


@pytest.mark.unit
def test_observability_ops_evidence_passes() -> None:
    assert [r for r in check_all() if not r.ok] == []


@pytest.mark.unit
def test_observability_ops_cli_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/check_observability_ops_evidence.py"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
