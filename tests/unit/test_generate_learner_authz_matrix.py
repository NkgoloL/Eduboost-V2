from __future__ import annotations

import pytest

from scripts.generate_learner_authz_matrix import collect_rows, render


@pytest.mark.unit
def test_learner_authz_matrix_collects_routes() -> None:
    rows = collect_rows()

    assert rows
    assert any(row.router == "learners.py" for row in rows)
    assert any(row.learner_scoped for row in rows)


@pytest.mark.unit
def test_learner_authz_matrix_renders_summary() -> None:
    rows = collect_rows()
    rendered = render(rows)

    assert "# Learner Authorization Coverage Matrix" in rendered
    assert "Missing learner authorization markers" in rendered
    assert "| Router | Method | Path | Function | Learner-scoped | Marker | Status |" in rendered
