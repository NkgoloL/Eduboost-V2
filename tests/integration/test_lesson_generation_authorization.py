from __future__ import annotations

"""Direct-call authorization tests for lesson generation."""

from datetime import datetime, timedelta, timezone  # noqa: E402
from types import SimpleNamespace  # noqa: E402
from typing import Any  # noqa: E402
from uuid import UUID  # noqa: E402

import pytest  # noqa: E402
from fastapi import HTTPException  # noqa: E402

from app.api_v2_deps.auth import AuthContext, TokenType  # noqa: E402
from app.api_v2_routers import lessons as lessons_router  # noqa: E402
from app.domain.schemas import LessonRequest  # noqa: E402
from app.models import UserRole  # noqa: E402

pytestmark = pytest.mark.integration


LEARNER_ID = "11111111-1111-1111-1111-111111111111"
GUARDIAN_ID = "22222222-2222-2222-2222-222222222222"
ADMIN_ID = "33333333-3333-3333-3333-333333333333"


class FakeLessonService:
    async def generate_lesson_for_learner(self, body, user_id: UUID):
        raise AssertionError("background handler should not run during enqueue contract test")


async def fake_lesson_service():
    return FakeLessonService()


async def fake_enqueue_job(background_tasks, *, operation: str, payload: dict, handler):
    return {
        "job_id": "job-lesson-1",
        "operation": operation,
        "status": "queued",
        "payload": payload,
    }


async def fake_consent(*args, **kwargs):
    return None


def make_auth_context(payload: dict[str, Any]) -> AuthContext:
    now = datetime.now(timezone.utc)
    return AuthContext(
        user_id=str(payload["sub"]),
        guardian_id=payload.get("guardian_id"),
        learner_id=payload.get("learner_id"),
        roles=[UserRole(str(payload["role"]))],
        token_type=TokenType.ACCESS,
        raw_claims=payload,
        issued_at=now,
        expires_at=now + timedelta(minutes=15),
        jti=payload.get("jti", "jti-lesson-1"),
    )


def override_user(payload: dict[str, Any]):
    async def _override() -> AuthContext:
        return make_auth_context(payload)

    return _override


@pytest.fixture(autouse=True)
def lesson_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(lessons_router, "enqueue_durable", fake_enqueue_job)
    monkeypatch.setattr(lessons_router, "require_active_consent_for_current_user", fake_consent)
    monkeypatch.setattr(lessons_router, "get_lesson_service", fake_lesson_service)
    yield


def lesson_payload(learner_id: str = LEARNER_ID) -> LessonRequest:
    return LessonRequest(
        learner_id=learner_id,
        subject="Math",
        topic="Fractions",
        language="en",
    )


@pytest.mark.asyncio
async def test_generate_lesson_allows_admin_write() -> None:
    result = await lessons_router.generate_lesson(
        request=SimpleNamespace(state=SimpleNamespace()),
        body=lesson_payload(),
        auth=make_auth_context({"sub": ADMIN_ID, "role": "admin"}),
        db=object(),
    )
    assert result.job_id == "job-lesson-1"


@pytest.mark.asyncio
async def test_generate_lesson_allows_guardian_with_learner_claim() -> None:
    result = await lessons_router.generate_lesson(
        request=SimpleNamespace(state=SimpleNamespace()),
        body=lesson_payload(),
        auth=make_auth_context({"sub": GUARDIAN_ID, "role": "parent", "guardian_learner_ids": [LEARNER_ID]}),
        db=object(),
    )
    assert result.status == "queued"


@pytest.mark.asyncio
async def test_generate_lesson_allows_root_alias() -> None:
    result = await lessons_router.generate_lesson(
        request=SimpleNamespace(state=SimpleNamespace()),
        body=lesson_payload(),
        auth=make_auth_context({"sub": GUARDIAN_ID, "role": "parent", "guardian_learner_ids": [LEARNER_ID]}),
        db=object(),
    )
    assert result.job_id == "job-lesson-1"


@pytest.mark.asyncio
async def test_generate_lesson_allows_learner_self_write() -> None:
    result = await lessons_router.generate_lesson(
        request=SimpleNamespace(state=SimpleNamespace()),
        body=lesson_payload(),
        auth=make_auth_context({"sub": LEARNER_ID, "role": "student"}),
        db=object(),
    )
    assert result.job_id == "job-lesson-1"


@pytest.mark.asyncio
async def test_generate_lesson_rejects_unrelated_guardian() -> None:
    with pytest.raises(HTTPException) as exc:
        await lessons_router.generate_lesson(
            request=SimpleNamespace(state=SimpleNamespace()),
            body=lesson_payload(),
            auth=make_auth_context({"sub": GUARDIAN_ID, "role": "parent", "guardian_learner_ids": ["other-learner"]}),
            db=object(),
        )
    assert exc.value.status_code == 403
    assert "object_forbidden" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_generate_lesson_rejects_missing_auth() -> None:
    with pytest.raises(HTTPException):
        await lessons_router.generate_lesson(
            request=SimpleNamespace(state=SimpleNamespace()),
            body=lesson_payload(),
            auth=AuthContext(user_id="", roles=[], token_type=TokenType.ACCESS, raw_claims={}, jti="jti-lesson-1"),
            db=object(),
        )
