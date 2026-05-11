from __future__ import annotations

import pytest

from scripts.generate_popia_consent_boundary_matrix import collect_rows, render


@pytest.mark.unit
def test_popia_consent_boundary_matrix_collects_core_routes() -> None:
    rows = collect_rows()
    lookup = {(row.router, row.function): row for row in rows}

    assert lookup[("lessons.py", "generate_lesson")].decision == "active_consent_required"
    assert lookup[("popia.py", "request_learner_deletion")].decision == "rights_exercise_not_active_consent_blocked"
    assert lookup[("assessments.py", "list_assessments")].decision == "authenticated_catalog_boundary"


@pytest.mark.unit
def test_popia_consent_boundary_matrix_renders_expected_sections() -> None:
    output = render(collect_rows())

    assert "# POPIA Consent Boundary Matrix" in output
    assert "active_consent_required" in output
    assert "rights_exercise_not_active_consent_blocked" in output
    assert "| Router | Method | Route | Function | Decision | Marker |" in output
