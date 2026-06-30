from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_popia_consent_boundary_matrix import collect_rows


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "onboarding.py"


@pytest.mark.unit
def test_onboarding_submit_is_authenticated_boundary() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def submit_onboarding", maxsplit=1)[1]

    assert "Depends(require_auth_context)" in block
    assert "require_learner_write_for_current_user" in block
    assert "await require_active_consent_for_current_user" in block


@pytest.mark.unit
def test_onboarding_submit_is_learner_scoped_and_consent_gated() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def submit_onboarding", maxsplit=1)[1]

    assert "body: OnboardingSubmit" in block
    assert "body.learner_id" in block
    assert "require_learner_write_for_current_user" in block
    assert "await require_active_consent_for_current_user" in block


@pytest.mark.unit
def test_onboarding_submit_matrix_classification_matches_boundary() -> None:
    rows = collect_rows()
    matches = [
        row
        for row in rows
        if row.router == "onboarding.py" and row.function == "submit_onboarding"
    ]

    assert matches
    assert {row.decision for row in matches} == {"active_consent_required"}
