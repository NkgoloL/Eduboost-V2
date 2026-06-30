from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_consent_gate_inventory import ALLOWLIST_PATH, load_allowlist, missing_rows, row_key


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_consent_gate_allowlist_exists_and_covers_current_missing_rows() -> None:
    assert ALLOWLIST_PATH.exists()

    allowed = load_allowlist()
    missing = missing_rows()

    assert allowed
    assert {row_key(row) for row in missing}.issubset(allowed)


@pytest.mark.unit
def test_consent_gate_check_cli_passes_current_baseline() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_consent_gate_inventory.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "POPIA consent-gate inventory check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_popia_consent_gate_check_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "popia-consent-gate-check:" in text
    assert "scripts/generate_consent_gate_inventory.py" in text
    assert "scripts/check_consent_gate_inventory.py" in text


@pytest.mark.unit
def test_lesson_generation_routes_removed_from_consent_allowlist_after_wiring() -> None:
    allowed = load_allowlist()

    assert "app/api_v2_routers/lessons.py::generate_lesson" not in allowed
    assert "app/api_v2_routers/lessons.py::generate_lesson_stream" not in allowed
