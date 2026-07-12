"""Direct-call authorization tests for diagnostic items read access."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.api_v2 import app  # noqa: F401 - imported for parity with route wiring checks
from app.api_v2_deps.auth import AuthContext, TokenType
from app.api_v2_routers import diagnostics as diagnostics_router
from app.models import UserRole

pytestmark = pytest.mark.integration


class FakeConsentService:
    def __init__(self, db: object) -> None:
        self.db = db

    async def require_active_consent(self, learner_id: str, actor_id: str | None = None) -> None:
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
            grade=4,
        )


class FakeIRTRepository:
    def __init__(self, db: object) -> None:
        self.db = db

    async def get_items_for_grade(self, grade: int, limit: int | None = None) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                id="item-1",
                question_text="What is 1 + 1?",
                options=["1", "2", "3", "4"],
                subject="MATH",
                topic="Addition",
                skill="Addition",
                b_param=0.0,
                a_param=1.0,
                caps_reference="CAPS-MATH-4",
                grade=grade,
                review_status="approved",
            )
        ]


class FakeCAPSValidator:
    def validate(self, grade: int, subject: str, topic: str) -> SimpleNamespace:
        return SimpleNamespace(caps_reference="CAPS-MATH-4")


async def override_db() -> object:
    return object()


def override_user(payload: dict[str, Any]):
    async def _override() -> AuthContext:
        return AuthContext(
            user_id=payload["sub"],
            guardian_id=payload.get("guardian_id"),
            learner_id=payload.get("learner_id"),
            roles=[UserRole(payload["role"])],
            token_type=TokenType.ACCESS,
            raw_claims=payload,
            jti="test-jti",
        )

    return _override


@pytest.fixture(autouse=True)
def diagnostic_items_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(diagnostics_router, "require_active_consent_for_current_user", AsyncMock(return_value=None))
    monkeypatch.setattr(
        diagnostics_router.diagnostic_repositories,
        "learner",
        lambda db: FakeLearnerRepository(db),
    )
    monkeypatch.setattr(
        diagnostics_router.diagnostic_repositories,
        "irt",
        lambda db: FakeIRTRepository(db),
    )
    monkeypatch.setattr(diagnostics_router, "_caps_validator", FakeCAPSValidator())
    diagnostics_router.get_db = override_db  # type: ignore[assignment]
    yield


def _request() -> SimpleNamespace:
    return SimpleNamespace(state=SimpleNamespace())


@pytest.mark.asyncio
async def test_get_diagnostic_items_allows_admin_read() -> None:
    result = await diagnostics_router.get_diagnostic_items(
        "learner-1",
        request=_request(),
        db=object(),
        current_user=AuthContext(
            user_id="admin-1",
            roles=[UserRole.ADMIN],
            token_type=TokenType.ACCESS,
            raw_claims={"sub": "admin-1", "role": "admin"},
            jti="test-jti",
        ),
    )
    assert result[0]["id"] == "item-1"


@pytest.mark.asyncio
async def test_get_diagnostic_items_allows_assigned_guardian_read() -> None:
    result = await diagnostics_router.get_diagnostic_items(
        "learner-1",
        request=_request(),
        db=object(),
        current_user=AuthContext(
            user_id="guardian-1",
            roles=[UserRole.PARENT],
            token_type=TokenType.ACCESS,
            raw_claims={"sub": "guardian-1", "role": "parent"},
            jti="test-jti",
        ),
    )
    assert result[0]["id"] == "item-1"


@pytest.mark.asyncio
async def test_get_diagnostic_items_allows_learner_self_read() -> None:
    result = await diagnostics_router.get_diagnostic_items(
        "learner-1",
        request=_request(),
        db=object(),
        current_user=AuthContext(
            user_id="learner-1",
            roles=[UserRole.STUDENT],
            token_type=TokenType.ACCESS,
            raw_claims={"sub": "learner-1", "role": "student"},
            jti="test-jti",
        ),
    )
    assert result[0]["id"] == "item-1"


@pytest.mark.asyncio
async def test_get_diagnostic_items_rejects_unrelated_guardian() -> None:
    with pytest.raises(HTTPException) as exc:
        await diagnostics_router.get_diagnostic_items(
            "learner-1",
            request=_request(),
            db=object(),
            current_user=AuthContext(
                user_id="guardian-2",
                roles=[UserRole.PARENT],
                token_type=TokenType.ACCESS,
                raw_claims={"sub": "guardian-2", "role": "parent"},
                jti="test-jti",
            ),
        )
    assert exc.value.status_code == 403
    assert "object_forbidden" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_get_diagnostic_items_rejects_missing_auth() -> None:
    with pytest.raises(HTTPException) as exc:
        await diagnostics_router.get_diagnostic_items(
            "learner-1",
            request=_request(),
            db=object(),
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
async def test_get_diagnostic_items_preserves_not_found() -> None:
    with pytest.raises(HTTPException) as exc:
        await diagnostics_router.get_diagnostic_items(
            "missing-learner",
            request=_request(),
            db=object(),
            current_user=AuthContext(
                user_id="admin-1",
                roles=[UserRole.ADMIN],
                token_type=TokenType.ACCESS,
                raw_claims={"sub": "admin-1", "role": "admin"},
                jti="test-jti",
            ),
        )
    assert exc.value.status_code == 404
