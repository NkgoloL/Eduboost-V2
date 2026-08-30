"""Batch 193: Unit tests for audit_service and caps_validator services."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.services.audit_service import AuditService, _entry_from_row
from app.domain.schemas import AuditLogEntry


# ─────────────────────────────────────────────
# AuditService
# ─────────────────────────────────────────────


class TestAuditServiceNoRepository:
    """Tests for AuditService with no repository (local fallback path)."""

    @pytest.mark.asyncio
    async def test_log_event_no_repo_returns_audit_entry(self):
        service = AuditService(repository=None)
        entry = await service.log_event("TEST_EVENT", payload={"key": "value"}, learner_id="L1", actor_id="A1")
        assert isinstance(entry, AuditLogEntry)
        assert entry.event_type == "TEST_EVENT"
        assert entry.learner_id == "L1"
        assert entry.payload == {"key": "value"}

    @pytest.mark.asyncio
    async def test_log_event_no_payload_defaults_to_empty(self):
        service = AuditService(repository=None)
        entry = await service.log_event("EMPTY_PAYLOAD")
        assert entry.payload == {}

    @pytest.mark.asyncio
    async def test_get_recent_events_no_repo_returns_empty_list(self):
        service = AuditService(repository=None)
        result = await service.get_recent_events()
        assert result == []


class TestAuditServiceWithAppendRepository:
    """Tests for AuditService with repository that has `append` method."""

    @pytest.mark.asyncio
    async def test_log_event_uses_append(self):
        mock_repo = AsyncMock()
        mock_row = MagicMock()
        mock_row.event_id = "evt-001"
        mock_row.learner_id = "L1"
        mock_row.event_type = "TEST_EVENT"
        mock_row.occurred_at = datetime.now(timezone.utc)
        mock_row.payload = {"key": "value"}
        mock_repo.append.return_value = mock_row

        service = AuditService(repository=mock_repo)
        entry = await service.log_event("TEST_EVENT", payload={"key": "value"}, learner_id="L1", actor_id="A1")

        mock_repo.append.assert_called_once_with(
            event_type="TEST_EVENT",
            payload={"key": "value"},
            resource_id="L1",
            actor_id="A1",
        )
        assert entry.event_id == "evt-001"
        assert entry.event_type == "TEST_EVENT"


class TestAuditServiceWithLogRepository:
    """Tests for AuditService with repository that has `log` method (not `append`)."""

    @pytest.mark.asyncio
    async def test_log_event_uses_log(self):
        class MockLogRepo:
            async def log(self, *, event_type, payload, actor_id, learner_pseudonym):
                row = MagicMock()
                row.event_id = "log-evt-001"
                row.learner_id = learner_pseudonym
                row.event_type = event_type
                row.occurred_at = datetime.now(timezone.utc)
                row.payload = payload
                return row

        service = AuditService(repository=MockLogRepo())
        entry = await service.log_event("LOG_EVENT", payload={"foo": "bar"}, learner_id="L2", actor_id="A2")
        assert entry.event_id == "log-evt-001"
        assert entry.event_type == "LOG_EVENT"

    @pytest.mark.asyncio
    async def test_get_recent_events_uses_latest(self):
        mock_repo = AsyncMock()
        mock_row = MagicMock()
        mock_row.event_id = "evt-002"
        mock_row.learner_id = "L3"
        mock_row.event_type = "CONSENT_GRANTED"
        mock_row.occurred_at = datetime.now(timezone.utc)
        mock_row.payload = {}
        mock_repo.latest.return_value = [mock_row]

        service = AuditService(repository=mock_repo)
        events = await service.get_recent_events(limit=10)
        assert len(events) == 1
        assert events[0].event_id == "evt-002"
        mock_repo.latest.assert_called_once_with(limit=10)


class TestAuditServiceConsentGranted:
    @pytest.mark.asyncio
    async def test_consent_granted_logs_correct_event(self):
        service = AuditService(repository=None)
        entry = await service.consent_granted(
            guardian_id="G1",
            learner_id="L1",
            policy_version="2024-v1",
        )
        assert entry.event_type == "CONSENT_GRANTED"
        assert entry.payload["learner_id"] == "L1"
        assert entry.payload["policy_version"] == "2024-v1"


class TestEntryFromRow:
    def test_uses_event_id(self):
        row = MagicMock()
        row.event_id = "e-999"
        row.learner_id = "L9"
        row.event_type = "FOO"
        row.occurred_at = datetime.now(timezone.utc)
        row.payload = {"a": 1}
        entry = _entry_from_row(row)
        assert entry.event_id == "e-999"

    def test_falls_back_to_id_when_no_event_id(self):
        row = MagicMock(spec=[])  # no attributes
        row.id = "fallback-id"
        entry = _entry_from_row(row)
        assert entry.event_id == "fallback-id"

    def test_payload_defaults_to_empty_when_none(self):
        row = MagicMock()
        row.event_id = "x"
        row.learner_id = None
        row.event_type = "T"
        row.occurred_at = datetime.now(timezone.utc)
        row.payload = None
        entry = _entry_from_row(row)
        assert entry.payload == {}


# ─────────────────────────────────────────────
# CAPSAlignmentValidator (basic smoke tests)
# ─────────────────────────────────────────────


class TestCAPSAlignmentValidator:
    def test_import_and_instantiation(self):
        from app.services.caps_validator import CAPSAlignmentValidator
        validator = CAPSAlignmentValidator()
        assert validator is not None

    def test_coverage_summary_returns_dict(self):
        from app.services.caps_validator import CAPSAlignmentValidator
        validator = CAPSAlignmentValidator()
        summary = validator.coverage_summary()
        assert isinstance(summary, dict)

    def test_validate_unknown_grade_returns_not_aligned(self):
        from app.services.caps_validator import CAPSAlignmentValidator
        validator = CAPSAlignmentValidator()
        result = validator.validate(grade=99, subject="NonExistent", topic="FakeTopic")
        assert result.caps_aligned is False
        assert result.canonical_topic is None

    def test_validate_caps_reference_unknown_returns_not_aligned(self):
        from app.services.caps_validator import CAPSAlignmentValidator
        validator = CAPSAlignmentValidator()
        result = validator.validate_caps_reference("UNKNOWN-REF-XYZ")
        assert result.caps_aligned is False

    def test_caps_scope_dict_is_populated(self):
        from app.services.caps_validator import CAPS_SCOPE
        # CAPS_SCOPE should have at least one grade entry populated from CAPSTopicMap
        assert isinstance(CAPS_SCOPE, dict)
        # Should have grade-level entries (e.g., grade 4-12)
        if CAPS_SCOPE:
            for grade, subjects in CAPS_SCOPE.items():
                assert isinstance(grade, int)
                assert isinstance(subjects, dict)
                break

    def test_suggest_topic_returns_none_for_unknown(self):
        from app.services.caps_validator import CAPSAlignmentValidator
        validator = CAPSAlignmentValidator()
        result = validator.suggest_topic(grade=99, subject="Nonexistent", topic="FakeTopic")
        assert result is None

    def test_validate_known_grade_subject_topic(self):
        """If any topic exists in the CAPSTopicMap for a grade, validate should align."""
        from app.services.caps_validator import CAPSAlignmentValidator, CAPS_SCOPE
        validator = CAPSAlignmentValidator()
        if not CAPS_SCOPE:
            pytest.skip("No CAPS topics loaded")
        # Find the first available grade/subject/topic triple
        grade = next(iter(CAPS_SCOPE))
        subject = next(iter(CAPS_SCOPE[grade]))
        topics = CAPS_SCOPE[grade][subject]
        if not topics:
            pytest.skip("No topics for first grade/subject combo")
        topic = topics[0]
        result = validator.validate(grade=grade, subject=subject, topic=topic)
        # Should be aligned (exact match from topic map)
        assert result.caps_aligned is True
        assert result.canonical_topic == topic
