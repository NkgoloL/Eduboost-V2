from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_popia_consent_closure import COMMANDS, run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_popia_consent_closure_command_list_is_complete() -> None:
    flattened = "\n".join(" ".join(command) for _, command in COMMANDS)

    assert "scripts/generate_consent_gate_inventory.py" in flattened
    assert "scripts/generate_popia_consent_boundary_matrix.py" in flattened
    assert "popia-consent-gate-check" in flattened
    assert "audit-contract-check" in flattened
    assert "popia-consent-audit-check" in flattened
    assert "popia-consent-boundary-check" in flattened
    assert "popia-consent-order-check" in flattened
    assert "popia-consent-source-check" in flattened
    assert "popia-consent-rejection-audit-check" in flattened


@pytest.mark.unit
def test_popia_consent_closure_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_popia_consent_closure_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_popia_consent_closure.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "POPIA consent closure check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_popia_consent_closure_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "popia-consent-closure-check:" in text
    assert "scripts/check_popia_consent_closure.py" in text
