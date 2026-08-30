"""Comprehensive unit tests for first consent and deep readiness runtime wiring candidates."""
from __future__ import annotations

import pytest

from app.services.first_consent_runtime_wiring import (
    FirstConsentRuntimeCandidate,
    load_first_consent_runtime_candidate,
    assert_consent_candidate_is_safe,
    build_first_consent_runtime_payload,
)
from app.services.first_deep_readiness_runtime_wiring import (
    FirstDeepReadinessRuntimeCandidate,
    DeepReadinessRuntimePlan,
    load_first_deep_readiness_runtime_candidate,
    assert_deep_readiness_candidate_is_safe,
)


class TestFirstConsentRuntimeWiring:
    def test_load_and_assert_safe_consent_candidate(self):
        candidate = load_first_consent_runtime_candidate()
        assert candidate.approved_for_runtime_pr is True
        assert candidate.destructive is False
        # assert safe should not raise
        assert_consent_candidate_is_safe(candidate)

    def test_assert_unsafe_consent_candidate_raises(self):
        unsafe_cand = FirstConsentRuntimeCandidate(
            id="unsafe-1",
            action="consent.delete",
            actor_id="admin-1",
            learner_id="learner-1",
            expected_operation_type="delete",
            expected_resource_type="consent",
            approved_for_runtime_pr=False,
            destructive=True,
            requires_route_change=False,
            requires_schema_change=False,
            requires_database_write_in_test=False,
            requires_table_merge=False,
        )
        with pytest.raises(ValueError, match="not approved for runtime PR"):
            assert_consent_candidate_is_safe(unsafe_cand)

    def test_build_first_consent_runtime_payload(self):
        payload = build_first_consent_runtime_payload()
        assert payload.candidate_id is not None
        assert "action" in payload.payload
        assert payload.payload["metadata"]["operation_type"] == "write"


class TestFirstDeepReadinessRuntimeWiring:
    def test_load_and_assert_safe_deep_readiness_candidate(self):
        candidate = load_first_deep_readiness_runtime_candidate()
        assert candidate.approved_for_runtime_pr is True
        assert candidate.destructive is False
        assert_deep_readiness_candidate_is_safe(candidate)

    def test_deep_readiness_runtime_plan_dataclass(self):
        plan = DeepReadinessRuntimePlan(
            candidate_id="deep-readiness-1",
            checks=("database", "redis", "alembic"),
            public_safe=True,
            mutates_state=False,
        )
        assert plan.candidate_id == "deep-readiness-1"
        assert plan.public_safe is True
        assert plan.mutates_state is False
