"""Tests for onboarding submit authorization wiring."""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from types import SimpleNamespace
import uuid

import pytest
from fastapi import HTTPException

from app.api_v2_routers import onboarding as onboarding_router
from app.api_v2_deps.auth import AuthContext, TokenType
from app.models import UserRole

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_onboarding_submit_uses_phase2_write_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "onboarding.py").read_text(encoding="utf-8")
    block = source.split("async def submit_onboarding", maxsplit=1)[1]
    assert "current_user: AuthContext = Depends(require_auth_context)" in block
    assert "require_learner_write_for_current_user(current_user, body.learner_id)" in block
    assert block.index("require_learner_write_for_current_user") < block.index("answers_raw =")


class FakeArchetype(Enum):
    EXPLORER = "explorer"


class FakeLearnerService:
    def __init__(self, db):
        self.db = db

    async def get_learner_summary(self, learner_id: str):
        if learner_id == "missing-learner":
            return None
        return SimpleNamespace(id=learner_id, guardian_id="guardian-1")

    async def process_onboarding(self, learner_id: str, answers: list):
        return {
            "learner_id": learner_id,
            "archetype": "explorer",
            "description": "Explorer profile",
            "probabilities": {"explorer": 1.0},
        }


@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_submit_allows_authorized_guardian(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(onboarding_router, "LearnerService", FakeLearnerService)

    async def allow_consent(*args, **kwargs):
        return None

    monkeypatch.setattr(onboarding_router, "require_active_consent_for_current_user", allow_consent)

    body = SimpleNamespace(
        learner_id="learner-1",
        answers=[SimpleNamespace(question_id="q1", answer="a1")],
    )

    auth = AuthContext(
        user_id="guardian-1",
        guardian_id="guardian-1",
        roles=[UserRole.PARENT],
        token_type=TokenType.ACCESS,
        raw_claims={"role": "parent", "guardian_learner_ids": ["learner-1"]},
        jti=str(uuid.uuid4()),
    )

    result = await onboarding_router.submit_onboarding(
        body,
        db=object(),
        current_user=auth,
    )

    assert result.learner_id == "learner-1"
    assert result.archetype == "explorer"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_submit_rejects_unrelated_guardian(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(onboarding_router, "LearnerService", FakeLearnerService)

    body = SimpleNamespace(
        learner_id="learner-1",
        answers=[SimpleNamespace(question_id="q1", answer="a1")],
    )

    auth = AuthContext(
        user_id="guardian-2",
        guardian_id="guardian-2",
        roles=[UserRole.PARENT],
        token_type=TokenType.ACCESS,
        raw_claims={"role": "parent", "guardian_learner_ids": ["learner-2"]},
        jti=str(uuid.uuid4()),
    )

    with pytest.raises(HTTPException) as exc_info:
        await onboarding_router.submit_onboarding(
            body,
            db=object(),
            current_user=auth,
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_submit_preserves_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(onboarding_router, "LearnerService", FakeLearnerService)

    body = SimpleNamespace(learner_id="missing-learner", answers=[])

    auth = AuthContext(
        user_id="admin-1",
        roles=[UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={"role": "admin"},
        jti=str(uuid.uuid4()),
    )

    with pytest.raises(HTTPException) as exc_info:
        await onboarding_router.submit_onboarding(
            body,
            db=object(),
            current_user=auth,
        )

    assert exc_info.value.status_code == 404
