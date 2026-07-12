from __future__ import annotations

from pathlib import Path

from scripts.test_suites.product_critical_flow_green import REQUIRED_FLOW_IDS, command_plan, evaluate_product_critical_flow_contract, run_product_flow_green


def test_product_critical_flow_command_plan_covers_required_flows() -> None:
    plan = command_plan()
    assert {item.flow_id for item in plan} == set(REQUIRED_FLOW_IDS)
    assert all(item.release_blocking for item in plan)
    assert all(item.requires_positive_path and item.requires_negative_path for item in plan)


def test_product_critical_flow_contract_is_valid_before_green_evidence() -> None:
    result = evaluate_product_critical_flow_contract(require_green=False)
    assert result["base_valid"] is True
    assert result["runtime_prerequisites_green"] is True


def test_product_critical_flow_runner_lists_without_executing(tmp_path: Path) -> None:
    result = run_product_flow_green(execute=False, output_dir=tmp_path)
    assert result["valid"] is True
    assert result["executed"] is False
    assert (tmp_path / "summary.json").exists()
