from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "diagnostics.py"


@pytest.mark.unit
def test_diagnostics_routes_do_not_bypass_central_consent_adapter() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_active_consent_for_current_user" in source
    assert "ConsentService(db).require_active_consent" not in source
    assert "from app.services.consent import ConsentService" not in source


@pytest.mark.unit
def test_diagnostics_item_and_submit_routes_still_call_central_consent_adapter() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    items_block = source.split("async def get_diagnostic_items", maxsplit=1)[1].split("@router.post", maxsplit=1)[0]
    submit_block = source.split("async def submit_diagnostic", maxsplit=1)[1]

    assert "await require_active_consent_for_current_user(db, current_user, str(learner_id))" in items_block
    assert "await require_active_consent_for_current_user(db, current_user, str(body.learner_id))" in submit_block
