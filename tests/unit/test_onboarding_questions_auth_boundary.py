"""Tests for onboarding questions authentication boundary."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.api_v2_routers import onboarding as onboarding_router

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_onboarding_questions_requires_authenticated_user_dependency() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "onboarding.py").read_text(encoding="utf-8")
    block = source.split("async def get_onboarding_questions", maxsplit=1)[1].split("@router.post", maxsplit=1)[0]

    assert "current_user: AuthContext = Depends(require_auth_context)" in block


class FakeEther:
    def get_onboarding_questions(self):
        return [{"id": "q1", "prompt": "Pick one"}]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_questions_returns_catalog_for_authenticated_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(onboarding_router, "_ether", FakeEther())

    result = await onboarding_router.get_onboarding_questions(current_user={"sub": "user-1", "role": "student"})

    assert result == [{"id": "q1", "prompt": "Pick one"}]
