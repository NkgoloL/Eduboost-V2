"""Comprehensive unit tests for backend consolidation runtime helpers and audit write models."""
from __future__ import annotations

import pytest

from app.services.backend_consolidation_runtime import (
    CanonicalAuditWrite,
    ConstructorProbeResult,
)


class TestBackendConsolidationRuntime:
    def test_canonical_audit_write_dataclass_and_kwargs(self):
        write = CanonicalAuditWrite(
            action="item.create",
            actor_id="admin-1",
            resource_type="diagnostic_item",
            resource_id="item-123",
            metadata={"source": "api"},
        )
        assert write.action == "item.create"
        kwargs = write.to_kwargs()
        assert kwargs["action"] == "item.create"
        assert kwargs["actor_id"] == "admin-1"
        assert kwargs["metadata"]["source"] == "api"

    def test_constructor_probe_result_dataclass(self):
        res = ConstructorProbeResult(
            import_path="app.services.system_service_v2",
            class_name="SystemServiceV2",
            importable=True,
            constructable_without_args=True,
            signature="()",
            error=None,
        )
        assert res.importable is True
        assert res.constructable_without_args is True
        assert res.class_name == "SystemServiceV2"

    @pytest.mark.asyncio
    async def test_record_canonical_audit_event_and_consent(self):
        from unittest.mock import AsyncMock
        from app.services.backend_consolidation_runtime import (
            record_canonical_audit_event,
            record_consent_audit_event,
            normalize_legacy_audit_call,
        )

        mock_repo = AsyncMock()
        mock_repo.record = AsyncMock(return_value={"status": "recorded"})

        write = CanonicalAuditWrite(
            action="consent.grant",
            actor_id="admin-1",
            resource_type="consent",
            resource_id="c-123",
            metadata={"reason": "enrollment"},
        )

        # 1. Event as CanonicalAuditWrite
        res1 = await record_canonical_audit_event(mock_repo, write)
        assert res1 is not None

        # 2. Event as dict
        res2 = await record_canonical_audit_event(mock_repo, write.to_kwargs())
        assert res2 is not None

        # 3. record_consent_audit_event
        res3 = await record_consent_audit_event(
            mock_repo,
            action="consent.granted",
            actor_id="user-1",
            learner_id="learner-1",
            resource_id="res-1",
            metadata={"version": "1.0"},
            extra_field="val",
        )
        assert res3 is not None

        # 4. normalize_legacy_audit_call
        norm = normalize_legacy_audit_call(
            event_type="consent_granted",
            actor_id="u-1",
            learner_id="l-1",
            details={"key": "val"},
        )
        assert "action" in norm

    def test_probe_constructor_branches(self):
        from app.services.backend_consolidation_runtime import probe_constructor

        # Valid module and class, constructable
        probe1 = probe_constructor("app.services.diagnostic_safety", "DiagnosticItemValidator")
        assert probe1.importable is True
        assert probe1.constructable_without_args is True
        assert probe1.error is None

        # Valid module, class requires args
        probe2 = probe_constructor("app.services.diagnostic_session_service", "DiagnosticSessionService")
        assert probe2.importable is True
        assert probe2.constructable_without_args is False
        assert probe2.error is not None

        # Invalid module
        probe3 = probe_constructor("app.services.nonexistent_service", "NonexistentClass")
        assert probe3.importable is False
        assert probe3.constructable_without_args is False
        assert probe3.error is not None

