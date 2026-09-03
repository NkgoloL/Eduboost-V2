from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.audit_canonicalization_registry import (
    AuditMigrationCandidate,
    MigrationStatus,
    migration_candidates,
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
from app.services.runtime_audit_facade import (
    RuntimeAuditRecord,
    record_runtime_audit_event,
)


def test_audit_canonicalization_registry():
    candidates = migration_candidates()
    assert len(candidates) >= 3
    assert not unsafe_candidates()

    allowed = allowed_candidate_names()
    assert "consent_audit_events" in allowed
    assert "popia_data_rights_audit" in allowed


@pytest.mark.asyncio
async def test_audit_canonicalization_slice():
    # 1. Valid learner audit command
    cmd = build_learner_audit_command(
        action="learner.consent_granted",
        actor_id="actor_1",
        learner_id="learner_1",
        metadata={"scope": "math"},
    )
    assert isinstance(cmd, CanonicalAuditCommand)
    assert cmd.resource_id == "learner_1"
    event_input = cmd.to_event_input()
    assert event_input.action == "learner.consent_granted"

    # 2. Validation errors
    with pytest.raises(ValueError, match="action is required"):
        build_learner_audit_command(action="", actor_id="a", learner_id="l")

    with pytest.raises(ValueError, match="learner_id is required"):
        build_learner_audit_command(action="act", actor_id="a", learner_id="")

    # 3. record_learner_audit_event
    repo_mock = MagicMock()
    repo_mock.record = AsyncMock(return_value={"id": "evt_123"})
    result = await record_learner_audit_event(
        repo_mock,
        action="learner.profile_updated",
        actor_id="actor_1",
        learner_id="learner_1",
    )
    assert result == {"id": "evt_123"}
    assert repo_mock.record.await_count == 1


@pytest.mark.asyncio
async def test_audit_migration_orchestrator():
    # 1. Build migration event
    env = build_audit_migration_event(
        candidate_name="consent_audit_events",
        action="consent.verified",
        actor_id="admin_1",
        learner_id="learner_1",
        metadata={"note": "first pass"},
        extra_key="extra_val",
    )
    assert isinstance(env, AuditMigrationEnvelope)
    assert env.candidate_name == "consent_audit_events"
    assert env.metadata["extra_key"] == "extra_val"

    # 2. Candidate not allowed error
    with pytest.raises(ValueError, match="not adapter-ready"):
        build_audit_migration_event(candidate_name="invalid_candidate", action="act")

    # 3. Empty action error
    with pytest.raises(ValueError, match="action is required"):
        build_audit_migration_event(candidate_name="consent_audit_events", action="")

    # 4. record_migrated_audit_event
    repo_mock = MagicMock()
    repo_mock.record = AsyncMock(return_value={"id": "migrated_1"})
    res = await record_migrated_audit_event(repo_mock, env)
    assert res == {"id": "migrated_1"}


@pytest.mark.asyncio
async def test_runtime_audit_facade():
    repo_mock = MagicMock()
    repo_mock.record = AsyncMock(return_value={"id": "facade_1"})

    record = await record_runtime_audit_event(
        repo_mock,
        action="runtime.action",
        candidate_name="consent_audit_events",
        actor_id="user_1",
        learner_id="learner_1",
        metadata={"detail": "facade test"},
    )
    assert isinstance(record, RuntimeAuditRecord)
    assert record.action == "runtime.action"
    assert record.metadata["runtime_audit_facade"] is True
    assert repo_mock.record.await_count == 1
