from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models import ConsentState
from app.repositories.repositories import ConsentRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_latest_for_learner_returns_scalar_value():
    db = MagicMock()
    expected = SimpleNamespace(id="consent-1")
    result_obj = MagicMock()
    result_obj.scalar_one_or_none.return_value = expected
    db.execute = AsyncMock(return_value=result_obj)

    repo = ConsentRepository(db)
    result = await repo.get_latest_for_learner("learner-1")

    assert result is expected
    db.execute.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_grant_creates_parental_consent_and_flushes():
    db = MagicMock()
    db.flush = AsyncMock()
    repo = ConsentRepository(db)

    consent = await repo.grant(
        learner_id="learner-1",
        guardian_id="guardian-1",
        consent_version="2.0.0",
        ip_address="127.0.0.1",
        user_agent="pytest",
        state="granted",
    )

    assert consent.learner_id == "learner-1"
    assert consent.guardian_id == "guardian-1"
    assert consent.policy_version == "2.0.0"
    assert consent.ip_address_hash == "127.0.0.1"
    assert consent.status in {ConsentState.GRANTED, "granted"}
    db.add.assert_called_once()
    db.flush.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_revoke_returns_rowcount():
    db = MagicMock()
    db.execute = AsyncMock(return_value=SimpleNamespace(rowcount=3))

    repo = ConsentRepository(db)
    count = await repo.revoke("learner-1", reason="withdrawn")

    assert count == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_renew_revokes_previous_and_grants_new_when_active_exists():
    db = MagicMock()
    repo = ConsentRepository(db)

    previous = SimpleNamespace(id="consent-old")
    renewed = SimpleNamespace(id="consent-new")

    repo.get_active = AsyncMock(return_value=previous)
    repo.revoke = AsyncMock(return_value=1)
    repo.grant = AsyncMock(return_value=renewed)

    prev, new = await repo.renew("learner-1", "guardian-1", "3.0.0")

    assert prev is previous
    assert new is renewed
    repo.revoke.assert_awaited_once_with("learner-1", reason="renewed")
    repo.grant.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_renew_skips_revoke_when_no_active_consent():
    db = MagicMock()
    repo = ConsentRepository(db)

    renewed = SimpleNamespace(id="consent-new")

    repo.get_active = AsyncMock(return_value=None)
    repo.revoke = AsyncMock(return_value=0)
    repo.grant = AsyncMock(return_value=renewed)

    prev, new = await repo.renew("learner-1", "guardian-1", "3.0.0")

    assert prev is None
    assert new is renewed
    repo.revoke.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_expiring_soon_uses_provided_db_session_when_present():
    primary_db = MagicMock()
    override_db = MagicMock()

    result_obj = MagicMock()
    result_obj.scalars.return_value.all.return_value = [SimpleNamespace(id="consent-1")]
    override_db.execute = AsyncMock(return_value=result_obj)
    primary_db.execute = AsyncMock()

    repo = ConsentRepository(primary_db)
    results = await repo.get_expiring_soon(db=override_db, days=7)

    assert len(results) == 1
    override_db.execute.assert_awaited_once()
    primary_db.execute.assert_not_called()
