import json
from pathlib import Path

from scripts.advisory_suites.coverage_static_security_green import REQUIRED_GATE_IDS, command_plan, evaluate_coverage_static_security_contract, run_coverage_static_security_green


def test_command_plan_covers_release_blocking_advisory_gates():
    plan = command_plan()
    assert {item.gate_id for item in plan} == set(REQUIRED_GATE_IDS)
    assert all(item.release_blocking for item in plan)
    assert all(item.command for item in plan)


def test_contract_is_valid_without_green_results():
    result = evaluate_coverage_static_security_contract(require_green=False)
    assert result["base_valid"] is True
    assert result["valid"] is True
    assert result["previous_green"] is True


def test_runner_plan_mode_writes_summary(tmp_path: Path):
    payload = run_coverage_static_security_green(execute=False, output_dir=tmp_path)
    assert payload["executed"] is False
    assert (tmp_path / "summary.json").exists()
    saved = json.loads((tmp_path / "summary.json").read_text())
    assert saved["valid"] is True
