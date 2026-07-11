from __future__ import annotations

from scripts.advisory_suites.generated_frontend_quality_gate import (
    REQUIRED_GATE_IDS,
    evaluate_generated_frontend_quality_contract,
    gate_command_plan,
)


def test_generated_frontend_quality_contract_is_valid() -> None:
    result = evaluate_generated_frontend_quality_contract()
    assert result["valid"] is True
    assert result["generated_contracts_green"] is False
    assert result["frontend_quality_green"] is False
    assert result["frontend_scripts_valid"] is True


def test_gate_command_plan_uses_active_python_for_generated_contracts() -> None:
    plan = gate_command_plan()
    assert {item["gate_id"] for item in plan} == set(REQUIRED_GATE_IDS)
    generated = [item for item in plan if item["gate_id"].startswith("generated_contract")]
    assert generated
    assert all(item["command"][0].endswith("python") or "python" in item["command"][0] for item in generated)


def test_frontend_gate_plan_uses_existing_frontend_scripts() -> None:
    plan = gate_command_plan()
    frontend_commands = [" ".join(item["command"]) for item in plan if item["gate_id"].startswith("frontend")]
    assert any("run type-check" in command for command in frontend_commands)
    assert any("run lint" in command for command in frontend_commands)
    assert any("run test" in command for command in frontend_commands)
    assert any("run build" in command for command in frontend_commands)
    assert all("test:run" not in command for command in frontend_commands)
