"""Comprehensive unit tests for AuditService, AuditMigrationOrchestrator, and AuditCanonicalization."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.domain.schemas import AuditLogEntry
from app.repositories.audit_compat import AuditEventInput
from app.services.audit_canonicalization_registry import (
    AuditMigrationCandidate,
    DEFAULT_AUDIT_MIGRATION_CANDIDATES,
    MigrationStatus,
    migration_candidates,
    ready_candidates,
    unsafe_candidates,
)
from app.services.audit_canonicalization_slice import (
    CanonicalAuditCommand,
    build_learner_audit_command,
    record_learner_audit_event,
)
from app.services.audit_migration_orchestrator import (
    AuditMigrationEnvelope,
    allowed_candidate_names,
    build_audit_migration_event,
    record_migrated_audit_event,
)
from app.services.audit_service import AuditService, _entry_from_row


# ─────────────────────────────────────────────
# AuditService
# ─────────────────────────────────────────────


class TestAuditService:
    @pytest.mark.asyncio
    async def test_log_event_with_append_repo(self):
        from types import SimpleNamespace
        mock_repo = MagicMock()
        mock_row = SimpleNamespace(
            event_id="evt-1",
            learner_id="learner-1",
            event_type="TEST_EVENT",
            occurred_at=datetime(2026, 8, 28, tzinfo=timezone.utc),
            payload={"key": "val"},
        )
        mock_repo.append = AsyncMock(return_value=mock_row)

        service = AuditService(repository=mock_repo)
        entry = await service.log_event("TEST_EVENT", payload={"key": "val"}, learner_id="learner-1", actor_id="actor-1")

        assert isinstance(entry, AuditLogEntry)
        assert entry.event_id == "evt-1"
        assert entry.learner_id == "learner-1"
        assert entry.event_type == "TEST_EVENT"
        mock_repo.append.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_event_with_log_repo(self):
        from types import SimpleNamespace
        mock_repo = MagicMock(spec=["log"])
        mock_row = SimpleNamespace(
            id="evt-2",
            learner_pseudonym="learner-2",
            event_type="TEST_LOG",
            created_at=datetime(2026, 8, 28, tzinfo=timezone.utc),
            payload={},
        )
        mock_repo.log = AsyncMock(return_value=mock_row)

        service = AuditService(repository=mock_repo)
        entry = await service.log_event("TEST_LOG", learner_id="learner-2", actor_id="actor-2")

        assert entry.event_id == "evt-2"
        assert entry.learner_id == "learner-2"
        mock_repo.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_event_without_repo_fallback(self):
        service = AuditService()
        entry = await service.log_event("FALLBACK_EVENT", payload={"hello": "world"}, learner_id="l-1")
        assert entry.event_id.startswith("local-")
        assert entry.event_type == "FALLBACK_EVENT"
        assert entry.payload == {"hello": "world"}

    @pytest.mark.asyncio
    async def test_get_recent_events(self):
        mock_repo = MagicMock(spec=["latest"])
        mock_row = MagicMock(
            event_id="evt-3",
            learner_id="l-3",
            event_type="EVENT_3",
            occurred_at=datetime(2026, 8, 28, tzinfo=timezone.utc),
            payload={},
        )
        mock_repo.latest = AsyncMock(return_value=[mock_row])

        service = AuditService(repository=mock_repo)
        events = await service.get_recent_events(limit=10)
        assert len(events) == 1
        assert events[0].event_id == "evt-3"

        # No repo returns []
        service_none = AuditService()
        assert await service_none.get_recent_events() == []

    @pytest.mark.asyncio
    async def test_consent_granted_helper(self):
        service = AuditService()
        entry = await service.consent_granted("guard-1", "learner-1", "v1.0")
        assert entry.event_type == "CONSENT_GRANTED"
        assert entry.payload["policy_version"] == "v1.0"


# ─────────────────────────────────────────────
# AuditCanonicalizationRegistry
# ─────────────────────────────────────────────


class TestAuditCanonicalizationRegistry:
    def test_migration_status_enum(self):
        assert MigrationStatus.INVENTORIED.value == "inventoried"
        assert MigrationStatus.ADAPTER_READY.value == "adapter_ready"
        assert MigrationStatus.MIGRATION_READY.value == "migration_ready"
        assert MigrationStatus.MIGRATED.value == "migrated"
        assert MigrationStatus.DEFERRED.value == "deferred"

    def test_candidates_helpers(self):
        all_cands = migration_candidates()
        assert len(all_cands) == 3

        ready = ready_candidates()
        assert len(ready) == 2
        assert {c.name for c in ready} == {"consent_audit_events", "popia_data_rights_audit"}

        unsafe = unsafe_candidates()
        assert len(unsafe) == 0


# ─────────────────────────────────────────────
# AuditMigrationOrchestrator
# ─────────────────────────────────────────────


class TestAuditMigrationOrchestrator:
    def test_allowed_candidate_names(self):
        names = allowed_candidate_names()
        assert "consent_audit_events" in names
        assert "popia_data_rights_audit" in names
        assert "legacy_audit_logs" not in names

    def test_build_audit_migration_event_validation(self):
        with pytest.raises(ValueError, match="not adapter-ready"):
            build_audit_migration_event(candidate_name="invalid_candidate", action="test")

        with pytest.raises(ValueError, match="action is required"):
            build_audit_migration_event(candidate_name="consent_audit_events", action="")

    def test_build_audit_migration_event_success(self):
        env = build_audit_migration_event(
            candidate_name="consent_audit_events",
            action="consent.granted",
            actor_id="actor-1",
            resource_type="consent",
            resource_id="cons-1",
            learner_id="learner-1",
            metadata={"source": "api"},
            extra_field="extra_value",
        )
        assert env.candidate_name == "consent_audit_events"
        assert env.action == "consent.granted"
        assert env.metadata["source"] == "api"
        assert env.metadata["extra_field"] == "extra_value"
        assert env.metadata["migration_candidate"] == "consent_audit_events"

        evt_input = env.to_event_input()
        assert isinstance(evt_input, AuditEventInput)
        assert evt_input.action == "consent.granted"

    @pytest.mark.asyncio
    async def test_record_migrated_audit_event(self):
        env = build_audit_migration_event(
            candidate_name="consent_audit_events",
            action="consent.granted",
            actor_id="actor-1",
            learner_id="learner-1",
        )
        mock_repo = MagicMock()
        mock_repo.record = AsyncMock(return_value={"status": "recorded"})

        res = await record_migrated_audit_event(mock_repo, env)
        assert res == {"status": "recorded"}


# ─────────────────────────────────────────────
# AuditCanonicalizationSlice
# ─────────────────────────────────────────────


class TestAuditCanonicalizationSlice:
    def test_build_learner_audit_command_validation(self):
        with pytest.raises(ValueError, match="audit action is required"):
            build_learner_audit_command(action="", actor_id="a1", learner_id="l1")

        with pytest.raises(ValueError, match="learner_id is required"):
            build_learner_audit_command(action="action", actor_id="a1", learner_id="")

    def test_build_learner_audit_command_success(self):
        cmd = build_learner_audit_command(
            action="learner.updated",
            actor_id="guard-1",
            learner_id="learner-1",
            metadata={"field": "grade"},
        )
        assert cmd.action == "learner.updated"
        assert cmd.resource_type == "learner"
        assert cmd.metadata == {"field": "grade"}

        evt_input = cmd.to_event_input()
        assert evt_input.resource_id == "learner-1"

    @pytest.mark.asyncio
    async def test_record_learner_audit_event(self):
        mock_repo = MagicMock()
        mock_repo.record = AsyncMock(return_value={"status": "ok"})

        res = await record_learner_audit_event(
            mock_repo,
            action="learner.viewed",
            actor_id="guard-1",
            learner_id="learner-1",
            metadata={"ip": "127.0.0.1"},
        )
        assert res == {"status": "ok"}
