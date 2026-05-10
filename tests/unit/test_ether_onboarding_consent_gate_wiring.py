from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_popia_consent_boundary_matrix import collect_rows


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "ether.py"


@pytest.mark.unit
def test_ether_onboarding_submit_is_authenticated_boundary() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def submit_onboarding", maxsplit=1)[1]

    assert "Depends(get_current_user)" in block
    assert "user.get(\"role\")" in block
    assert "await require_active_consent_for_current_user" not in block


@pytest.mark.unit
def test_ether_onboarding_submit_is_not_learner_scoped() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def submit_onboarding", maxsplit=1)[1]

    assert "response: OnboardingResponse" in block
    assert "learner_id" not in block


@pytest.mark.unit
def test_ether_onboarding_submit_matrix_classification_matches_boundary() -> None:
    rows = collect_rows()
    matches = [
        row
        for row in rows
        if row.router == "ether.py" and row.function == "submit_onboarding"
    ]

    assert matches
    assert {row.decision for row in matches} == {"authenticated_catalog_boundary"}
