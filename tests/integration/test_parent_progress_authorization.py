from __future__ import annotations

"""Direct-call authorization tests for parent learner-progress access."""

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException

from app.api_v2_deps.auth import AuthContext, TokenType
from app.api_v2_routers import parents as parents_router
from app.models import UserRole

pytestmark = pytest.mark.integration


class FakeScalarResult:
    def __init__(self, rows: list[tuple]) -> None:
        self._rows = rows

    def all(self) -> list[tuple]:
        return self._rows


class FakeExecuteResult:
    def __init__(self, rows: list[tuple]) -> None:
        self._rows = rows

    def all(self) -> list[tuple]:
        return self._rows

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self._rows)


class FakeDB:
    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, statement) -> FakeExecuteResult:
        self.calls += 1
        if self.calls == 1:
            return FakeExecuteResult([(datetime(2026, 1, 1, tzinfo=UTC), "MATH")])
        return FakeExecuteResult([("MATH", False), ("ENG", True)])

    async def commit(self) -> None:
        return None

    def expire_all(self) -> None:
        return None


class FakeLearnerRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_by_id(self, learner_id: str) -> SimpleNamespace | None:
        if learner_id == "missing-learner":
            return None
        return SimpleNamespace(
            id=learner_id,
            guardian_id="guardian-1",
            pseudonym_id=f"pseudo-{learner_id}",
            display_name="Pilot Learner",
            grade=4,
            archetype=None,
            theta=0.4,
        )


class FakeConsentService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def require_active_consent(self, learner_id: str, actor_id: str | None = None) -> None:
        return None


def _auth_context(payload: dict[str, Any]) -> AuthContext:
    return AuthContext(
        user_id=payload["sub"],
        roles=[UserRole(payload["role"])],
        token_type=TokenType.ACCESS,
        raw_claims=payload,
        jti="test-jti",
    )


@pytest.fixture(autouse=True)
def parent_progress_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(parents_router, "LearnerRepository", FakeLearnerRepository)
    async def _no_consent(*args, **kwargs) -> None:
        return None

    monkeypatch.setattr(parents_router, "require_active_consent_for_current_user", _no_consent)
    yield


@pytest.mark.asyncio
async def test_parent_progress_allows_admin_read() -> None:
    result = await parents_router.get_learner_progress(
        learner_id="learner-1",
        db=FakeDB(),
        current_user=_auth_context({"sub": "admin-1", "role": "admin"}),
    )
    assert result["learner_id"] == "learner-1"


@pytest.mark.asyncio
async def test_parent_progress_allows_assigned_guardian_read() -> None:
    result = await parents_router.get_learner_progress(
        learner_id="learner-1",
        db=FakeDB(),
        current_user=_auth_context({"sub": "guardian-1", "role": "parent"}),
    )
    assert result["learner_id"] == "learner-1"


@pytest.mark.asyncio
async def test_parent_progress_rejects_unrelated_guardian() -> None:
    with pytest.raises(HTTPException) as exc:
        await parents_router.get_learner_progress(
            learner_id="learner-1",
            db=FakeDB(),
            current_user=_auth_context({"sub": "guardian-2", "role": "parent"}),
        )
    assert exc.value.status_code == 403
    assert "object_forbidden" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_parent_progress_rejects_missing_auth() -> None:
    with pytest.raises(HTTPException) as exc:
        await parents_router.get_learner_progress(
            learner_id="learner-1",
            db=FakeDB(),
            current_user=AuthContext(
                user_id="",
                roles=[],
                token_type=TokenType.ACCESS,
                raw_claims={},
                jti="test-jti",
            ),
        )
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_parent_progress_preserves_not_found() -> None:
    with pytest.raises(HTTPException) as exc:
        await parents_router.get_learner_progress(
            learner_id="missing-learner",
            db=FakeDB(),
            current_user=_auth_context({"sub": "admin-1", "role": "admin"}),
        )
    assert exc.value.status_code == 404
