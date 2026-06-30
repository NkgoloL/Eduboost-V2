"""
tests/unit/test_consent_repository_contract.py
─────────────────────────────────────────────────────────────────────────────
Task 135A: ConsentRepository contract tests

Validates:
  - get_active_for_learner() returns most recent active consent
  - get_by_id() returns consent record or None
  - create() persists consent record
  - update() modifies consent state and metadata
  - list_expiring_soon() returns consents expiring within window
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

import pytest
from unittest.mock import AsyncMock

from app.domain.consent import ConsentRecord, ConsentState
from app.repositories.consent_repository import ConsentRepository


class TestConsentRepositoryGetActiveForLearner:

    @pytest.mark.asyncio
    async def test_get_active_for_learner_returns_record(self):
        """get_active_for_learner() must return most recent consent for learner."""
        pool = AsyncMock()
        learner_id = uuid.uuid4()
        record_id = uuid.uuid4()
        guardian_id = uuid.uuid4()

        row = {
            "id": record_id,
            "learner_id": learner_id,
            "guardian_id": guardian_id,
            "privacy_notice_version": "2.0",
            "state": "granted",
            "granted_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "withdrawn_at": None,
            "denial_reason": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        pool.fetchrow = AsyncMock(return_value=row)

        repo = ConsentRepository(pool)
        result = await repo.get_active_for_learner(learner_id)

        assert result is not None
        assert result.id == record_id
        assert result.learner_id == learner_id
        assert result.state == ConsentState.GRANTED

    @pytest.mark.asyncio
    async def test_get_active_for_learner_returns_none_when_no_records(self):
        """get_active_for_learner() must return None when no consent exists."""
        pool = AsyncMock()
        pool.fetchrow = AsyncMock(return_value=None)

        repo = ConsentRepository(pool)
        result = await repo.get_active_for_learner(uuid.uuid4())

        assert result is None


class TestConsentRepositoryGetById:

    @pytest.mark.asyncio
    async def test_get_by_id_returns_record(self):
        """get_by_id() must return consent record when it exists."""
        pool = AsyncMock()
        record_id = uuid.uuid4()
        learner_id = uuid.uuid4()

        row = {
            "id": record_id,
            "learner_id": learner_id,
            "guardian_id": uuid.uuid4(),
            "privacy_notice_version": "2.0",
            "state": "granted",
            "granted_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "withdrawn_at": None,
            "denial_reason": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        pool.fetchrow = AsyncMock(return_value=row)

        repo = ConsentRepository(pool)
        result = await repo.get_by_id(record_id)

        assert result is not None
        assert result.id == record_id

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_missing(self):
        """get_by_id() must return None when record does not exist."""
        pool = AsyncMock()
        pool.fetchrow = AsyncMock(return_value=None)

        repo = ConsentRepository(pool)
        result = await repo.get_by_id(uuid.uuid4())

        assert result is None


class TestConsentRepositoryCreate:

    @pytest.mark.asyncio
    async def test_create_persists_record(self):
        """create() must persist consent record to database."""
        pool = AsyncMock()
        pool.execute = AsyncMock()

        record = ConsentRecord(
            id=uuid.uuid4(),
            learner_id=uuid.uuid4(),
            guardian_id=uuid.uuid4(),
            privacy_notice_version="2.0",
            state=ConsentState.GRANTED,
            granted_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            withdrawn_at=None,
            denial_reason=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        repo = ConsentRepository(pool)
        result = await repo.create(record)

        assert result.id == record.id
        pool.execute.assert_awaited_once()


class TestConsentRepositoryUpdate:

    @pytest.mark.asyncio
    async def test_update_modifies_record(self):
        """update() must modify consent state and metadata."""
        pool = AsyncMock()
        pool.execute = AsyncMock()

        record = ConsentRecord(
            id=uuid.uuid4(),
            learner_id=uuid.uuid4(),
            guardian_id=uuid.uuid4(),
            privacy_notice_version="2.0",
            state=ConsentState.WITHDRAWN,
            granted_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            withdrawn_at=datetime.now(timezone.utc),
            denial_reason="parent_request",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        repo = ConsentRepository(pool)
        result = await repo.update(record)

        assert result.id == record.id
        assert result.state == ConsentState.WITHDRAWN
        pool.execute.assert_awaited_once()


class TestConsentRepositoryListExpiringSoon:

    @pytest.mark.asyncio
    async def test_list_expiring_soon_returns_records(self):
        """list_expiring_soon() must return consents expiring within window."""
        pool = AsyncMock()
        record_id = uuid.uuid4()

        row = {
            "id": record_id,
            "learner_id": uuid.uuid4(),
            "guardian_id": uuid.uuid4(),
            "privacy_notice_version": "2.0",
            "state": "granted",
            "granted_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=15),
            "withdrawn_at": None,
            "denial_reason": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        pool.fetch = AsyncMock(return_value=[row])

        repo = ConsentRepository(pool)
        result = await repo.list_expiring_soon(within_days=30)

        assert len(result) == 1
        assert result[0].id == record_id
        assert result[0].state == ConsentState.GRANTED

    @pytest.mark.asyncio
    async def test_list_expiring_soon_returns_empty_when_none(self):
        """list_expiring_soon() must return empty list when no consents expiring."""
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])

        repo = ConsentRepository(pool)
        result = await repo.list_expiring_soon(within_days=30)

        assert len(result) == 0
