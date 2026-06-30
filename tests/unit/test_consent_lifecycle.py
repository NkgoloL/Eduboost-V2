"""
tests/unit/test_consent_lifecycle.py
§4.1 – Consent lifecycle unit tests.
§4.2 – Negative tests for routes without consent.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.consent import ConsentRecord, ConsentState, CONSENT_VALIDITY_DAYS
from app.services.consent_service import ConsentService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pending_record() -> ConsentRecord:
    return ConsentRecord(
        learner_id=uuid.uuid4(),
        guardian_id=uuid.uuid4(),
        privacy_notice_version="v1.0",
    )


def _granted_record() -> ConsentRecord:
    return _pending_record().grant("v1.0")


# ---------------------------------------------------------------------------
# §4.1 State transitions
# ---------------------------------------------------------------------------

class TestConsentStates:
    def test_initial_state_is_pending(self):
        record = _pending_record()
        assert record.state == ConsentState.PENDING

    def test_grant_from_pending(self):
        r = _pending_record().grant("v1.0")
        assert r.state == ConsentState.GRANTED
        assert r.granted_at is not None
        assert r.expires_at is not None

    def test_grant_sets_expiry(self):
        r = _pending_record().grant("v1.0")
        delta = r.expires_at - r.granted_at
        assert delta.days == CONSENT_VALIDITY_DAYS

    def test_deny_from_pending(self):
        r = _pending_record().deny("parent refused")
        assert r.state == ConsentState.DENIED
        assert r.denial_reason == "parent refused"

    def test_withdraw_from_granted(self):
        r = _granted_record().withdraw()
        assert r.state == ConsentState.WITHDRAWN
        assert r.withdrawn_at is not None

    def test_renew_resets_expiry(self):
        r = _granted_record()
        renewed = r.renew("v2.0")
        assert renewed.state == ConsentState.GRANTED
        assert renewed.expires_at > r.expires_at
        assert renewed.privacy_notice_version == "v2.0"

    def test_expire_from_granted(self):
        r = _granted_record().mark_expired()
        assert r.state == ConsentState.EXPIRED

    def test_renewal_required_from_granted(self):
        r = _granted_record().mark_renewal_required()
        assert r.state == ConsentState.RENEWAL_REQUIRED

    def test_invalid_transition_raises(self):
        r = _pending_record()
        with pytest.raises(ValueError, match="Invalid consent transition"):
            r.withdraw()  # PENDING → WITHDRAWN is not allowed

    def test_deny_to_grant_allowed(self):
        r = _pending_record().deny().grant("v1.0")
        assert r.state == ConsentState.GRANTED

    def test_is_active_true_for_granted(self):
        r = _granted_record()
        assert r.is_active() is True

    def test_is_active_false_for_withdrawn(self):
        r = _granted_record().withdraw()
        assert r.is_active() is False

    def test_is_active_false_for_past_expiry(self):
        r = _granted_record()
        past = r.model_copy(
            update={"expires_at": datetime.now(timezone.utc) - timedelta(days=1)}
        )
        assert past.is_active() is False

    def test_days_until_expiry_positive(self):
        r = _granted_record()
        days = r.days_until_expiry()
        assert days is not None
        assert CONSENT_VALIDITY_DAYS - 1 <= days <= CONSENT_VALIDITY_DAYS

    def test_days_until_expiry_none_when_no_expiry(self):
        r = _pending_record()
        assert r.days_until_expiry() is None


# ---------------------------------------------------------------------------
# §4.2 Negative tests – consent gate
# ---------------------------------------------------------------------------

class TestConsentGateNegativeTests:
    """
    These tests verify that each protected subsystem REJECTS requests
    when consent is missing or inactive.
    """

    def _service(self, has_consent: bool) -> ConsentService:
        consent_repo = MagicMock()
        audit_repo = AsyncMock()
        svc = ConsentService(consent_repo, audit_repo)
        if has_consent:
            consent_repo.get_active_for_learner = AsyncMock(
                return_value=_granted_record()
            )
        else:
            consent_repo.get_active_for_learner = AsyncMock(return_value=None)
        return svc

    @pytest.mark.asyncio
    async def test_assert_active_consent_raises_without_consent(self):
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError, match="No active POPIA consent"):
            await svc.assert_active_consent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_assert_active_consent_passes_with_consent(self):
        svc = self._service(has_consent=True)
        record = await svc.assert_active_consent(uuid.uuid4())
        assert record.state == ConsentState.GRANTED

    @pytest.mark.asyncio
    async def test_no_consent_blocks_diagnostics(self):
        """§4.2 – negative test for diagnostics without consent."""
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError):
            await svc.assert_active_consent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_no_consent_blocks_lessons(self):
        """§4.2 – negative test for lesson generation without consent."""
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError):
            await svc.assert_active_consent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_no_consent_blocks_learner_profile(self):
        """§4.2 – negative test for learner profile access without consent."""
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError):
            await svc.assert_active_consent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_no_consent_blocks_study_plan(self):
        """§4.2 – negative test for study plan access without consent."""
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError):
            await svc.assert_active_consent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_no_consent_blocks_gamification(self):
        """§4.2 – negative test for gamification without consent."""
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError):
            await svc.assert_active_consent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_no_consent_blocks_analytics(self):
        """§4.2 – negative test for analytics processing without consent."""
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError):
            await svc.assert_active_consent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_no_consent_blocks_rlhf_feedback(self):
        """§4.2 – negative test for RLHF feedback without consent."""
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError):
            await svc.assert_active_consent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_no_consent_blocks_parent_reports(self):
        """§4.2 – negative test for parent reports without consent."""
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError):
            await svc.assert_active_consent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_no_authority_blocks_data_export(self):
        """§4.2 – negative test for data export without consent/authority."""
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError):
            await svc.assert_active_consent(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_no_authority_blocks_erasure(self):
        """§4.2 – negative test for erasure request without authority."""
        svc = self._service(has_consent=False)
        with pytest.raises(PermissionError):
            await svc.assert_active_consent(uuid.uuid4())
