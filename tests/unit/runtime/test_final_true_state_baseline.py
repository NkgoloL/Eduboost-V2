from __future__ import annotations

from scripts.runtime.final_true_state_baseline import (
    NEXT_IF_RED,
    REQUIRED_GATE_IDS,
    collect_final_true_state_baseline,
    evaluate_final_true_state_handoff_contract,
    gate_command_plan,
)


def test_final_true_state_handoff_contract_stays_red_when_reviewed_raw_release_state_is_red() -> None:
    result = evaluate_final_true_state_handoff_contract()
    assert result["valid"] is False
    assert result["manual_review"]["valid"] is True
    assert result["raw_execution_valid"] is True
    assert result["raw_all_release_gates_green"] is False
    assert not result["missing_gates"]
    assert result["gates_valid"] is True
    assert result["policy_valid"] is True


def test_final_true_state_commands_cover_required_gates() -> None:
    command_ids = {item["gate_id"] for item in gate_command_plan()}
    assert set(REQUIRED_GATE_IDS).issubset(command_ids)


def test_final_true_state_default_collection_is_fail_closed() -> None:
    result = collect_final_true_state_baseline()
    assert result["contract_valid"] is False
    assert result["all_release_gates_green"] is False
    assert result["controlled_handoff_to_prd1100_1104_authorised"] is False
    assert result["next_authorised_item"] == NEXT_IF_RED
