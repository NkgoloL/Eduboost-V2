"""Comprehensive unit tests for first audit runtime wiring models and in-memory sink."""
from __future__ import annotations

import pytest

from app.services.first_audit_runtime_wiring import (
    FirstAuditRuntimeCandidate,
    FirstAuditRuntimePayload,
    FirstAuditRuntimeRecordResult,
    InMemoryFirstAuditRuntimeSink,
    load_first_audit_runtime_candidate,
)


class TestFirstAuditRuntimeWiring:
    def test_first_audit_runtime_candidate_dataclass(self):
        cand = FirstAuditRuntimeCandidate(
            id="audit-cand-1",
            source_candidate="consent_audit_events",
            action="consent.granted",
            actor_id="guardian-1",
            learner_id="learner-1",
            resource_type="consent",
            approved_for_runtime_pr=True,
            destructive=False,
            requires_route_change=False,
            requires_schema_change=False,
            requires_database_write_in_test=False,
        )
        assert cand.id == "audit-cand-1"
        assert cand.approved_for_runtime_pr is True
        assert cand.destructive is False

    def test_first_audit_runtime_payload_dataclass(self):
        payload = FirstAuditRuntimePayload(
            candidate_id="cand-100",
            payload={"action": "test.action"},
        )
        assert payload.candidate_id == "cand-100"
        assert payload.payload["action"] == "test.action"

    def test_first_audit_runtime_record_result_dataclass(self):
        res = FirstAuditRuntimeRecordResult(
            candidate_id="cand-100",
            recorded=True,
            response={"status": "ok"},
        )
        assert res.candidate_id == "cand-100"
        assert res.recorded is True

    @pytest.mark.asyncio
    async def test_in_memory_first_audit_runtime_sink(self):
        sink = InMemoryFirstAuditRuntimeSink()
        result = await sink.record(action="consent.verified", resource_id="learner-99")
        assert result["recorded"] is True
        assert result["event_count"] == 1
        assert result["action"] == "consent.verified"
        assert result["resource_id"] == "learner-99"
        assert len(sink.events) == 1

    def test_load_first_audit_runtime_candidate_fixture(self):
        candidate = load_first_audit_runtime_candidate()
        assert candidate.approved_for_runtime_pr is True
        assert candidate.destructive is False
