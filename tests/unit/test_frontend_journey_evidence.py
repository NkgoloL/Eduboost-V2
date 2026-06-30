from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_frontend_journey_evidence import REQUIRED, check_all

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_frontend_journey_required_files_cover_api_and_journeys() -> None:
    assert "app/frontend/src/lib/api/client.ts" in REQUIRED
    assert "docs/frontend/learner_vertical_journey_contract.md" in REQUIRED
    assert "tests/fixtures/frontend/parent_journey_fixture.json" in REQUIRED


@pytest.mark.unit
def test_frontend_journey_evidence_passes() -> None:
    assert [r for r in check_all() if not r.ok] == []


@pytest.mark.unit
def test_frontend_journey_cli_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/check_frontend_journey_evidence.py"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
