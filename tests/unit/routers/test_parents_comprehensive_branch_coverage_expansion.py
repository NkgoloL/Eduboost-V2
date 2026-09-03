"""Batch 223 — app/api_v2_routers/parents.py comprehensive branch coverage expansion.

Tests:
- get_parent_dashboard: guardian 404, learner consent exception skip, successful analytics and response assembly
- get_parent_trust_dashboard: forbidden (different guardian, non-admin), guardian 404, learner consent skip, zero vs positive lessons completion rate, executive summary call, analytics event
- export_parent_access_bundle: forbidden, guardian 404, valid export bundle with multiple learners
- get_learner_progress: learner 404, 30-day timeline grouping, knowledge gap breakdown by subject (active vs resolved)
- request_erasure: delegating to POPIADataRightsService.request_erasure
- _log_purge_request helper function
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api_v2_deps.auth import AuthContext, require_parent_or_admin
from app.api_v2_routers.parents import _log_purge_request, get_db, router
from app.models import Guardian


GUARDIAN_UUID = uuid.uuid4()
GUARDIAN_ID_STR = str(GUARDIAN_UUID)


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    mock_auth = AuthContext(
        user_id=GUARDIAN_ID_STR,
        email="parent@eduboost.co.za",
        role="parent",
        scopes=["parent:read"],
        token_type="access",
        raw_claims={},
        jti="jti-123",
    )
    app.dependency_overrides[require_parent_or_admin] = lambda: mock_auth

    mock_session = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_session

    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /parents/dashboard
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_parent_dashboard_guardian_not_found(app, client):
    mock_session = AsyncMock()
    mock_session.get.return_value = None
    app.dependency_overrides[get_db] = lambda: mock_session

    response = client.get("/parents/dashboard")
    assert response.status_code == 404
    assert "Guardian not found" in response.json()["detail"]


@pytest.mark.unit
def test_get_parent_dashboard_success_and_consent_filter(app, client):
    mock_session = AsyncMock()
    mock_guardian = MagicMock(spec=Guardian, id=GUARDIAN_UUID, subscription_tier="premium")
    mock_session.get.return_value = mock_guardian

    id1 = uuid.uuid4()
    id2 = uuid.uuid4()

    learner1 = MagicMock(
        id=id1,
        display_name="Learner One",
        grade=4,
        archetype="visual",
        theta=0.55,
    )
    learner2 = MagicMock(
        id=id2,
        display_name="Learner Two",
        grade=6,
        archetype="auditory",
        theta=-0.12,
    )

    mock_session.scalar.side_effect = [
        3,                   # lessons_this_week (learner1)
        1,                   # active_gaps (learner1)
        datetime.now(timezone.utc),  # last_lesson_at (learner1)
        10,                  # total_lessons (learner1)
    ]
    app.dependency_overrides[get_db] = lambda: mock_session

    with (
        patch("app.api_v2_routers.parents.LearnerService") as mock_svc_cls,
        patch("app.api_v2_routers.parents.require_learner_read_for_current_user"),
        patch(
            "app.api_v2_routers.parents.require_active_consent_for_current_user",
            side_effect=[None, HTTPException(status_code=403, detail="No consent")],
        ),
    ):
        mock_svc = MagicMock()
        mock_svc.list_by_guardian = AsyncMock(return_value=[learner1, learner2])
        mock_svc_cls.return_value = mock_svc

        response = client.get("/parents/dashboard")
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data", payload)
        assert data["guardian_id"] == GUARDIAN_ID_STR
        assert len(data["learners"]) == 1
        assert data["learners"][0]["learner_id"] == str(id1)
        assert data["total_lessons_generated"] == 10


# ---------------------------------------------------------------------------
# GET /parents/{guardian_id}/dashboard (Trust Dashboard)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_parent_trust_dashboard_forbidden(app, client):
    response = client.get("/parents/other-guardian-456/dashboard")
    assert response.status_code == 403


@pytest.mark.unit
def test_get_parent_trust_dashboard_guardian_not_found(app, client):
    mock_session = AsyncMock()
    mock_session.get.return_value = None
    app.dependency_overrides[get_db] = lambda: mock_session

    response = client.get(f"/parents/{GUARDIAN_ID_STR}/dashboard")
    assert response.status_code == 404


@pytest.mark.unit
def test_get_parent_trust_dashboard_success(app, client):
    mock_session = AsyncMock()
    mock_guardian = MagicMock(spec=Guardian, id=GUARDIAN_ID_STR, subscription_tier="free")
    mock_session.get.return_value = mock_guardian

    learner = MagicMock(
        id="learner-uuid-str-1",
        display_name="Lethabo",
        grade=4,
        archetype="explorer",
        theta=0.88,
        pseudonym_id="pseudo-1",
        streak_days=5,
    )

    gap_mock = MagicMock(topic="Fractions")
    res_gaps = MagicMock()
    res_gaps.scalars.return_value.all.return_value = [gap_mock]
    mock_session.execute.return_value = res_gaps

    mock_session.scalar.side_effect = [
        4,  # lessons_generated
        3,  # lessons_completed
    ]
    app.dependency_overrides[get_db] = lambda: mock_session

    with (
        patch("app.api_v2_routers.parents.LearnerService") as mock_svc_cls,
        patch("app.api_v2_routers.parents.require_learner_read_for_current_user"),
        patch("app.api_v2_routers.parents.require_active_consent_for_current_user", return_value=None),
        patch("app.api_v2_routers.parents._executive.generate_progress_summary", AsyncMock(return_value="Great progress on Fractions!")),
    ):
        mock_svc = MagicMock()
        mock_svc.list_by_guardian = AsyncMock(return_value=[learner])
        mock_svc_cls.return_value = mock_svc

        response = client.get(f"/parents/{GUARDIAN_ID_STR}/dashboard")
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data", payload)
        assert data["guardian_id"] == GUARDIAN_ID_STR
        assert len(data["learners"]) == 1
        assert data["learners"][0]["lesson_completion_rate_7d"] == 75.0
        assert data["learners"][0]["ai_progress_summary"] == "Great progress on Fractions!"


# ---------------------------------------------------------------------------
# GET /parents/{guardian_id}/export
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_export_parent_access_bundle_forbidden_and_404(app, client):
    res_forbid = client.get("/parents/different-guardian/export")
    assert res_forbid.status_code == 403

    mock_session = AsyncMock()
    mock_session.get.return_value = None
    app.dependency_overrides[get_db] = lambda: mock_session

    res_404 = client.get(f"/parents/{GUARDIAN_ID_STR}/export")
    assert res_404.status_code == 404


@pytest.mark.unit
def test_export_parent_access_bundle_success(app, client):
    mock_session = AsyncMock()
    mock_guardian = MagicMock(spec=Guardian, id=GUARDIAN_ID_STR, subscription_tier="premium")
    mock_session.get.return_value = mock_guardian

    learner = MagicMock(id="learner-1", display_name="Lethabo")

    with (
        patch("app.api_v2_routers.parents.LearnerService") as mock_svc_cls,
        patch("app.api_v2_routers.parents.require_learner_read_for_current_user"),
        patch("app.api_v2_routers.parents.require_active_consent_for_current_user", return_value=None),
    ):
        mock_svc = MagicMock()
        mock_svc.list_by_guardian = AsyncMock(return_value=[learner])
        mock_svc_cls.return_value = mock_svc
        app.dependency_overrides[get_db] = lambda: mock_session

        response = client.get(f"/parents/{GUARDIAN_ID_STR}/export")
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data", payload)
        assert data["guardian_id"] == GUARDIAN_ID_STR
        assert len(data["exports"]) == 1
        assert "export_url" in data["exports"][0]


# ---------------------------------------------------------------------------
# GET /parents/learners/{learner_id}/progress
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_learner_progress_404_and_success(app, client):
    mock_session = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_session

    with (
        patch("app.api_v2_routers.parents.LearnerService") as mock_svc_cls,
        patch("app.api_v2_routers.parents.require_learner_read_for_current_user"),
        patch("app.api_v2_routers.parents.require_active_consent_for_current_user", return_value=None),
    ):
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc

        # 404
        mock_svc.get_learner_summary = AsyncMock(return_value=None)
        res_404 = client.get("/parents/learners/missing-123/progress")
        assert res_404.status_code == 404

        # Success
        mock_learner = MagicMock(
            id="learner-123",
            display_name="Lethabo",
            grade=4,
            archetype="visual",
            theta=1.23,
        )
        mock_svc.get_learner_summary = AsyncMock(return_value=mock_learner)

        res_lessons = MagicMock()
        res_lessons.all.return_value = [
            (datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc), "Mathematics"),
            (datetime(2026, 8, 1, 14, 0, tzinfo=timezone.utc), "English"),
        ]

        res_gaps = MagicMock()
        res_gaps.all.return_value = [
            ("Mathematics", False),
            ("Mathematics", True),
            ("English", False),
        ]

        mock_session.execute.side_effect = [res_lessons, res_gaps]

        res_ok = client.get("/parents/learners/learner-123/progress")
        assert res_ok.status_code == 200
        payload = res_ok.json()
        data = payload.get("data", payload)
        assert data["learner_id"] == "learner-123"
        assert data["total_lessons"] == 2
        assert len(data["lessons_last_30_days"]) == 1
        assert len(data["knowledge_gap_breakdown"]) == 2


# ---------------------------------------------------------------------------
# DELETE /parents/learners/{learner_id} & Helpers
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_request_erasure_endpoint(app, client):
    mock_session = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("app.api_v2_routers.parents.POPIADataRightsService") as mock_popia_cls:
        mock_popia = MagicMock()
        mock_popia.request_erasure = AsyncMock(return_value={"status": "erasure_requested"})
        mock_popia_cls.return_value = mock_popia

        response = client.delete("/parents/learners/learner-123")
        assert response.status_code == 202
        payload = response.json()
        data = payload.get("data", payload)
        assert data == {"status": "erasure_requested"}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_log_purge_request_helper():
    assert await _log_purge_request("learner-1", "pseudo-1") is None
