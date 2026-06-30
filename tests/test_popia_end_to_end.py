import pytest
pytestmark = pytest.mark.integration

from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from app.api_v2 import app
from app.core import security as core_security

client = TestClient(app)


# ---------------------------------------------------------------------------
# Auth-required smoke tests (no mocks needed)
# ---------------------------------------------------------------------------

def test_popia_export_endpoint_auth_required():
    response = client.post(
        "/v2/popia/exports",
        json={"learner_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 401


def test_popia_erasure_endpoint_auth_required():
    response = client.post(
        "/v2/popia/erasure",
        json={"learner_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 401


def test_popia_api_prefix_auth_required():
    response = client.post(
        "/api/v2/popia/erasure",
        json={"learner_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 401


def test_audit_log_visibility():
    response = client.get("/api/v2/audit")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Full-flow test with service mock
# ---------------------------------------------------------------------------

def test_popia_full_flow_success():
    fake_user = {"sub": "guardian-123", "role": "guardian"}

    async def fake_current_user():
        return fake_user

    app.dependency_overrides[core_security.get_current_user] = fake_current_user

    mock_svc = AsyncMock()
    mock_svc.build_learner_export.return_value = {"status": "queued"}
    mock_svc.request_erasure.return_value = {"status": "pending"}
    mock_svc.cancel_erasure.return_value = {"status": "cancelled"}

    from app.api_v2_deps.consent_lifecycle import get_canonical_data_rights_service
    app.dependency_overrides[get_canonical_data_rights_service] = lambda: mock_svc

    try:
        # 1. Export
        resp = client.post(
            "/v2/popia/exports",
            json={"learner_id": "00000000-0000-0000-0000-000000000000"},
        )
        assert resp.status_code == 200
        assert mock_svc.build_learner_export.called

        # 2. Erasure
        resp = client.post(
            "/v2/popia/erasure",
            json={"learner_id": "00000000-0000-0000-0000-000000000000", "reason": "test"},
        )
        assert resp.status_code in (200, 201)
        assert mock_svc.request_erasure.called

        # 3. Cancel erasure
        resp = client.post(
            "/v2/popia/erasure/00000000-0000-0000-0000-000000000000/cancel",
        )
        assert resp.status_code in (200, 201)
        assert mock_svc.cancel_erasure.called
    finally:
        app.dependency_overrides.clear()
