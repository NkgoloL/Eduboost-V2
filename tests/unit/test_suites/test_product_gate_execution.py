from __future__ import annotations

from scripts.test_suites.product_gate_execution import (
    REQUIRED_FLOW_IDS,
    evaluate_product_gate_execution_contract,
    flow_command_plan,
)


def test_product_gate_execution_contract_is_valid() -> None:
    result = evaluate_product_gate_execution_contract()
    assert result["valid"] is True
    assert result["missing_flow_ids"] == []
    assert set(result["critical_flow_ids"]) >= set(REQUIRED_FLOW_IDS)
    assert result["execution_policy_valid"] is True


def test_flow_command_plan_requires_positive_and_negative_commands() -> None:
    commands = flow_command_plan()
    assert commands
    for item in commands:
        assert item["release_blocking"] is True
        assert item["positive_command"]
        assert item["negative_command"]
        assert item["evidence_artifact"].endswith(".json")
