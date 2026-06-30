from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs" / "security" / "POPIA_CONSENT_GATE_CLOSURE.md"


@pytest.mark.unit
def test_cluster_c_closure_stamp_exists() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "## Cluster C Closure Stamp" in text
    assert "make popia-consent-closure-check" in text
    assert "make popia-consent-source-check" in text
    assert "make popia-consent-rejection-audit-check" in text


@pytest.mark.unit
def test_cluster_c_closure_stamp_links_core_artifacts() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "docs/security/popia_consent_gate_inventory.md" in text
    assert "docs/security/popia_consent_boundary_matrix.md" in text
    assert "docs/security/popia_consent_closure_check.md" in text
    assert "docs/security/popia_consent_closure_ci.md" in text
