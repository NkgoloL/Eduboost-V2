from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "diagnostics.py"


@pytest.mark.unit
def test_diagnostics_routes_import_consent_gate_adapter() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_active_consent_for_current_user" in source


@pytest.mark.unit
def test_diagnostic_items_route_calls_read_authz_then_consent_gate() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_learner_read_for_current_user(current_user, learner)" in source
    assert "await require_active_consent_for_current_user(db, current_user, str(learner_id))" in source

    read_index = source.index("require_learner_read_for_current_user(current_user, learner)")
    consent_index = source.index("await require_active_consent_for_current_user(db, current_user, str(learner_id))")
    assert read_index < consent_index


@pytest.mark.unit
def test_diagnostic_submit_route_calls_write_authz_then_consent_gate() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_learner_write_for_current_user(current_user, body.learner_id)" in source
    assert "await require_active_consent_for_current_user(db, current_user, str(body.learner_id))" in source

    write_index = source.index("require_learner_write_for_current_user(current_user, body.learner_id)")
    consent_index = source.index("await require_active_consent_for_current_user(db, current_user, str(body.learner_id))")
    assert write_index < consent_index
