from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_accessibility_pwa_e2e_evidence import REQUIRED, check_all

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_accessibility_pwa_required_files_cover_a11y_offline_and_e2e() -> None:
    assert "app/frontend/public/service-worker.js" in REQUIRED
    assert "docs/frontend/frontend_accessibility_contract.md" in REQUIRED
    assert "tests/e2e/learner-vertical-journey.spec.ts" in REQUIRED


@pytest.mark.unit
def test_accessibility_pwa_e2e_evidence_passes() -> None:
    assert [r for r in check_all() if not r.ok] == []


@pytest.mark.unit
def test_accessibility_pwa_e2e_cli_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/check_accessibility_pwa_e2e_evidence.py"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
