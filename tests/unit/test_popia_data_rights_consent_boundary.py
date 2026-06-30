from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "services" / "popia_service.py"


@pytest.mark.unit
def test_popia_service_uses_central_consent_adapter() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "await self.consent.require_active_consent" in source


@pytest.mark.unit
def test_data_export_requires_read_authz_then_active_consent() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def build_learner_export", maxsplit=1)[1].split("async def request_erasure", maxsplit=1)[0]

    assert "self.load_learner_for_read(learner_id, current_user)" in block
    assert "await self.consent.require_active_consent(learner_id, actor_id=requester_id)" in block
    assert block.index("self.load_learner_for_read(learner_id, current_user)") < block.index(
        "await self.consent.require_active_consent(learner_id, actor_id=requester_id)"
    )


@pytest.mark.unit
def test_dsr_mutation_routes_remain_object_authorized_not_active_consent_blocked() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    for marker in (
        "async def request_erasure",
        "async def cancel_erasure",
        "async def request_correction",
        "async def restrict_processing",
    ):
        assert marker in source

    # These endpoints are data-subject rights workflows. They must remain
    # object-authorized but must not be blocked by requiring active consent.
    dsr_section = source.split("async def request_erasure", maxsplit=1)[1]
    assert "self.load_learner_for_write" in dsr_section
    assert "self.consent.require_active_consent" not in dsr_section
