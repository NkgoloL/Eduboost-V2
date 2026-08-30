import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.domain.consent import AuditEventType
from app.repositories.audit_repository import (
    configure_hmac_secret,
    compute_audit_hash,
    sign_audit_hash,
    _compute_hash,
    _compute_hmac,
    AuditRepository,
)


def test_hmac_and_hash_functions():
    configure_hmac_secret(b"secret-key-12345")
    h = _compute_hash({"action": "CONSENT_GRANTED", "user": "user1"})
    assert isinstance(h, str)
    assert len(h) == 64

    sig = _compute_hmac(h, "prev-hash-000")
    assert isinstance(sig, str)
    assert len(sig) == 64

    custom_sig = sign_audit_hash(h, "custom-secret")
    assert isinstance(custom_sig, str)
    assert len(custom_sig) == 64


def test_compute_audit_hash_deterministic():
    event_id = uuid.uuid4()
    h1 = compute_audit_hash(
        event_id=event_id,
        event_type="LOGIN",
        actor_id="actor1",
        resource_id="res1",
        previous_event_hash=None,
        payload={"k": "v"},
    )
    h2 = compute_audit_hash(
        event_id=event_id,
        event_type="LOGIN",
        actor_id="actor1",
        resource_id="res1",
        previous_event_hash=None,
        payload={"k": "v"},
    )
    assert h1 == h2


@pytest.mark.asyncio
async def test_audit_repository_session_mode():
    db = AsyncMock()
    # Mocking AsyncSession behavior (has 'add')
    db.add = MagicMock()
    repo = AuditRepository(db)
    assert repo._is_async_session is True
