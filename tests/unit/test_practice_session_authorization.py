from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock

from app.models import PracticeSession
from app.modules.practice import router as practice_router
from app.modules.practice.router import PracticeResponseRequest
from app.repositories.practice_session_repository import PracticeSessionRepository


@pytest.mark.asyncio
async def test_next_practice_item_rejects_wrong_session_owner(monkeypatch):
    """Test that next_practice_item rejects access from wrong user (owner_subject mismatch)"""
    learner_id = str(uuid4())
    item_id = str(uuid4())
    session_id = str(uuid4())

    # Create a mock session
    session = MagicMock(spec=PracticeSession)
    session.id = session_id
    session.learner_id = learner_id
    session.owner_subject = learner_id  # Owner is learner_id
    session.items = [item_id]
    session.cursor = 0
    session.responses = []
    session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    # Mock repository to return the session
    mock_repo = AsyncMock(spec=PracticeSessionRepository)
    mock_repo.get_by_id.return_value = session

    # Mock db session
    mock_db = AsyncMock()

    # Inject mock repository
    monkeypatch.setattr(practice_router, "PracticeSessionRepository", lambda db: mock_repo)

    # Try to access with different owner
    with pytest.raises(HTTPException) as exc:
        await practice_router.next_practice_item(
            session_id,
            current_user={"sub": str(uuid4()), "role": "learner"},  # Different subject
            db=mock_db,
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_next_practice_item_requires_consent_for_session_owner(monkeypatch):
    """Test that next_practice_item checks active consent for session owner"""
    learner_id = str(uuid4())
    item_id = str(uuid4())
    session_id = str(uuid4())
    owner_subject = learner_id

    # Create a mock session
    session = MagicMock(spec=PracticeSession)
    session.id = session_id
    session.learner_id = learner_id
    session.owner_subject = owner_subject
    session.items = [item_id]
    session.cursor = 0
    session.responses = []
    session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    # Mock repository to return the session
    mock_repo = AsyncMock(spec=PracticeSessionRepository)
    mock_repo.get_by_id.return_value = session

    # Mock db session
    mock_db = AsyncMock()

    # Track consent check calls
    consent_calls = []

    async def mock_consent_check(db, current_user, checked_learner_id):
        consent_calls.append((db, current_user, checked_learner_id))

    monkeypatch.setattr(practice_router, "require_active_consent_for_current_user", mock_consent_check)
    monkeypatch.setattr(practice_router, "PracticeSessionRepository", lambda db: mock_repo)

    result = await practice_router.next_practice_item(
        session_id,
        current_user={"sub": owner_subject, "role": "learner", "learner_id": learner_id},
        db=mock_db,
    )

    assert result == {"completed": False, "item_id": item_id}
    assert consent_calls and consent_calls[0][2] == learner_id


@pytest.mark.asyncio
async def test_respond_practice_rejects_wrong_session_owner_without_advancing(monkeypatch):
    """Test that respond_practice rejects access from wrong user without advancing session"""
    learner_id = str(uuid4())
    item_id = str(uuid4())
    session_id = str(uuid4())

    # Create a mock session
    session = MagicMock(spec=PracticeSession)
    session.id = session_id
    session.learner_id = learner_id
    session.owner_subject = learner_id  # Owner is learner_id
    session.items = [item_id]
    session.cursor = 0
    session.responses = []
    session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    # Mock repository
    mock_repo = AsyncMock(spec=PracticeSessionRepository)
    mock_repo.get_by_id.return_value = session

    # Mock db session
    mock_db = AsyncMock()

    # Inject mock repository
    monkeypatch.setattr(practice_router, "PracticeSessionRepository", lambda db: mock_repo)

    # Try to respond with different owner
    with pytest.raises(HTTPException) as exc:
        await practice_router.respond_practice(
            session_id,
            PracticeResponseRequest(item_id=uuid4(), correct=True),
            current_user={"sub": str(uuid4()), "role": "learner"},  # Different subject
            db=mock_db,
        )

    assert exc.value.status_code == 403
    # Verify repository was not called to update
    mock_repo.update_cursor_and_responses.assert_not_called()


@pytest.mark.asyncio
async def test_respond_practice_requires_consent_before_advancing(monkeypatch):
    """Test that respond_practice checks active consent before advancing session"""
    learner_id = str(uuid4())
    item_id_1 = str(uuid4())
    item_id_2 = str(uuid4())  # Use 2 items to avoid immediate completion
    session_id = str(uuid4())
    owner_subject = learner_id

    # Create a mock session with 2 items
    session = MagicMock(spec=PracticeSession)
    session.id = session_id
    session.learner_id = learner_id
    session.owner_subject = owner_subject
    session.items = [item_id_1, item_id_2]
    session.cursor = 0
    session.responses = []
    session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    # Mock repository
    mock_repo = AsyncMock(spec=PracticeSessionRepository)
    mock_repo.get_by_id.return_value = session
    mock_repo.update_cursor_and_responses.return_value = True

    # Mock db session
    mock_db = AsyncMock()

    # Track consent check calls
    consent_calls = []

    async def mock_consent_check(db, current_user, checked_learner_id):
        consent_calls.append((db, current_user, checked_learner_id))

    monkeypatch.setattr(practice_router, "require_active_consent_for_current_user", mock_consent_check)
    monkeypatch.setattr(practice_router, "PracticeSessionRepository", lambda db: mock_repo)

    result = await practice_router.respond_practice(
        session_id,
        PracticeResponseRequest(item_id=item_id_1, correct=False),
        current_user={"sub": owner_subject, "role": "learner", "learner_id": learner_id},
        db=mock_db,
    )

    # Should return "accepted" (not completed since we have 2 items)
    assert result.get("accepted") == True
    assert consent_calls and consent_calls[0][2] == learner_id
    # Verify repository was called to update with new cursor=1 and response
    mock_repo.update_cursor_and_responses.assert_called_once()
    call_args = mock_repo.update_cursor_and_responses.call_args
    assert call_args[0][1] == 1  # new_cursor should be 1
    assert len(call_args[0][2]) == 1  # 1 response
    assert call_args[0][2][0]["correct"] == False
