from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "parents.py"


@pytest.mark.unit
def test_parent_routes_import_central_consent_adapter() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_active_consent_for_current_user" in source


@pytest.mark.unit
def test_parent_dashboard_routes_use_central_consent_adapter_after_read_authz() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_learner_read_for_current_user(current_user, learner)" in source
    assert "await require_active_consent_for_current_user(db, current_user, learner.id)" in source
    assert "await consent_service.require_active_consent" not in source


@pytest.mark.unit
def test_parent_progress_route_uses_central_consent_adapter_after_read_authz() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def get_learner_progress", maxsplit=1)[1].split("@router.delete", maxsplit=1)[0]

    assert "require_learner_read_for_current_user(current_user, learner)" in block
    assert "await require_active_consent_for_current_user(db, current_user, learner_id)" in block
    assert block.index("require_learner_read_for_current_user(current_user, learner)") < block.index(
        "await require_active_consent_for_current_user(db, current_user, learner_id)"
    )


@pytest.mark.unit
def test_parent_erasure_still_uses_consent_service_workflow() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def request_erasure", maxsplit=1)[1]

    assert "consent_service = ConsentService(db)" in block
    assert "await consent_service.execute_erasure" in block
