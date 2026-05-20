"""
Negative-path tests for POPIA data-subject rights endpoints.

Strategy: override get_data_subject_rights_service_for_router with an AsyncMock
so we can control what the service returns/raises without touching the DB.
"""
import pytest
pytestmark = pytest.mark.integration

from unittest.mock import AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api_v2 import app
from app.core import security as core_security
from app.api_v2_deps.consent_lifecycle import get_canonical_data_rights_service
from app.services.popia_service import POPIADataRightsService

client = TestClient(app)

LEARNER_ID = "00000000-0000-0000-0000-000000000001"


def _set_user(sub: str, role: str = "guardian"):
    async def fake_current_user():
        return {"sub": sub, "role": role}
    app.dependency_overrides[core_security.get_current_user] = fake_current_user


@pytest.fixture
def override_popia_svc():
    mock_svc = AsyncMock(spec=POPIADataRightsService)
    app.dependency_overrides[get_canonical_data_rights_service] = lambda: mock_svc


def _set_service(mock_svc):
    app.dependency_overrides[get_canonical_data_rights_service] = lambda: mock_svc


def teardown_function():
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Unauthenticated requests → 401
# ---------------------------------------------------------------------------

def test_erasure_requires_auth():
    app.dependency_overrides.clear()
    r = client.post("/v2/popia/erasure", json={"learner_id": LEARNER_ID, "reason": "test"})
    assert r.status_code == 401


def test_export_requires_auth():
    app.dependency_overrides.clear()
    r = client.post("/v2/popia/exports", json={"learner_id": LEARNER_ID})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Service raises 404 → router propagates 404
# ---------------------------------------------------------------------------

def test_erasure_404_when_learner_not_found():
    _set_user("guardian-1")
    mock_svc = AsyncMock()
    mock_svc.request_erasure.side_effect = HTTPException(status_code=404, detail="Learner not found")
    _set_service(mock_svc)

    r = client.post("/v2/popia/erasure", json={"learner_id": LEARNER_ID, "reason": "test"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Service raises 409 → router propagates 409 (already requested)
# ---------------------------------------------------------------------------

def test_erasure_409_when_already_requested():
    _set_user("guardian-1")
    mock_svc = AsyncMock()
    mock_svc.request_erasure.side_effect = HTTPException(
        status_code=409, detail="Erasure already requested"
    )
    _set_service(mock_svc)

    r = client.post("/v2/popia/erasure", json={"learner_id": LEARNER_ID, "reason": "test"})
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# Service raises 409 on cancel → router propagates 409 (nothing to cancel)
# ---------------------------------------------------------------------------

def test_cancel_erasure_409_when_no_pending_request():
    _set_user("guardian-1")
    mock_svc = AsyncMock()
    mock_svc.cancel_erasure.side_effect = HTTPException(
        status_code=409, detail="No pending erasure request"
    )
    _set_service(mock_svc)

    r = client.post(f"/v2/popia/erasure/{LEARNER_ID}/cancel")
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# Service raises 403 → router propagates 403 (wrong guardian)
# ---------------------------------------------------------------------------

def test_erasure_403_for_wrong_guardian():
    _set_user("other-guardian")
    mock_svc = AsyncMock()
    mock_svc.request_erasure.side_effect = HTTPException(
        status_code=403, detail="Not your learner"
    )
    _set_service(mock_svc)

    r = client.post("/v2/popia/erasure", json={"learner_id": LEARNER_ID, "reason": "test"})
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Missing body fields → 422 Unprocessable Entity
# ---------------------------------------------------------------------------

def test_erasure_422_missing_learner_id():
    _set_user("guardian-1")
    mock_svc = AsyncMock()
    _set_service(mock_svc)

    r = client.post("/v2/popia/erasure", json={"reason": "test"})
    assert r.status_code == 422


def test_export_422_missing_learner_id():
    _set_user("guardian-1")
    mock_svc = AsyncMock()
    _set_service(mock_svc)

    r = client.post("/v2/popia/exports", json={})
    assert r.status_code == 422
