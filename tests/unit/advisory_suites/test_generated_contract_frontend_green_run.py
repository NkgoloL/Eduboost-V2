from scripts.advisory_suites.generated_contract_frontend_green_run import (
    REQUIRED_GATE_IDS,
    evaluate_green_run_contract,
    green_run_command_plan,
)


def test_green_run_command_plan_covers_generated_and_frontend_gates():
    plan = green_run_command_plan()
    assert {item["gate_id"] for item in plan} == set(REQUIRED_GATE_IDS)
    assert any(item["gate_id"] == "openapi_regenerate" and item["mutates_generated_contracts"] for item in plan)
    assert any(item["gate_id"] == "generated_contract_readonly_check" for item in plan)
    assert any(item["gate_id"] == "frontend_release_quality" for item in plan)


def test_green_run_contract_fails_closed_without_manual_review():
    result = evaluate_green_run_contract()
    assert result["valid"] is False
    assert result["manual_review"]["missing"] == ["PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3"]
    assert result["generated_contracts_green"] is False
    assert result["frontend_quality_green"] is False
    assert result["command_plan_valid"] is True
