from __future__ import annotations

import pytest

from scripts.generate_consent_gate_inventory import collect_rows, render


@pytest.mark.unit
def test_consent_gate_inventory_collects_rows() -> None:
    rows = collect_rows()

    assert rows
    assert any(row.path.endswith("consent.py") for row in rows)
    assert any("ConsentService" in row.marker for row in rows)


@pytest.mark.unit
def test_consent_gate_inventory_renders_summary() -> None:
    output = render(collect_rows())

    assert "# POPIA Consent Gate Inventory" in output
    assert "Candidate Missing Consent Gates" in output or "Learner-related functions without local consent marker" in output
    assert "| File | Function | Learner-related | Marker | Status |" in output
