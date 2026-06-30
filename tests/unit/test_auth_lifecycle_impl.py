from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, Response

from app.domain.schemas import LoginRequest, RefreshRequest, RegisterRequest
from app.models import UserRole
from app.services import auth_lifecycle_impl
from app.services.auth_runtime_boundary import AuthRuntimeContext


class RecordingAudit:
    last_event: tuple[str, object | None, object | None] | None = None

    def __init__(self, db: object):
        self.db = db

    async def auth_event(self, event: str, guardian_id: object | None = None, payload: object | None = None):
        RecordingAudit.last_event = (event, guardian_id, payload)
        return None


@pytest.fixture(autouse=True)
def patch_auth_security(monkeypatch):
    monkeypatch.setattr(auth_lifecycle_impl, "settings", SimpleNamespace(is_production=lambda: False))
    monkeypatch.setattr(auth_lifecycle_impl, "create_access_token", lambda subject, role, claims=None: "access-token")
    monkeypatch.setattr(auth_lifecycle_impl, "create_refresh_token", lambda subject, role, family_id=None: "refresh-token")
    monkeypatch.setattr(auth_lifecycle_impl, "decode_token", lambda token: {"sub": "guardian-1", "jti": "jti", "family": "family"})
    monkeypatch.setattr(auth_lifecycle_impl, "store_refresh_token", AsyncMock())
    monkeypatch.setattr(auth_lifecycle_impl, "FourthEstateService", RecordingAudit)
    monkeypatch.setattr(
        auth_lifecycle_impl,
        "_canonical_access_claims",
        lambda user, *, existing_claims=None, extra=None: {"refresh_jti": extra["refresh_jti"], "refresh_family": extra["refresh_family"]},
    )
    monkeypatch.setattr(auth_lifecycle_impl, "hash_email", lambda value: f"hashed::{value}")
    monkeypatch.setattr(auth_lifecycle_impl, "hash_password", lambda value: f"hashed-pass::{value}")
    monkeypatch.setattr(auth_lifecycle_impl, "encrypt_pii", lambda value: f"encrypted::{value}")
    monkeypatch.setattr(auth_lifecycle_impl, "verify_password", lambda password, stored: password == "correct-password")
    RecordingAudit.last_event = None
    yield


def build_auth_runtime(guardian_repo: object, learner_repo: object, consent_repo: object) -> AuthRuntimeContext:
    return AuthRuntimeContext(db=object(), guardian_repo=guardian_repo, learner_repo=learner_repo, consent_repo=consent_repo)


@pytest.mark.asyncio
async def test_create_dev_session_impl_bootstraps_dev_session_when_missing_data():
    guardian = SimpleNamespace(
        id="guardian-1",
        display_name="Dev Guardian",
        role=UserRole.PARENT,
        password_hash="hashed-pass::secret",
    )
    learner = SimpleNamespace(
        id="learner-1",
        display_name="DevLearner",
        grade=3,
        language="en",
        streak_days=0,
    )

    guardian_repo = SimpleNamespace(
        get_by_email_hash=AsyncMock(return_value=None),
        create=AsyncMock(return_value=guardian),
    )
    learner_repo = SimpleNamespace(
        get_by_guardian=AsyncMock(return_value=[]),
        create=AsyncMock(return_value=learner),
    )
    consent_repo = SimpleNamespace(
        get_active=AsyncMock(return_value=None),
        create=AsyncMock(return_value=None),
    )
    auth_runtime = build_auth_runtime(guardian_repo, learner_repo, consent_repo)
    response = Response()

    result = await auth_lifecycle_impl.create_dev_session_impl(
        response=response,
        db=object(),
        auth_runtime=auth_runtime,
    )

    assert result["access_token"] == "access-token"
    assert result["token_type"] == "bearer"
    assert response.headers.get("set-cookie") is not None
    guardian_repo.get_by_email_hash.assert_awaited_once()
    guardian_repo.create.assert_awaited_once()
    learner_repo.create.assert_awaited_once()
    consent_repo.create.assert_awaited_once()
    assert RecordingAudit.last_event is not None
    assert RecordingAudit.last_event[0] == "DEV_SESSION_BOOTSTRAPPED"


@pytest.mark.asyncio
async def test_create_dev_session_impl_rejects_production_environment(monkeypatch):
    monkeypatch.setattr(auth_lifecycle_impl.settings, "is_production", lambda: True)
    response = Response()
    auth_runtime = build_auth_runtime(None, None, None)

    with pytest.raises(HTTPException) as exc_info:
        await auth_lifecycle_impl.create_dev_session_impl(
            response=response,
            db=object(),
            auth_runtime=auth_runtime,
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_login_impl_returns_access_token_for_valid_credentials():
    guardian = SimpleNamespace(id="guardian-1", role=UserRole.PARENT, password_hash="stored-password")
    repo = SimpleNamespace(get_by_email_hash=AsyncMock(return_value=guardian))
    auth_runtime = SimpleNamespace(guardian_repo=repo)
    response = Response()

    result = await auth_lifecycle_impl.login_impl(
        request=SimpleNamespace(),
        body=LoginRequest(email="user@example.com", password="correct-password"),
        response=response,
        db=object(),
        auth_runtime=auth_runtime,
    )

    assert result.access_token == "access-token"
    auth_lifecycle_impl.store_refresh_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_impl_rejects_invalid_credentials():
    repo = SimpleNamespace(get_by_email_hash=AsyncMock(return_value=None))
    auth_runtime = SimpleNamespace(guardian_repo=repo)
    response = Response()

    with pytest.raises(HTTPException) as exc_info:
        await auth_lifecycle_impl.login_impl(
            request=SimpleNamespace(),
            body=LoginRequest(email="bad@example.com", password="wrong-password"),
            response=response,
            db=object(),
            auth_runtime=auth_runtime,
        )

    assert exc_info.value.status_code == 401
    assert RecordingAudit.last_event is not None
    assert RecordingAudit.last_event[0] == "USER_LOGIN_FAILED"


@pytest.mark.asyncio
async def test_refresh_impl_requires_a_token():
    auth_runtime = SimpleNamespace(guardian_repo=SimpleNamespace())
    response = Response()

    with pytest.raises(HTTPException) as exc_info:
        await auth_lifecycle_impl.refresh_impl(
            request=SimpleNamespace(),
            response=response,
            body=None,
            db=object(),
            cookie_refresh=None,
            auth_runtime=auth_runtime,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_impl_rejects_disabled_account(monkeypatch):
    repo = SimpleNamespace(get_by_id=AsyncMock(return_value=SimpleNamespace(is_active=False)))
    auth_runtime = SimpleNamespace(guardian_repo=repo, guardian_learner_ids=AsyncMock(return_value=[]))
    response = Response()
    monkeypatch.setattr(auth_lifecycle_impl, "consume_refresh_token", AsyncMock(return_value={"sub": "guardian-1", "family": "family-1", "jti": "jti"}))

    with pytest.raises(HTTPException) as exc_info:
        await auth_lifecycle_impl.refresh_impl(
            request=SimpleNamespace(),
            response=response,
            body=RefreshRequest(refresh_token="refresh-token"),
            db=object(),
            cookie_refresh=None,
            auth_runtime=auth_runtime,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_impl_issues_new_access_token_when_account_is_active(monkeypatch):
    guardian = SimpleNamespace(id="guardian-1", is_active=True, role=UserRole.PARENT)
    repo = SimpleNamespace(get_by_id=AsyncMock(return_value=guardian))
    auth_runtime = SimpleNamespace(guardian_repo=repo, guardian_learner_ids=AsyncMock(return_value=["learner-1"]))
    response = Response()
    monkeypatch.setattr(auth_lifecycle_impl, "consume_refresh_token", AsyncMock(return_value={"sub": "guardian-1", "family": "family-1", "jti": "jti"}))

    result = await auth_lifecycle_impl.refresh_impl(
        request=SimpleNamespace(),
        response=response,
        body=RefreshRequest(refresh_token="refresh-token"),
        db=object(),
        cookie_refresh=None,
        auth_runtime=auth_runtime,
    )

    assert result.access_token == "access-token"
    assert auth_lifecycle_impl.store_refresh_token.await_count == 1


@pytest.mark.asyncio
async def test_register_impl_rejects_duplicate_email():
    repo = SimpleNamespace(get_by_email_hash=AsyncMock(return_value=SimpleNamespace()))
    auth_runtime = SimpleNamespace(guardian_repo=repo)
    response = Response()

    with pytest.raises(HTTPException) as exc_info:
        await auth_lifecycle_impl.register_impl(
            request=SimpleNamespace(),
            body=RegisterRequest(email="existing@example.com", password="StrongPass123!", display_name="Existing", role="parent"),
            response=response,
            db=object(),
            auth_runtime=auth_runtime,
        )

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_register_impl_creates_guardian_and_returns_token():
    guardian = SimpleNamespace(id="guardian-1", role=UserRole.PARENT, password_hash="hashed-pass::pwd")
    repo = SimpleNamespace(
        get_by_email_hash=AsyncMock(return_value=None),
        create=AsyncMock(return_value=guardian),
    )
    auth_runtime = SimpleNamespace(guardian_repo=repo)
    response = Response()

    result = await auth_lifecycle_impl.register_impl(
        request=SimpleNamespace(),
        body=RegisterRequest(email="new@example.com", password="StrongPass123!", display_name="New Guardian", role="parent"),
        response=response,
        db=object(),
        auth_runtime=auth_runtime,
    )

    assert result.access_token == "access-token"
    assert auth_lifecycle_impl.store_refresh_token.await_count == 1
    assert RecordingAudit.last_event is not None
    assert RecordingAudit.last_event[0] == "USER_REGISTERED"
