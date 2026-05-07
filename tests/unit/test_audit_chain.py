from __future__ import annotations

import uuid

from app.repositories.audit_repository import compute_audit_hash, sign_audit_hash


def test_audit_hash_changes_when_payload_changes() -> None:
    event_id = uuid.uuid4()
    base = dict(
        event_id=event_id,
        event_type="consent.granted",
        actor_id=uuid.uuid4(),
        resource_id=uuid.uuid4(),
        previous_event_hash=None,
    )
    first = compute_audit_hash(payload={"learner_id": "learner-1"}, **base)
    second = compute_audit_hash(payload={"learner_id": "learner-2"}, **base)
    assert first != second


def test_audit_hmac_signature_is_secret_bound() -> None:
    event_hash = "a" * 64
    assert sign_audit_hash(event_hash, "secret-1") != sign_audit_hash(event_hash, "secret-2")
    assert len(sign_audit_hash(event_hash, "secret-1")) == 64
