from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.models import UserRole
from app.services.auth_lifecycle_impl import DEV_CONSENT_POLICY_VERSION, _ensure_dev_session_consent, _normalise_role_value
from app.services.auth_token_claims import build_access_token_claims


class FakeConsentRepo:
    def __init__(self, active=None, latest=None):
        self.active = active
        self.latest = latest
        self.created = None

    async def get_active(self, learner_id):
        return self.active

    async def get_latest_for_learner(self, learner_id):
        return self.latest

    async def create(self, **kwargs):
        self.created = SimpleNamespace(**kwargs)
        return self.created


def test_user_role_enum_is_serialised_as_stable_jwt_role() -> None:
    payload = build_access_token_claims(SimpleNamespace(id="guardian-1", role=UserRole.PARENT))
    assert payload["role"] == "parent"
    assert _normalise_role_value(UserRole.PARENT) == "parent"


@pytest.mark.asyncio
async def test_dev_session_consent_normalises_existing_active_policy_version() -> None:
    consent = SimpleNamespace(
        guardian_id="old-guardian",
        learner_id="learner-1",
        policy_version="1.0",
        status="granted",
        revoked_at=None,
        expires_at=datetime.now(timezone.utc),
    )
    repo = FakeConsentRepo(active=consent)

    result = await _ensure_dev_session_consent(
        repo,
        guardian_id="guardian-1",
        learner_id="learner-1",
    )

    assert result is consent
    assert consent.guardian_id == "guardian-1"
    assert consent.policy_version == DEV_CONSENT_POLICY_VERSION
    assert repo.created is None


@pytest.mark.asyncio
async def test_dev_session_consent_creates_missing_policy_version() -> None:
    repo = FakeConsentRepo()

    result = await _ensure_dev_session_consent(
        repo,
        guardian_id="guardian-1",
        learner_id="learner-1",
    )

    assert result is repo.created
    assert repo.created.policy_version == DEV_CONSENT_POLICY_VERSION
