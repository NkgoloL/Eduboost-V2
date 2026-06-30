"""tests/unit/test_popia_consent_versioning.py
T112B: POPIA consent versioning implementation tests

Verifies consent version tracking, stale consent detection,
version change detection, and version history recording.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ConsentState, ParentalConsent
from app.modules.consent.service import ConsentService
from app.utils.versioning import (
    SemanticVersion,
    VersionChangeType,
    detect_version_change,
    is_same_major_minor,
    requires_manual_renewal,
)


# ── Versioning utility tests ───────────────────────────────────────────────────────


class TestSemanticVersion:
    """Test semantic version parsing and comparison."""

    def test_parse_valid_version(self):
        """Parse valid version strings."""
        v = SemanticVersion.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert str(v) == "1.2.3"

    def test_parse_invalid_format(self):
        """Reject invalid version formats."""
        with pytest.raises(ValueError):
            SemanticVersion.parse("1.2")  # Missing patch
        with pytest.raises(ValueError):
            SemanticVersion.parse("1.2.3.4")  # Too many parts
        with pytest.raises(ValueError):
            SemanticVersion.parse("a.b.c")  # Non-numeric

    def test_version_comparison(self):
        """Test version comparison operators."""
        v1 = SemanticVersion.parse("1.0.0")
        v2 = SemanticVersion.parse("2.0.0")
        v3 = SemanticVersion.parse("1.0.0")

        assert v1 < v2
        assert v2 > v1
        assert v1 == v3
        assert v1 <= v2
        assert v2 >= v1

    def test_detect_version_change_type(self):
        """Detect version change types."""
        v1 = SemanticVersion.parse("1.0.0")

        assert v1.detect_change_type(SemanticVersion.parse("1.0.1")) == VersionChangeType.PATCH
        assert v1.detect_change_type(SemanticVersion.parse("1.1.0")) == VersionChangeType.MINOR
        assert v1.detect_change_type(SemanticVersion.parse("2.0.0")) == VersionChangeType.MAJOR


class TestVersioningUtilities:
    """Test versioning utility functions."""

    def test_detect_version_change(self):
        """Detect version change type from strings."""
        assert detect_version_change("1.0.0", "1.0.1") == VersionChangeType.PATCH
        assert detect_version_change("1.0.0", "1.1.0") == VersionChangeType.MINOR
        assert detect_version_change("1.0.0", "2.0.0") == VersionChangeType.MAJOR

    def test_requires_manual_renewal(self):
        """Determine if manual renewal is required."""
        assert not requires_manual_renewal("1.0.0", "1.0.1")  # PATCH: auto-renew
        assert requires_manual_renewal("1.0.0", "1.1.0")  # MINOR: manual
        assert requires_manual_renewal("1.0.0", "2.0.0")  # MAJOR: manual

    def test_is_same_major_minor(self):
        """Check if versions have same MAJOR.MINOR."""
        assert is_same_major_minor("1.0.0", "1.0.1")
        assert not is_same_major_minor("1.0.0", "1.1.0")
        assert not is_same_major_minor("1.0.0", "2.0.0")


# ── Consent service versioning tests ───────────────────────────────────────────────


class TestConsentVersioning:
    """Test consent service versioning functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock AsyncSession."""
        db = AsyncMock(spec=AsyncSession)
        db.add = MagicMock()
        db.flush = AsyncMock()
        return db

    @pytest.fixture
    def mock_repo(self):
        """Create a mock ConsentRepository."""
        repo = AsyncMock()
        repo.grant = AsyncMock()
        repo.revoke = AsyncMock()
        repo.renew = AsyncMock()
        repo.get_active = AsyncMock()
        repo.get_latest_for_learner = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_db, mock_repo):
        """Create ConsentService with mocked dependencies."""
        return ConsentService(db=mock_db, consent_repo=mock_repo)

    def test_required_policy_version_default(self, service):
        """Service has default required policy version."""
        assert service._required_policy_version == "1.0.0"

    def test_required_policy_version_custom(self, mock_db, mock_repo):
        """Service accepts custom required policy version."""
        service = ConsentService(db=mock_db, consent_repo=mock_repo, required_policy_version="2.0.0")
        assert service._required_policy_version == "2.0.0"

    def test_is_consent_stale_major_change(self, service):
        """Detect stale consent on major version change."""
        service._required_policy_version = "2.0.0"
        assert service._is_consent_stale("1.0.0")

    def test_is_consent_stale_minor_change(self, service):
        """Detect stale consent on minor version change."""
        service._required_policy_version = "1.1.0"
        assert service._is_consent_stale("1.0.0")

    def test_is_consent_stale_patch_change(self, service):
        """Patch changes do not make consent stale."""
        service._required_policy_version = "1.0.1"
        assert not service._is_consent_stale("1.0.0")

    def test_is_consent_stale_invalid_version(self, service):
        """Invalid version format treated as stale (safe default)."""
        service._required_policy_version = "1.0.0"
        assert service._is_consent_stale("invalid")

    def test_detect_version_change_type_patch(self, service):
        """Detect PATCH version change."""
        assert service.detect_version_change_type("1.0.0", "1.0.1") == VersionChangeType.PATCH

    def test_detect_version_change_type_minor(self, service):
        """Detect MINOR version change."""
        assert service.detect_version_change_type("1.0.0", "1.1.0") == VersionChangeType.MINOR

    def test_detect_version_change_type_major(self, service):
        """Detect MAJOR version change."""
        assert service.detect_version_change_type("1.0.0", "2.0.0") == VersionChangeType.MAJOR

    def test_detect_version_change_type_invalid(self, service):
        """Invalid version format treated as MAJOR (safe default)."""
        assert service.detect_version_change_type("invalid", "1.0.0") == VersionChangeType.MAJOR

    @pytest.mark.asyncio
    async def test_consent_decision_stale_consent_blocked(self, service, mock_repo):
        """Stale consent is marked as RENEWAL_REQUIRED and inactive."""
        service._required_policy_version = "2.0.0"

        consent = ParentalConsent(
            id=str(uuid.uuid4()),
            guardian_id=str(uuid.uuid4()),
            learner_id=str(uuid.uuid4()),
            policy_version="1.0.0",
            status=ConsentState.GRANTED,
            granted_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=365),
        )
        mock_repo.get_latest_for_learner.return_value = consent

        decision = await service.consent_decision("learner-123")

        assert not decision.active
        assert decision.state == ConsentState.RENEWAL_REQUIRED
        assert "stale" in decision.reason.lower()

    @pytest.mark.asyncio
    async def test_consent_decision_current_version_allowed(self, service, mock_repo):
        """Current version consent remains active."""
        service._required_policy_version = "1.0.0"

        consent = ParentalConsent(
            id=str(uuid.uuid4()),
            guardian_id=str(uuid.uuid4()),
            learner_id=str(uuid.uuid4()),
            policy_version="1.0.0",
            status=ConsentState.GRANTED,
            granted_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=365),
        )
        mock_repo.get_latest_for_learner.return_value = consent

        decision = await service.consent_decision("learner-123")

        assert decision.active
        assert decision.state == ConsentState.GRANTED

    @pytest.mark.asyncio
    async def test_grant_records_version_history(self, service, mock_repo, mock_db):
        """Granting consent records version history entry."""
        consent = ParentalConsent(
            id=str(uuid.uuid4()),
            guardian_id="guardian-123",
            learner_id="learner-123",
            policy_version="1.0.0",
            status=ConsentState.GRANTED,
            granted_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=365),
        )
        mock_repo.grant.return_value = consent

        await service.grant("guardian-123", "learner-123", "1.0.0")

        # Verify version history was recorded (called twice: audit + version history)
        assert mock_db.add.call_count >= 1
        mock_db.flush.assert_called()

        # Check that one of the calls was for ConsentVersionHistory
        from app.models import ConsentVersionHistory
        version_history_calls = [call for call in mock_db.add.call_args_list if isinstance(call[0][0], ConsentVersionHistory)]
        assert len(version_history_calls) >= 1

    @pytest.mark.asyncio
    async def test_revoke_records_version_history(self, service, mock_repo, mock_db):
        """Revoking consent records version history entry."""
        consent = ParentalConsent(
            id=str(uuid.uuid4()),
            guardian_id="guardian-123",
            learner_id="learner-123",
            policy_version="1.0.0",
            status=ConsentState.GRANTED,
            granted_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=365),
        )
        mock_repo.get_active.return_value = consent
        mock_repo.revoke.return_value = 1

        await service.revoke("learner-123", guardian_id="guardian-123")

        # Verify version history was recorded (called twice: audit + version history)
        assert mock_db.add.call_count >= 1
        mock_db.flush.assert_called()

        # Check that one of the calls was for ConsentVersionHistory
        from app.models import ConsentVersionHistory
        version_history_calls = [call for call in mock_db.add.call_args_list if isinstance(call[0][0], ConsentVersionHistory)]
        assert len(version_history_calls) >= 1

    @pytest.mark.asyncio
    async def test_renew_records_version_history(self, service, mock_repo, mock_db):
        """Renewing consent records version history entry."""
        previous = ParentalConsent(
            id=str(uuid.uuid4()),
            guardian_id="guardian-123",
            learner_id="learner-123",
            policy_version="1.0.0",
            status=ConsentState.GRANTED,
            granted_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=365),
        )
        renewed = ParentalConsent(
            id=str(uuid.uuid4()),
            guardian_id="guardian-123",
            learner_id="learner-123",
            policy_version="2.0.0",
            status=ConsentState.GRANTED,
            granted_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=365),
        )
        mock_repo.get_latest_for_learner.return_value = previous
        mock_repo.renew.return_value = (previous, renewed)

        await service.renew("guardian-123", "learner-123", "2.0.0")

        # Verify version history was recorded for renewed consent
        assert mock_db.add.call_count >= 1
        mock_db.flush.assert_called()
