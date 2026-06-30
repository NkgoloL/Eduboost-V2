from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api_v2 import app
from app.api_v2_deps.auth import AuthContext, TokenType
from app.api_v2_routers import lessons as lessons_router
from app.core.security import get_current_user, require_admin, require_parent_or_admin
from app.models import UserRole


def _override_user():
    return {"sub": "00000000-0000-0000-0000-000000000002", "role": "admin", "jti": "test-jti"}


def _override_lesson_auth():
    now = datetime.now(timezone.utc)
    return AuthContext(
        user_id="00000000-0000-0000-0000-000000000002",
        roles=[UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={
            "sub": "00000000-0000-0000-0000-000000000002",
            "role": "admin",
            "jti": "test-jti",
            "type": "access",
        },
        issued_at=now,
        expires_at=now + timedelta(minutes=15),
        jti="test-jti",
    )


def _client() -> TestClient:
    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[require_parent_or_admin] = _override_user
    app.dependency_overrides[require_admin] = _override_user
    app.dependency_overrides[lessons_router.require_auth_context] = _override_lesson_auth
    return TestClient(app)


def teardown_module():
    app.dependency_overrides.clear()


def test_lesson_generation_job_flow():
    client = _client()
    with patch("app.api_v2_routers.lessons.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.lessons.enqueue_durable", new=AsyncMock(return_value="lesson-job-1")):
        response = client.post(
            "/v2/lessons/generate",
            json={
                "learner_id": "00000000-0000-0000-0000-000000000001",
                "subject": "Mathematics",
                "topic": "Fractions",
            },
        )
    assert response.status_code == 202
    assert response.json()["data"]["job_id"] == "lesson-job-1"


def test_study_plan_generation_job_flow():
    client = _client()
    with patch("app.api_v2_routers.study_plans.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.study_plans.enqueue_durable", new=AsyncMock(return_value="study-plan-job-1")):
        response = client.post(
            "/v2/study-plans/generate/00000000-0000-0000-0000-000000000001",
            json={"gap_ratio": 0.4},
        )
    assert response.status_code == 202
    assert response.json()["data"]["job_id"] == "study-plan-job-1"


def test_consent_renewal_job_flow():
    client = _client()
    with patch("app.api_v2_routers.consent_renewal.enqueue_durable", new=AsyncMock(return_value="consent-job-1")):
        response = client.post("/v2/admin/consent/trigger-renewal-reminders")
    assert response.status_code == 202
    assert response.json()["data"]["job_id"] == "consent-job-1"
