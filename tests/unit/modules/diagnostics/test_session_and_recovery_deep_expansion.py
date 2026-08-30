"""Comprehensive unit tests for diagnostic session recovery, memory redis store, and item selection."""
from __future__ import annotations

import time
from types import SimpleNamespace
import pytest

from app.modules.diagnostics.session_recovery_service import (
    DiagnosticSessionSnapshot,
    _MemoryRedis,
    SessionRecoveryService,
)
from app.modules.diagnostics.item_selection_service import (
    SelectionResult,
    ItemSelectionService,
)


class TestDiagnosticSessionModels:
    def test_session_snapshot_dataclass(self):
        snap = DiagnosticSessionSnapshot(
            session_id="sess_456",
            learner_id="learner_789",
            caps_ref="4.M.1.1",
            session_state="item_serving",
            theta=0.1,
            se_estimate=0.8,
            items_served=2,
            served_item_ids=["item_1", "item_2"],
        )
        assert snap.session_id == "sess_456"
        assert snap.session_state == "item_serving"
        assert len(snap.served_item_ids) == 2

    def test_selection_result_dataclass(self):
        res = SelectionResult(
            item=None,
            information=0.85,
            eligible_count=5,
        )
        assert res.item is None
        assert res.information == 0.85
        assert res.eligible_count == 5


class TestSessionRecoveryServiceAndMemoryRedis:
    @pytest.mark.asyncio
    async def test_memory_redis_crud_and_expiry(self):
        mem = _MemoryRedis()
        await mem.setex("key1", 10, "val1")
        assert await mem.get("key1") == "val1"

        await mem.delete("key1")
        assert await mem.get("key1") is None

        # Expired entry
        await mem.setex("key_exp", -1, "expired_val")
        assert await mem.get("key_exp") is None

    @pytest.mark.asyncio
    async def test_recovery_service_write_and_read_snapshot(self):
        recovery = SessionRecoveryService()
        snap = DiagnosticSessionSnapshot(
            session_id="sess_abc",
            learner_id="learner_xyz",
            caps_ref="4.M.1.1",
            theta=0.2,
        )
        await recovery.write_session_snapshot("sess_abc", snap)

        read_snap = await recovery.read_session_snapshot("sess_abc")
        assert read_snap is not None
        assert read_snap.session_id == "sess_abc"
        assert read_snap.learner_id == "learner_xyz"
        assert read_snap.theta == 0.2


class TestItemSelectionService:
    def test_select_max_information_item(self):
        service = ItemSelectionService()
        item1 = SimpleNamespace(item_id="item_1", discrimination_a=1.0, difficulty_b=0.0, review_status="approved")
        item2 = SimpleNamespace(item_id="item_2", discrimination_a=1.5, difficulty_b=0.2, review_status="approved")

        selected = service.select_max_information_item([item1, item2], theta=0.0, served_ids=set())
        assert selected.item is not None
        assert selected.eligible_count == 2
