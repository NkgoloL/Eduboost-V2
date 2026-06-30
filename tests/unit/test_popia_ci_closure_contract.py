from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "popia-consent-audit.yml"


@pytest.mark.unit
def test_popia_ci_includes_boundary_order_and_rejection_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make audit-contract-check" in text
    assert "make popia-consent-gate-check" in text
    assert "make popia-consent-boundary-check" in text
    assert "make popia-consent-order-check" in text
    assert "make popia-consent-rejection-audit-check" in text


@pytest.mark.unit
def test_popia_ci_includes_closure_tests() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "tests/unit/test_generate_popia_consent_boundary_matrix.py" in text
    assert "tests/unit/test_popia_consent_boundary_matrix_check.py" in text
    assert "tests/unit/test_popia_consent_gate_closure_report.py" in text
    assert "tests/unit/test_active_consent_route_order.py" in text
    assert "tests/unit/test_consent_rejection_audit_check.py" in text
