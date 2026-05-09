from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_learner_authz_matrix import collect_rows


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "ether.py"


@pytest.mark.unit
def test_ether_onboarding_questions_requires_authenticated_user() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def get_questions", maxsplit=1)[1].split("@router.post", maxsplit=1)[0]

    assert "user: dict = Depends(get_current_user)" in block


@pytest.mark.unit
def test_matrix_recognizes_ether_questions_auth_marker() -> None:
    rows = collect_rows()
    matches = [
        row
        for row in rows
        if row.router == "ether.py"
        and row.method == "GET"
        and row.path == "/onboarding/questions"
    ]

    assert matches
    assert matches[0].authz_marker == "get_current_user"
    assert matches[0].status == "covered"
