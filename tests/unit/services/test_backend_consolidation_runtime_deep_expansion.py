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
