from __future__ import annotations

from scripts.advisory_suites.advisory_gate import (
    REQUIRED_GATE_IDS,
    evaluate_advisory_quality_gate_contract,
    gate_command_plan,
)


def test_advisory_quality_gate_contract_is_valid() -> None:
    result = evaluate_advisory_quality_gate_contract()
    assert result["valid"] is True
    assert not result["missing_gates"]
    assert result["gates_valid"] is True
    assert result["policy_valid"] is True


def test_advisory_gate_commands_cover_required_gate_ids() -> None:
    command_ids = {item["gate_id"] for item in gate_command_plan()}
    assert set(REQUIRED_GATE_IDS).issubset(command_ids)


def test_advisory_quality_green_state_not_claimed_by_contract() -> None:
    result = evaluate_advisory_quality_gate_contract()
    assert result["coverage_gate_green"] is False
    assert result["frontend_quality_green"] is False
    assert result["advisory_static_gate_green"] is False
