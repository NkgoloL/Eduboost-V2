"""
tests/unit/test_audit_integrity.py
§4.5 – Audit chain integrity: hashing, HMAC, chain verification.
"""
from __future__ import annotations



from app.domain.consent import AuditEventType
from app.repositories.audit_repository import (
    _compute_hash,
    _compute_hmac,
    configure_hmac_secret,
)


configure_hmac_secret(b"test-secret-key-for-unit-tests")


class TestAuditHashing:
    def test_compute_hash_deterministic(self):
        payload = {"event_id": "abc", "event_type": "login_success"}
        h1 = _compute_hash(payload)
        h2 = _compute_hash(payload)
        assert h1 == h2

    def test_compute_hash_changes_with_payload(self):
        h1 = _compute_hash({"x": 1})
        h2 = _compute_hash({"x": 2})
        assert h1 != h2

    def test_compute_hmac_deterministic(self):
        m1 = _compute_hmac("hash-abc", "GENESIS")
        m2 = _compute_hmac("hash-abc", "GENESIS")
        assert m1 == m2

    def test_compute_hmac_changes_with_previous_hash(self):
        m1 = _compute_hmac("hash-abc", "GENESIS")
        m2 = _compute_hmac("hash-abc", "different-previous")
        assert m1 != m2


class TestAuditEventContracts:
    """
    §4.5 – Verify that all required audit event types are defined.
    Mirrors scripts/check_audit_event_contracts.py.
    """

    REQUIRED_EVENTS = [
        AuditEventType.LOGIN_SUCCESS,
        AuditEventType.LOGIN_FAILURE,
        AuditEventType.TOKEN_REFRESH,
        AuditEventType.LOGOUT,
        AuditEventType.CONSENT_GRANT,
        AuditEventType.CONSENT_RENEWAL,
        AuditEventType.CONSENT_WITHDRAWAL,
        AuditEventType.CONSENT_EXPIRY,
        AuditEventType.CONSENT_DENIAL,
        AuditEventType.LEARNER_PROFILE_CREATE,
        AuditEventType.LEARNER_PROFILE_UPDATE,
        AuditEventType.LEARNER_PROFILE_DELETE,
        AuditEventType.DIAGNOSTIC_START,
        AuditEventType.DIAGNOSTIC_ANSWER,
        AuditEventType.DIAGNOSTIC_COMPLETE,
        AuditEventType.LESSON_GENERATION,
        AuditEventType.LLM_PROVIDER_CALL,
        AuditEventType.PARENT_REPORT_GENERATION,
        AuditEventType.DATA_EXPORT_REQUEST,
        AuditEventType.DATA_EXPORT_DOWNLOAD,
        AuditEventType.ERASURE_REQUEST,
        AuditEventType.ERASURE_EXECUTION,
        AuditEventType.ADMIN_ACCESS,
        AuditEventType.BILLING_CHANGE,
    ]

    def test_all_required_event_types_exist(self):
        existing = {e.value for e in AuditEventType}
        for event in self.REQUIRED_EVENTS:
            assert event.value in existing, f"Missing audit event: {event.value}"

    def test_event_values_are_snake_case_strings(self):
        for event in AuditEventType:
            assert event.value == event.value.lower()
            assert " " not in event.value
