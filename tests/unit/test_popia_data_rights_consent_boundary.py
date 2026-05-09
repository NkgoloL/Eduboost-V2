from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "popia.py"


@pytest.mark.unit
def test_popia_router_imports_central_consent_adapter() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_active_consent_for_current_user" in source


@pytest.mark.unit
def test_data_export_requires_read_authz_then_active_consent() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def export_learner_data", maxsplit=1)[1].split("@router.post", maxsplit=1)[0]

    assert "require_learner_read_for_current_user(current_user, learner)" in block
    assert "await require_active_consent_for_current_user(db, current_user, learner_id)" in block
    assert block.index("require_learner_read_for_current_user(current_user, learner)") < block.index(
        "await require_active_consent_for_current_user(db, current_user, learner_id)"
    )


@pytest.mark.unit
def test_dsr_mutation_routes_remain_object_authorized_not_active_consent_blocked() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    for marker in (
        "async def request_learner_deletion",
        "async def cancel_learner_deletion",
        "async def request_correction",
        "async def request_processing_restriction",
        "async def get_deletion_status",
    ):
        assert marker in source

    # These endpoints are data-subject rights workflows. They must remain
    # object-authorized but must not be blocked by requiring active consent.
    dsr_section = source.split("async def request_learner_deletion", maxsplit=1)[1].split("@router.post(\"/rlhf-export", maxsplit=1)[0]
    assert "require_learner_write_for_current_user" in dsr_section
    assert "require_learner_read_for_current_user" in dsr_section
    assert "await require_active_consent_for_current_user" not in dsr_section
