"""Tests for practice session authorization."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import uuid

import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock

from app.models import PracticeSession
from app.modules.practice import router as practice_router
from app.modules.practice.router import PracticeResponseRequest


@pytest.mark.asyncio
async def test_next_practice_item_rejects_wrong_session_owner(monkeypatch):
    """Test that next_practice_item rejects access from wrong user (owner_subject mismatch)"""
    learner_id = str(uuid4())
    item_id = str(uuid4())
    session_id = str(uuid4())

    session = MagicMock(spec=PracticeSession)
    session.id = session_id
    session.learner_id = learner_id
    session.owner_subject = learner_id
    session.items = [item_id]
    session.cursor = 0
    session.responses = []
    session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    mock_service = AsyncMock()
    mock_service.get_session.return_value = session

    mock_db = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await practice_router.next_practice_item(
            session_id,
            current_user={"sub": str(uuid4()), "role": "learner"},
            db=mock_db,
            service=mock_service,
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_next_practice_item_requires_consent_for_session_owner(monkeypatch):
    """Test that next_practice_item checks active consent for session owner"""
    learner_id = str(uuid4())
    item_id = str(uuid4())
    session_id = str(uuid4())
    owner_subject = learner_id

    session = MagicMock(spec=PracticeSession)
    session.id = session_id
    session.learner_id = learner_id
    session.owner_subject = owner_subject
    session.items = [item_id]
    session.cursor = 0
    session.responses = []
    session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    mock_service = AsyncMock()
    mock_service.get_session.return_value = session

    mock_db = AsyncMock()
    consent_calls = []

    async def mock_consent_check(db, current_user, checked_learner_id):
        consent_calls.append((db, current_user, checked_learner_id))

    monkeypatch.setattr(practice_router, "require_active_consent_for_current_user", mock_consent_check)

    result = await practice_router.next_practice_item(
        session_id,
        current_user={"sub": owner_subject, "role": "learner", "learner_id": learner_id},
        db=mock_db,
        service=mock_service,
    )

    assert result == {"completed": False, "item_id": item_id}
    assert consent_calls and consent_calls[0][2] == learner_id


@pytest.mark.asyncio
async def test_respond_practice_rejects_wrong_session_owner_without_advancing(monkeypatch):
    """Test that respond_practice rejects access from wrong user without advancing session"""
    learner_id = str(uuid4())
    item_id = str(uuid4())
    session_id = str(uuid4())

    session = MagicMock(spec=PracticeSession)
    session.id = session_id
    session.learner_id = learner_id
    session.owner_subject = learner_id
    session.items = [item_id]
    session.cursor = 0
    session.responses = []
    session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    mock_service = AsyncMock()
    mock_service.get_session.return_value = session

    mock_db = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await practice_router.respond_practice(
            session_id,
            PracticeResponseRequest(item_id=uuid4(), correct=True),
            current_user={"sub": str(uuid4()), "role": "learner"},
            db=mock_db,
            service=mock_service,
        )

    assert exc.value.status_code == 403
    mock_service.record_response.assert_not_called()


@pytest.mark.asyncio
async def test_respond_practice_requires_consent_before_advancing(monkeypatch):
    """Test that respond_practice checks active consent before advancing session"""
    learner_id = str(uuid4())
    item_id_1 = str(uuid4())
    item_id_2 = str(uuid4())
    session_id = str(uuid4())
    owner_subject = learner_id

    session = MagicMock(spec=PracticeSession)
    session.id = session_id
    session.learner_id = learner_id
    session.owner_subject = owner_subject
    session.items = [item_id_1, item_id_2]
    session.cursor = 0
    session.responses = []
    session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    mock_service = AsyncMock()
    mock_service.get_session.return_value = session
    mock_service.record_response.return_value = {"accepted": True, "next_item_id": item_id_2}

    mock_db = AsyncMock()
    consent_calls = []

    async def mock_consent_check(db, current_user, checked_learner_id):
        consent_calls.append((db, current_user, checked_learner_id))

    monkeypatch.setattr(practice_router, "require_active_consent_for_current_user", mock_consent_check)

    result = await practice_router.respond_practice(
        session_id,
        PracticeResponseRequest(item_id=uuid.UUID(item_id_1), correct=False),
        current_user={"sub": owner_subject, "role": "learner", "learner_id": learner_id},
        db=mock_db,
        service=mock_service,
    )

    assert result.get("accepted") is True
    assert consent_calls and consent_calls[0][2] == learner_id
    mock_service.record_response.assert_called_once()
