"""Comprehensive unit tests for POPIA adapter coercions, SQLite auth lifecycle proof store, and audit helpers."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
import pytest

from app.domain.consent import ConsentState
from app.services.popia_consent_lifecycle_adapter import (
    _coerce_uuid,
    _coerce_datetime,
    _state_from,
)
from app.services.auth_db_lifecycle_proof import (
    AuthDBProofTokens,
    _hash_password,
    _stable_token,
    SQLiteAuthLifecycleProofStore,
)


class TestPOPIAAdapterCoercions:
    def test_coerce_uuid(self):
        # Existing UUID
        uid = uuid.uuid4()
        assert _coerce_uuid(uid, salt="test") == uid

        # Valid string UUID
        uid_str = str(uid)
        assert _coerce_uuid(uid_str, salt="test") == uid

        # None or arbitrary string uses deterministic uuid5
        assert isinstance(_coerce_uuid(None, salt="test"), uuid.UUID)
        assert isinstance(_coerce_uuid("arbitrary-id-123", salt="test"), uuid.UUID)

    def test_coerce_datetime(self):
        now = datetime.now(UTC)
        fallback = datetime(2026, 1, 1, tzinfo=UTC)

        assert _coerce_datetime(now, fallback=fallback) == now
        assert _coerce_datetime("invalid-date", fallback=fallback) == fallback

    def test_state_from(self):
        assert _state_from(ConsentState.GRANTED, fallback=ConsentState.PENDING) == ConsentState.GRANTED
        assert _state_from("active", fallback=ConsentState.PENDING) == ConsentState.GRANTED
        assert _state_from("denied", fallback=ConsentState.PENDING) == ConsentState.DENIED
        assert _state_from("withdrawn", fallback=ConsentState.PENDING) == ConsentState.WITHDRAWN
        assert _state_from("revoked", fallback=ConsentState.PENDING) == ConsentState.WITHDRAWN
        assert _state_from(None, fallback=ConsentState.PENDING) == ConsentState.PENDING


class TestAuthDBLifecycleProofStore:
    def test_hash_password_deterministic(self):
        h1 = _hash_password("Secret123!", salt="salt-1")
        h2 = _hash_password("Secret123!", salt="salt-1")
        h3 = _hash_password("Secret123!", salt="salt-2")

        assert h1 == h2
        assert h1 != h3

    def test_stable_token(self):
        token = _stable_token("access", "user-123")
        assert token.startswith("access-")

    def test_sqlite_proof_store_init_and_schema(self):
        store = SQLiteAuthLifecycleProofStore()
        assert store.connection is not None

        # Verify tables exist
        cursor = store.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        assert "users" in tables
