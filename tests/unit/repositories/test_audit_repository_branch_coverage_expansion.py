"""Batch 221 — app/repositories/audit_repository.py comprehensive branch coverage expansion.

Tests:
- configure_hmac_secret, compute_audit_hash, sign_audit_hash
- record & append with AsyncSession and asyncpg interfaces
- blank event_type validation error
- _validate_payload PII detection (top-level, nested dict, nested list)
- get_by_resource & get_by_actor with AsyncSession and asyncpg (with and without event_type)
- verify_chain with AsyncSession and asyncpg (clean chain, event_hash mismatch, hmac mismatch, broken chain)
- _latest_hash (None vs resource_id, GENESIS fallback)
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.consent import AuditEventType
from app.models import AuditEvent
from app.repositories.audit_repository import (
    AuditRepository,
    _compute_hash,
    _compute_hmac,
    compute_audit_hash,
    configure_hmac_secret,
    sign_audit_hash,
)


@pytest.fixture(autouse=True)
def setup_hmac():
    configure_hmac_secret(b"test-secret-key-32-bytes-minimum!!")


# ---------------------------------------------------------------------------
# Cryptographic Hash & Signature Functions
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_compute_audit_hash_deterministic():
    event_id = uuid.uuid4()
    h1 = compute_audit_hash(
        event_id=event_id,
        event_type="auth.login",
        actor_id="user-1",
        resource_id="session-1",
        previous_event_hash="prev-hash-123",
        payload={"ip": "127.0.0.1"},
    )
    h2 = compute_audit_hash(
        event_id=event_id,
        event_type="auth.login",
        actor_id="user-1",
        resource_id="session-1",
        previous_event_hash="prev-hash-123",
        payload={"ip": "127.0.0.1"},
    )
    assert h1 == h2
    assert len(h1) == 64

    # With None actor and resource
    h_none = compute_audit_hash(
        event_id=event_id,
        event_type="system.start",
        actor_id=None,
        resource_id=None,
        previous_event_hash=None,
        payload={},
    )
    assert isinstance(h_none, str)


@pytest.mark.unit
def test_sign_audit_hash_with_str_and_bytes():
    event_hash = "a" * 64
    sig_str = sign_audit_hash(event_hash, "secret-key")
    sig_bytes = sign_audit_hash(event_hash, b"secret-key")
    assert sig_str == sig_bytes
    assert len(sig_str) == 64


# ---------------------------------------------------------------------------
# PII Validation in Payloads
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_validate_payload_rejects_pii():
    mock_session = AsyncMock()
    repo = AuditRepository(mock_session)

    # Top-level PII
    with pytest.raises(ValueError, match="PII field names are not permitted in audit payload"):
        repo._validate_payload({"email": "user@example.com"})

    # Nested dict PII
    with pytest.raises(ValueError, match="PII field names are not permitted in audit payload: user.phone"):
        repo._validate_payload({"user": {"phone": "0821234567"}})

    # Nested list PII
    with pytest.raises(ValueError, match="PII field names are not permitted in audit payload"):
        repo._validate_payload({"identities": [{"first_name": "Lethabo"}]})

    # None and safe payload
    repo._validate_payload(None)
    repo._validate_payload({"action_count": 5, "score": 92.5})


# ---------------------------------------------------------------------------
# Record & Append with AsyncSession
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_record_with_async_session():
    mock_session = AsyncMock()
    repo = AuditRepository(mock_session)

    # Mock _latest_hash
    res_latest = MagicMock()
    res_latest.scalar_one_or_none.return_value = "GENESIS"
    mock_session.execute.return_value = res_latest

    # Blank event_type raises ValueError
    with pytest.raises(ValueError, match="event_type must not be blank"):
        await repo.record("   ")

    # Success with AuditEventType enum
    event_id = await repo.record(
        AuditEventType.CONSENT_GRANT,
        actor_id="guardian-1",
        resource_id="learner-1",
        payload={"consent_type": "terms"},
    )
    assert isinstance(event_id, uuid.UUID)
    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_append_with_async_session():
    mock_session = AsyncMock()
    repo = AuditRepository(mock_session)

    res_latest = MagicMock()
    res_latest.scalar_one_or_none.return_value = "prior-hash-123"
    mock_session.execute.return_value = res_latest

    event = await repo.append(
        "auth.login_success",
        actor_id=uuid.uuid4(),
        resource_id=uuid.uuid4(),
        payload={"ip_hash": "abc"},
    )
    assert isinstance(event, AuditEvent)
    assert event.previous_event_hash == "prior-hash-123"
    mock_session.add.assert_called_once()


# ---------------------------------------------------------------------------
# Record & Append with asyncpg Connection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_record_and_append_with_asyncpg():
    mock_pool = MagicMock(spec=["execute", "fetchrow", "fetch"])
    mock_pool.execute = AsyncMock()
    mock_pool.fetchrow = AsyncMock(return_value={"event_hash": "genesis-hash"})
    repo = AuditRepository(mock_pool)

    # Record via pool
    event_id = await repo.record("item.reviewed", actor_id="admin-1")
    assert isinstance(event_id, uuid.UUID)
    mock_pool.execute.assert_called_once()

    # Append via pool
    mock_record = {"id": event_id, "event_type": "item.reviewed"}
    mock_pool.fetchrow.side_effect = [
        {"event_hash": "prev-hash"},  # for _latest_hash
        mock_record,                  # for INSERT ... RETURNING
    ]
    appended = await repo.append("item.reviewed", actor_id="admin-1")
    assert appended == mock_record


# ---------------------------------------------------------------------------
# Queries: get_by_resource & get_by_actor
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_by_resource_and_actor_async_session():
    mock_session = AsyncMock()
    repo = AuditRepository(mock_session)

    mock_event = MagicMock(spec=AuditEvent)
    res = MagicMock()
    res.scalars.return_value.all.return_value = [mock_event]
    mock_session.execute.return_value = res

    # Resource with event_type
    events = await repo.get_by_resource("res-1", event_type="consent.granted")
    assert len(events) == 1

    # Actor without event_type
    events_actor = await repo.get_by_actor("actor-1")
    assert len(events_actor) == 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_by_resource_and_actor_asyncpg():
    mock_pool = MagicMock(spec=["execute", "fetchrow", "fetch"])
    mock_pool.fetch = AsyncMock(return_value=[{"id": "event-1"}])
    repo = AuditRepository(mock_pool)

    # Resource with event_type
    res_items = await repo.get_by_resource("res-1", event_type="consent.granted")
    assert len(res_items) == 1

    # Actor without event_type
    actor_items = await repo.get_by_actor("actor-1")
    assert len(actor_items) == 1


# ---------------------------------------------------------------------------
# verify_chain
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_verify_chain_valid_and_broken_async_session():
    mock_session = AsyncMock()
    repo = AuditRepository(mock_session)

    eid1 = uuid.uuid4()
    p1 = {"step": 1}
    h1 = _compute_hash({
        "event_id": str(eid1),
        "event_type": "event.one",
        "actor_id": "act-1",
        "resource_id": "res-1",
        "previous_event_hash": "GENESIS",
        "payload": p1,
    })
    sig1 = _compute_hmac(h1, "GENESIS")

    event1 = MagicMock(
        id=eid1,
        event_type="event.one",
        actor_id="act-1",
        resource_id="res-1",
        previous_event_hash="GENESIS",
        payload=p1,
        event_hash=h1,
        hmac_signature=sig1,
    )

    eid2 = uuid.uuid4()
    p2 = {"step": 2}
    h2 = _compute_hash({
        "event_id": str(eid2),
        "event_type": "event.two",
        "actor_id": "act-1",
        "resource_id": "res-1",
        "previous_event_hash": h1,
        "payload": p2,
    })
    sig2 = _compute_hmac(h2, h1)

    event2 = MagicMock(
        id=eid2,
        event_type="event.two",
        actor_id="act-1",
        resource_id="res-1",
        previous_event_hash=h1,
        payload=p2,
        event_hash=h2,
        hmac_signature=sig2,
    )

    res_clean = MagicMock()
    res_clean.scalars.return_value.all.return_value = [event1, event2]
    mock_session.execute.return_value = res_clean

    # 1. Clean verification
    ok, errors = await repo.verify_chain(resource_id=uuid.uuid4())
    assert ok is True
    assert len(errors) == 0

    # 2. Corrupted event_hash and HMAC
    event2_corrupted = MagicMock(
        id=eid2,
        event_type="event.two",
        actor_id="act-1",
        resource_id="res-1",
        previous_event_hash="WRONG_PREV",
        payload=p2,
        event_hash="BAD_HASH",
        hmac_signature="BAD_HMAC",
    )
    res_corrupt = MagicMock()
    res_corrupt.scalars.return_value.all.return_value = [event1, event2_corrupted]
    mock_session.execute.return_value = res_corrupt

    ok_corrupt, errors_corrupt = await repo.verify_chain(resource_id=uuid.uuid4())
    assert ok_corrupt is False
    assert len(errors_corrupt) >= 2


@pytest.mark.asyncio
@pytest.mark.unit
async def test_verify_chain_asyncpg():
    mock_pool = MagicMock(spec=["execute", "fetchrow", "fetch"])
    repo = AuditRepository(mock_pool)

    eid1 = uuid.uuid4()
    p1 = {"step": 1}
    h1 = _compute_hash({
        "event_id": str(eid1),
        "event_type": "event.one",
        "actor_id": None,
        "resource_id": None,
        "previous_event_hash": "GENESIS",
        "payload": p1,
    })
    sig1 = _compute_hmac(h1, "GENESIS")

    row1 = {
        "id": eid1,
        "event_type": "event.one",
        "actor_id": None,
        "resource_id": None,
        "previous_event_hash": "GENESIS",
        "payload": json.dumps(p1),
        "event_hash": h1,
        "hmac_signature": sig1,
    }
    mock_pool.fetch = AsyncMock(return_value=[row1])

    ok, errors = await repo.verify_chain()
    assert ok is True
    assert len(errors) == 0
