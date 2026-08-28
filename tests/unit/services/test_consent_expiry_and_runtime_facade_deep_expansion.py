"""Comprehensive unit tests for consent expiry loop and runtime audit facade."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock
import pytest

from app.services.consent_expiry_service import consent_expiry_loop
from app.services.runtime_audit_facade import (
    RuntimeAuditRecord,
    record_runtime_audit_event,
)


class TestConsentExpiryLoop:
    @pytest.mark.asyncio
    async def test_consent_expiry_loop_one_iteration(self):
        mock_run_once = AsyncMock(return_value=5)

        async def run_and_cancel():
            task = asyncio.create_task(consent_expiry_loop(interval_seconds=10, run_once=mock_run_once))
            await asyncio.sleep(0.01)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        await run_and_cancel()
        assert mock_run_once.await_count >= 1


class TestRuntimeAuditFacade:
    def test_runtime_audit_record_dataclass(self):
        rec = RuntimeAuditRecord(
            action="consent.renew",
            resource_id="res_123",
            metadata={"source": "api"},
        )
        assert rec.action == "consent.renew"
        assert rec.resource_id == "res_123"
        assert rec.metadata["source"] == "api"

    @pytest.mark.asyncio
    async def test_record_runtime_audit_event(self):
        mock_repo = AsyncMock()
        record = await record_runtime_audit_event(
            repository=mock_repo,
            action="consent.granted",
            candidate_name="consent_audit_events",
            actor_id="guard-123",
            resource_type="consent",
            metadata={"source": "portal"},
        )
        assert record.action == "consent.granted"
        assert record.metadata.get("migration_candidate") == "consent_audit_events"
