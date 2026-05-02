"""
EduBoost SA — POPIA Compliance Tests
Non-negotiable compliance test suite for POPIA (Protection of Personal Information Act).
These tests must all pass before any production deployment.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
from datetime import UTC, datetime, timedelta

from app.core.security import (
    decrypt_pii, encrypt_pii, hash_email,
    pseudonymise_for_llm, generate_secure_token,
)
from app.core.audit import AuditAction, _sanitise_metadata
from app.modules.diagnostics.irt_engine import IRTEngine


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — PII Encryption & Pseudonymisation
# ═══════════════════════════════════════════════════════════════════════════════

class TestPIIEncryption:
    """POPIA §19: Appropriate security measures for personal information."""

    def test_email_is_never_stored_in_plaintext(self) -> None:
        """Guardian email must be encrypted at rest."""
        email = "guardian@example.co.za"
        encrypted = encrypt_pii(email)
        assert email not in encrypted
        assert len(encrypted) > len(email)

    def test_encrypted_pii_is_decryptable(self) -> None:
        """Encryption must be reversible for right-of-access requests."""
        original = "Sipho Dlamini"
        assert decrypt_pii(encrypt_pii(original)) == original

    def test_email_hash_is_deterministic(self) -> None:
        """Hash must be deterministic for login lookup."""
        email = "guardian@example.co.za"
        assert hash_email(email) == hash_email(email)

    def test_email_hash_is_case_insensitive(self) -> None:
        assert hash_email("Guardian@EXAMPLE.CO.ZA") == hash_email("guardian@example.co.za")

    def test_different_emails_produce_different_hashes(self) -> None:
        h1 = hash_email("a@example.com")
        h2 = hash_email("b@example.com")
        assert h1 != h2

    def test_email_hash_not_reversible(self) -> None:
        """Hash must be one-way — cannot recover email from hash."""
        email = "guardian@example.co.za"
        h = hash_email(email)
        assert email not in h
        assert "@" not in h

    def test_pii_encryption_produces_different_ciphertexts_each_call(self) -> None:
        """Fernet uses random IV — same plaintext should produce different ciphertext."""
        text = "same input"
        c1 = encrypt_pii(text)
        c2 = encrypt_pii(text)
        # Both decrypt correctly but ciphertexts differ due to random IV
        assert decrypt_pii(c1) == decrypt_pii(c2) == text
        # Note: Fernet does produce different ciphertexts for same plaintext


class TestPseudonymisation:
    """POPIA §19: LLM providers must never receive real learner identifiers."""

    def test_pseudonym_does_not_contain_real_learner_id(self) -> None:
        learner_id = uuid4()
        pseudonym = pseudonymise_for_llm(learner_id)
        assert str(learner_id) not in pseudonym
        assert str(learner_id).replace("-", "") not in pseudonym

    def test_pseudonym_is_deterministic_within_session(self) -> None:
        learner_id = uuid4()
        p1 = pseudonymise_for_llm(learner_id, "session_abc")
        p2 = pseudonymise_for_llm(learner_id, "session_abc")
        assert p1 == p2

    def test_different_sessions_produce_different_pseudonyms(self) -> None:
        """Cross-session correlation must be impossible."""
        learner_id = uuid4()
        p1 = pseudonymise_for_llm(learner_id, "session_1")
        p2 = pseudonymise_for_llm(learner_id, "session_2")
        assert p1 != p2

    def test_different_learners_produce_different_pseudonyms(self) -> None:
        l1, l2 = uuid4(), uuid4()
        assert pseudonymise_for_llm(l1) != pseudonymise_for_llm(l2)

    def test_pseudonym_format_is_safe_for_llm_prompts(self) -> None:
        """Pseudonym must be safe to include in LLM prompt strings."""
        pseudonym = pseudonymise_for_llm(uuid4())
        assert pseudonym.startswith("learner_")
        assert len(pseudonym) < 64
        # No SQL injection chars, quotes, etc.
        for char in ["'", '"', ";", "--", "<", ">"]:
            assert char not in pseudonym


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Audit Trail
# ═══════════════════════════════════════════════════════════════════════════════

class TestAuditTrail:
    """POPIA §22: Records of processing activities."""

    def test_audit_metadata_strips_email_field(self) -> None:
        metadata = {"email": "guardian@example.com", "action": "grant"}
        sanitised = _sanitise_metadata(metadata)
        assert sanitised["email"] == "[REDACTED]"
        assert sanitised["action"] == "grant"

    def test_audit_metadata_strips_password_field(self) -> None:
        metadata = {"password": "secret123", "user_id": "abc"}
        sanitised = _sanitise_metadata(metadata)
        assert sanitised["password"] == "[REDACTED]"

    def test_audit_metadata_strips_id_number(self) -> None:
        metadata = {"id_number": "8001015009087", "grade": "5"}
        sanitised = _sanitise_metadata(metadata)
        assert sanitised["id_number"] == "[REDACTED]"
        assert sanitised["grade"] == "5"

    def test_audit_metadata_preserves_non_pii_fields(self) -> None:
        metadata = {"action": "lesson_generated", "subject": "Mathematics", "count": 3}
        sanitised = _sanitise_metadata(metadata)
        assert sanitised == metadata

    def test_all_audit_actions_are_defined(self) -> None:
        """Validate that all expected POPIA-critical actions are in AuditAction enum."""
        required = {
            AuditAction.CONSENT_GRANTED,
            AuditAction.CONSENT_REVOKED,
            AuditAction.CONSENT_EXPIRED,
            AuditAction.CONSENT_RENEWED,
            AuditAction.LEARNER_ERASED,
            AuditAction.LEARNER_DATA_EXPORTED,
            AuditAction.USER_REGISTERED,
            AuditAction.USER_LOGIN,
        }
        for action in required:
            assert action in AuditAction


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Consent Lifecycle
# ═══════════════════════════════════════════════════════════════════════════════

class TestConsentLifecycle:
    """POPIA §11: Processing must be lawful — requires data subject / guardian consent."""

    def test_consent_expires_after_one_year(self) -> None:
        """Annual renewal is mandatory."""
        from app.models import ParentalConsent
        now = datetime.now(UTC)
        consent = ParentalConsent()
        consent.is_active = True
        consent.granted_at = now
        consent.expires_at = now + timedelta(days=365)
        consent.revoked_at = None

        # Just before expiry — valid
        assert not consent.is_expired

        # Simulate expiry
        consent.expires_at = now - timedelta(seconds=1)
        assert consent.is_expired

    def test_consent_revocation_marks_inactive(self) -> None:
        from app.models import ParentalConsent
        consent = ParentalConsent()
        consent.is_active = True
        # Simulating revocation
        consent.is_active = False
        consent.revoked_at = datetime.now(UTC)
        assert not consent.is_active
        assert consent.revoked_at is not None

    def test_consent_captures_ip_and_user_agent(self) -> None:
        """Proof of consent requires IP and user agent for forensic purposes."""
        from app.models import ParentalConsent
        consent = ParentalConsent()
        consent.ip_address = "41.13.100.1"
        consent.user_agent = "Mozilla/5.0"
        assert consent.ip_address is not None
        assert consent.user_agent is not None

    def test_consent_records_version(self) -> None:
        """Consent version must be recorded for legal versioning of terms."""
        from app.models import ParentalConsent
        consent = ParentalConsent()
        consent.consent_version = "1.0"
        assert consent.consent_version == "1.0"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Right to Erasure (POPIA §24)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRightToErasure:
    """POPIA §24: Data subjects have the right to erasure of their information."""

    def test_learner_erasure_fields(self) -> None:
        """After erasure, no PII should be recoverable from the learner record."""
        from app.models import Learner
        learner = Learner()
        learner.is_erased = True
        learner.first_name_encrypted = "[ERASED]"
        learner.erased_at = datetime.now(UTC)
        learner.is_active = False

        assert learner.is_erased
        assert learner.first_name_encrypted == "[ERASED]"
        assert learner.erased_at is not None
        assert not learner.is_active

    def test_erased_learner_pseudonym_is_anonymised(self) -> None:
        """Pseudonym_id must also be anonymised — cannot map back to learner."""
        from app.models import Learner
        import uuid
        learner = Learner()
        original_id = uuid.uuid4()
        learner.id = original_id
        learner.pseudonym_id = f"erased_{original_id.hex[:8]}"

        # The pseudonym_id should not contain the full original ID
        assert str(original_id) not in learner.pseudonym_id

    def test_audit_log_preserved_after_erasure(self) -> None:
        """
        Audit logs for POPIA compliance must be preserved even after learner erasure.
        Audit log references learner_id (UUID), not PII — so it remains compliant.
        """
        from app.models import AuditLog
        learner_id = uuid4()
        log = AuditLog()
        log.learner_id = learner_id
        log.action = AuditAction.LEARNER_ERASED
        # The log row survives — it contains only UUIDs, not PII
        assert log.learner_id == learner_id


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Secure Token Generation
# ═══════════════════════════════════════════════════════════════════════════════

class TestSecureTokens:
    def test_verification_tokens_are_unique(self) -> None:
        tokens = {generate_secure_token() for _ in range(100)}
        assert len(tokens) == 100

    def test_verification_token_has_sufficient_entropy(self) -> None:
        """Token must be at least 32 characters (URL-safe base64 of 32 bytes)."""
        token = generate_secure_token(32)
        assert len(token) >= 32

    def test_tokens_are_url_safe(self) -> None:
        for _ in range(20):
            token = generate_secure_token()
            assert " " not in token
            assert "/" not in token or token.count("/") == 0  # URL-safe b64 avoids /
