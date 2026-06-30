from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_active_consent_route_order import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_active_consent_route_order_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_active_consent_route_order_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_active_consent_route_order.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Active-consent route-order check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_popia_consent_order_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "popia-consent-order-check:" in text
    assert "scripts/check_active_consent_route_order.py" in text


@pytest.mark.unit
def test_active_consent_route_order_doc_contains_evidence_phrase() -> None:
    doc = REPO_ROOT / "docs" / "security" / "active_consent_route_order.md"
    text = doc.read_text(encoding="utf-8")

    assert "object authorization must run before active POPIA consent" in text
