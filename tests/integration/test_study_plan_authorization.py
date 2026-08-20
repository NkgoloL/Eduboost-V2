from __future__ import annotations

"""Direct-call authorization tests for study-plan write access."""

from typing import Any  # noqa: E402

import pytest  # noqa: E402
from fastapi import HTTPException  # noqa: E402

from app.api_v2_deps.auth import AuthContext, TokenType  # noqa: E402
from app.api_v2_routers import study_plans as study_plans_router  # noqa: E402
from app.domain.api_v2_models import StudyPlanGenerateRequest  # noqa: E402
from app.models import UserRole  # noqa: E402

pytestmark = pytest.mark.integration


LEARNER_1 = "00000000-0000-0000-0000-000000000001"
LEARNER_2 = "00000000-0000-0000-0000-000000000002"
GUARDIAN_1 = "00000000-0000-0000-0000-000000000003"
ADMIN_1 = "00000000-0000-0000-0000-000000000004"


async def fake_enqueue_job(background_tasks, *, operation: str, payload: dict, handler):
    return {
        "job_id": "job-study-plan-1",
        "operation": operation,
        "status": "queued",
        "payload": payload,
    }


async def fake_runtime_kg(*args, **kwargs):
    return {"runtime_kg": True}


async def fake_consent(*args, **kwargs):
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
def study_plan_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(study_plans_router, "enqueue_durable", fake_enqueue_job)
    monkeypatch.setattr(study_plans_router, "build_runtime_kg_study_plan_payload", fake_runtime_kg)
    monkeypatch.setattr(study_plans_router, "require_active_consent_for_current_user", fake_consent)
    yield


def _request() -> StudyPlanGenerateRequest:
    return StudyPlanGenerateRequest(gap_ratio=0.4)


@pytest.mark.asyncio
async def test_generate_study_plan_allows_admin_write() -> None:
    result = await study_plans_router.generate_study_plan(
        LEARNER_1,
        _request(),
        current_user=_auth_context({"sub": ADMIN_1, "role": "admin"}),
        db=object(),
    )
    assert result.job_id == "job-study-plan-1"
    assert result.operation == "study_plan_generation"


@pytest.mark.asyncio
async def test_generate_study_plan_allows_guardian_with_learner_claim() -> None:
    result = await study_plans_router.generate_study_plan(
        LEARNER_1,
        _request(),
        current_user=_auth_context(
            {
                "sub": GUARDIAN_1,
                "role": "parent",
                "guardian_learner_ids": [LEARNER_1],
            }
        ),
        db=object(),
    )
    assert result.job_id == "job-study-plan-1"


@pytest.mark.asyncio
async def test_generate_study_plan_allows_legacy_generate_alias() -> None:
    result = await study_plans_router.generate_study_plan(
        LEARNER_1,
        _request(),
        current_user=_auth_context(
            {
                "sub": GUARDIAN_1,
                "role": "parent",
                "guardian_learner_ids": [LEARNER_1],
            }
        ),
        db=object(),
    )
    assert result.status == "queued"


@pytest.mark.asyncio
async def test_generate_study_plan_allows_learner_self_write() -> None:
    result = await study_plans_router.generate_study_plan(
        LEARNER_1,
        _request(),
        current_user=_auth_context({"sub": LEARNER_1, "role": "student"}),
        db=object(),
    )
    assert result.job_id == "job-study-plan-1"


@pytest.mark.asyncio
async def test_generate_study_plan_rejects_unrelated_guardian() -> None:
    with pytest.raises(HTTPException) as exc:
        await study_plans_router.generate_study_plan(
            LEARNER_1,
            _request(),
            current_user=_auth_context(
                {
                    "sub": GUARDIAN_1,
                    "role": "parent",
                    "guardian_learner_ids": [LEARNER_2],
                }
            ),
            db=object(),
        )
    assert exc.value.status_code == 403
    assert "object_forbidden" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_generate_study_plan_rejects_missing_auth() -> None:
    with pytest.raises(HTTPException):
        await study_plans_router.generate_study_plan(
            LEARNER_1,
            _request(),
            current_user=AuthContext(user_id="", roles=[], token_type=TokenType.ACCESS, raw_claims={}, jti="test-jti"),
            db=object(),
        )
