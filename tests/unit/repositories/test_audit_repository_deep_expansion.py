"""Comprehensive unit tests for AuditRepository and cryptographic audit hashing/signing."""
from __future__ import annotations

import uuid
import pytest

from app.repositories.audit_repository import (
    compute_audit_hash,
    sign_audit_hash,
    configure_hmac_secret,
)


class TestAuditHashingAndSigning:
    def test_compute_audit_hash_deterministic(self):
        eid = uuid.uuid4()
        aid = uuid.uuid4()
        rid = uuid.uuid4()
        payload = {"action": "consent_grant", "policy": "1.0"}

        h1 = compute_audit_hash(
            event_id=eid,
            event_type="consent_granted",
            actor_id=aid,
            resource_id=rid,
            previous_event_hash="hash_prev_001",
            payload=payload,
        )
        h2 = compute_audit_hash(
            event_id=eid,
            event_type="consent_granted",
            actor_id=aid,
            resource_id=rid,
            previous_event_hash="hash_prev_001",
            payload=payload,
        )
        assert h1 == h2
        assert len(h1) == 64

    def test_compute_audit_hash_chain_tamper_detection(self):
        eid = uuid.uuid4()
        h1 = compute_audit_hash(
            event_id=eid,
            event_type="consent_granted",
            actor_id=None,
            resource_id=None,
            previous_event_hash="hash_prev_001",
            payload={"k": "v"},
        )
        h2 = compute_audit_hash(
            event_id=eid,
            event_type="consent_granted",
            actor_id=None,
            resource_id=None,
            previous_event_hash="hash_prev_tampered",
            payload={"k": "v"},
        )
        assert h1 != h2

    def test_sign_audit_hash_hmac(self):
        secret = "test-hmac-secret-key-32bytes-long"
        event_hash = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"

        sig_str = sign_audit_hash(event_hash, secret)
        sig_bytes = sign_audit_hash(event_hash, secret.encode("utf-8"))

        assert sig_str == sig_bytes
        assert len(sig_str) == 64

    def test_configure_hmac_secret(self):
        configure_hmac_secret(b"new_secret_key")
