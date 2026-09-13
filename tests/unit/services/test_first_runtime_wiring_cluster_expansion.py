from unittest.mock import AsyncMock, MagicMock, patch
import pytest


from app.services.first_audit_runtime_wiring import (
    FirstAuditRuntimeCandidate,
    InMemoryFirstAuditRuntimeSink,
    assert_candidate_is_safe,
    build_first_audit_runtime_payload,
    load_first_audit_runtime_candidate,
    record_first_audit_runtime_candidate,
)
from app.services.first_consent_runtime_wiring import (
    FirstConsentRuntimeCandidate,
    assert_consent_candidate_is_safe,
    build_first_consent_runtime_payload,
    load_first_consent_runtime_candidate,
)
from app.services.first_deep_readiness_runtime_wiring import (
    FirstDeepReadinessRuntimeCandidate,
    assert_deep_readiness_candidate_is_safe,
    build_first_deep_readiness_runtime_plan,
    load_first_deep_readiness_runtime_candidate,
)


@pytest.mark.asyncio
async def test_first_audit_runtime_wiring_complete():
    # 1. InMemoryFirstAuditRuntimeSink
    sink = InMemoryFirstAuditRuntimeSink()
    res = await sink.record(action="user.login", resource_id="res-1")
    assert res["recorded"] is True
    assert res["event_count"] == 1
    assert res["action"] == "user.login"

    # 2. load_first_audit_runtime_candidate
    cand = load_first_audit_runtime_candidate()
    assert cand.id is not None
    assert_candidate_is_safe(cand)

    # 3. assert_candidate_is_safe violations
    with pytest.raises(ValueError, match="not approved"):
        assert_candidate_is_safe(FirstAuditRuntimeCandidate(
            id="c1", source_candidate="s", action="a", actor_id="act", learner_id="l",
            resource_type="r", approved_for_runtime_pr=False, destructive=False,
            requires_route_change=False, requires_schema_change=False, requires_database_write_in_test=False,
        ))

    with pytest.raises(ValueError, match="destructive"):
        assert_candidate_is_safe(FirstAuditRuntimeCandidate(
            id="c2", source_candidate="s", action="a", actor_id="act", learner_id="l",
            resource_type="r", approved_for_runtime_pr=True, destructive=True,
            requires_route_change=False, requires_schema_change=False, requires_database_write_in_test=False,
        ))

    with pytest.raises(ValueError, match="route-change"):
        assert_candidate_is_safe(FirstAuditRuntimeCandidate(
            id="c3", source_candidate="s", action="a", actor_id="act", learner_id="l",
            resource_type="r", approved_for_runtime_pr=True, destructive=False,
            requires_route_change=True, requires_schema_change=False, requires_database_write_in_test=False,
        ))

    with pytest.raises(ValueError, match="schema-change"):
        assert_candidate_is_safe(FirstAuditRuntimeCandidate(
            id="c4", source_candidate="s", action="a", actor_id="act", learner_id="l",
            resource_type="r", approved_for_runtime_pr=True, destructive=False,
            requires_route_change=False, requires_schema_change=True, requires_database_write_in_test=False,
        ))

    with pytest.raises(ValueError, match="DB-writing"):
        assert_candidate_is_safe(FirstAuditRuntimeCandidate(
            id="c5", source_candidate="s", action="a", actor_id="act", learner_id="l",
            resource_type="r", approved_for_runtime_pr=True, destructive=False,
            requires_route_change=False, requires_schema_change=False, requires_database_write_in_test=True,
        ))

    # 4. build_first_audit_runtime_payload & record_first_audit_runtime_candidate
    payload = build_first_audit_runtime_payload(cand)
    assert payload.candidate_id == cand.id
    assert "action" in payload.payload

    record_res = await record_first_audit_runtime_candidate(sink, cand)
    assert record_res.recorded is True
    assert record_res.candidate_id == cand.id

    # Default cand load in record
    record_res_default = await record_first_audit_runtime_candidate(sink)
    assert record_res_default.recorded is True


def test_first_consent_runtime_wiring_complete():
    from app.services.first_consent_runtime_wiring import validate_first_consent_runtime_payload

    # 1. load_first_consent_runtime_candidate
    cand = load_first_consent_runtime_candidate()
    assert cand.id is not None
    assert_consent_candidate_is_safe(cand)

    # 2. assert_consent_candidate_is_safe violations
    base_args = dict(
        id="c1", action="a", actor_id="act", learner_id="l",
        expected_operation_type="op", expected_resource_type="res",
        approved_for_runtime_pr=True, destructive=False,
        requires_route_change=False, requires_schema_change=False,
        requires_database_write_in_test=False, requires_table_merge=False,
    )

    for flag, err_match in [
        ("approved_for_runtime_pr", "not approved"),
        ("destructive", "destructive"),
        ("requires_route_change", "route-change"),
        ("requires_schema_change", "schema-change"),
        ("requires_database_write_in_test", "DB-writing"),
        ("requires_table_merge", "table merge"),
    ]:
        modified = dict(base_args)
        modified[flag] = not base_args[flag]
        with pytest.raises(ValueError, match=err_match):
            assert_consent_candidate_is_safe(FirstConsentRuntimeCandidate(**modified))

    # 3. build_first_consent_runtime_payload
    payload = build_first_consent_runtime_payload(cand)
    assert payload.candidate_id == cand.id
    assert "action" in payload.payload

    payload_default = build_first_consent_runtime_payload()
    assert payload_default.candidate_id == cand.id

    # 4. validate_first_consent_runtime_payload
    assert validate_first_consent_runtime_payload(cand) is True
    assert validate_first_consent_runtime_payload() is True


def test_first_deep_readiness_runtime_wiring_complete():
    from app.services.first_deep_readiness_runtime_wiring import validate_first_deep_readiness_runtime_plan

    # 1. load_first_deep_readiness_runtime_candidate
    cand = load_first_deep_readiness_runtime_candidate()
    assert cand.id is not None
    assert_deep_readiness_candidate_is_safe(cand)

    # 2. assert_deep_readiness_candidate_is_safe violations
    base_args = dict(
        id="c1", checks=("chk1",), approved_for_runtime_pr=True,
        destructive=False, requires_route_change=False,
        requires_schema_change=False, requires_database_write_in_test=False,
        allows_public_mutation=False,
    )

    for flag, err_match in [
        ("approved_for_runtime_pr", "not approved"),
        ("destructive", "destructive"),
        ("requires_route_change", "route-change"),
        ("requires_schema_change", "schema-change"),
        ("requires_database_write_in_test", "DB-writing"),
        ("allows_public_mutation", "public mutation"),
    ]:
        modified = dict(base_args)
        modified[flag] = not base_args[flag]
        with pytest.raises(ValueError, match=err_match):
            assert_deep_readiness_candidate_is_safe(FirstDeepReadinessRuntimeCandidate(**modified))

    # 3. build_first_deep_readiness_runtime_plan
    plan = build_first_deep_readiness_runtime_plan(cand)
    assert plan.candidate_id == cand.id
    assert plan.public_safe is True
    assert plan.mutates_state is False

    plan_default = build_first_deep_readiness_runtime_plan()
    assert plan_default.candidate_id == cand.id

    # 4. validate_first_deep_readiness_runtime_plan
    assert validate_first_deep_readiness_runtime_plan(cand) is True
    assert validate_first_deep_readiness_runtime_plan() is True

    # 5. Invalid checks in build_first_deep_readiness_runtime_plan
    cand_missing_chk = FirstDeepReadinessRuntimeCandidate(
        id="c_missing", checks=("nonexistent_check",), approved_for_runtime_pr=True,
        destructive=False, requires_route_change=False, requires_schema_change=False,
        requires_database_write_in_test=False, allows_public_mutation=False,
    )
    with pytest.raises(ValueError, match="missing from catalogue"):
        build_first_deep_readiness_runtime_plan(cand_missing_chk)

    # Check that is not public safe
    from app.services.deep_readiness_route_contracts import DeepReadinessRouteCheck, ReadinessCheckMode
    bad_contract = DeepReadinessRouteCheck(
        name="unsafe_chk",
        mode=ReadinessCheckMode.INTERNAL_MUTATING,
        dependency="dep",
        public_safe=False,
        mutates_state=True,
        required_for_release=False,
    )
    with patch("app.services.first_deep_readiness_runtime_wiring.DEFAULT_DEEP_READINESS_CHECKS", (bad_contract,)):
        cand_unsafe = FirstDeepReadinessRuntimeCandidate(
            id="c_unsafe", checks=("unsafe_chk",), approved_for_runtime_pr=True,
            destructive=False, requires_route_change=False, requires_schema_change=False,
            requires_database_write_in_test=False, allows_public_mutation=False,
        )
        with pytest.raises(ValueError, match="not public/read-only safe"):
            build_first_deep_readiness_runtime_plan(cand_unsafe)


