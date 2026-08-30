"""Comprehensive unit tests for app/core/dependencies.py."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Request

from app.core.dependencies import (
    get_consent_repo,
    get_current_user_id,
    get_current_guardian_id,
    require_active_consent,
    get_request_id,
)
from app.core.exceptions import AuthenticationError, ConsentRequiredError
from app.repositories.consent_repository import ConsentRepository


@pytest.mark.asyncio
async def test_get_consent_repo():
    repo = await get_consent_repo()
    assert isinstance(repo, ConsentRepository)


@pytest.mark.asyncio
async def test_get_current_user_id_missing_credentials():
    with pytest.raises(AuthenticationError, match="missing"):
        await get_current_user_id(None)


@pytest.mark.asyncio
async def test_get_current_user_id_valid_token():
    uid = uuid.uuid4()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake.jwt.token")
    with patch("app.core.dependencies.decode_token", return_value={"sub": str(uid)}):
        res = await get_current_user_id(credentials)
        assert res == uid


@pytest.mark.asyncio
async def test_get_current_user_id_missing_sub():
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake.jwt.token")
    with patch("app.core.dependencies.decode_token", return_value={}):
        with pytest.raises(AuthenticationError):
            await get_current_user_id(credentials)


@pytest.mark.asyncio
async def test_get_current_guardian_id():
    uid = uuid.uuid4()
    res = await get_current_guardian_id(uid)
    assert res == uid


@pytest.mark.asyncio
async def test_require_active_consent_granted():
    learner_id = uuid.uuid4()
    mock_db = AsyncMock()
    mock_repo = MagicMock(spec=ConsentRepository)
    mock_repo.get_active = AsyncMock(return_value=MagicMock())

    # Should not raise
    await require_active_consent(learner_id, db=mock_db, repo=mock_repo)


@pytest.mark.asyncio
async def test_require_active_consent_missing():
    learner_id = uuid.uuid4()
    mock_db = AsyncMock()
    mock_repo = MagicMock(spec=ConsentRepository)
    mock_repo.get_active = AsyncMock(return_value=None)

    with pytest.raises(ConsentRequiredError):
        await require_active_consent(learner_id, db=mock_db, repo=mock_repo)


@pytest.mark.asyncio
async def test_get_request_id():
    mock_req = MagicMock(spec=Request)
    mock_req.headers = {"X-Request-ID": "req-xyz-123"}
    with patch("app.core.context.get_request_id", return_value=None):
        rid = await get_request_id(mock_req)
        assert rid == "req-xyz-123"
