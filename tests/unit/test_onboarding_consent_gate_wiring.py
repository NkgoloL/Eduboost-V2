from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "onboarding.py"


@pytest.mark.unit
def test_onboarding_submit_imports_consent_gate() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_active_consent_for_current_user" in source


@pytest.mark.unit
def test_onboarding_submit_authorizes_before_consent_gate() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def submit_onboarding", maxsplit=1)[1]

    assert "require_learner_write_for_current_user(current_user, body.learner_id)" in block
    assert "await require_active_consent_for_current_user(db, current_user, body.learner_id)" in block
    assert block.index("require_learner_write_for_current_user(current_user, body.learner_id)") < block.index(
        "await require_active_consent_for_current_user(db, current_user, body.learner_id)"
    )


@pytest.mark.unit
def test_onboarding_questions_remains_authenticated_catalog_boundary() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def get_onboarding_questions", maxsplit=1)[1].split("@router.post", maxsplit=1)[0]

    assert "Depends(get_current_user)" in block
    assert "require_active_consent_for_current_user" not in block
