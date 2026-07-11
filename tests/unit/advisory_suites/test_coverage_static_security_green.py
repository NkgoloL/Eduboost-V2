import json
from pathlib import Path
import sys

from scripts.advisory_suites.coverage_static_security_green import (
    REQUIRED_GATE_IDS,
    CoverageStaticSecurityCommand,
    _remaining_violation_count,
    _run_one,
    command_plan,
    evaluate_coverage_static_security_contract,
    run_coverage_static_security_green,
)


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
    assert payload["partial"] is False
    assert (tmp_path / "summary.json").exists()
    saved = json.loads((tmp_path / "summary.json").read_text())
    assert saved["valid"] is True


def test_runner_can_plan_one_gate_for_remediation(tmp_path: Path):
    payload = run_coverage_static_security_green(
        execute=False,
        output_dir=tmp_path,
        gate_ids={"ruff_release_static_quality"},
    )

    assert payload["partial"] is True
    assert payload["selected_gate_ids"] == ["ruff_release_static_quality"]
    assert [item["gate_id"] for item in payload["command_plan"]] == ["ruff_release_static_quality"]


def test_gate_execution_records_bounded_operational_artifacts(tmp_path: Path):
    command = CoverageStaticSecurityCommand(
        "ruff_release_static_quality",
        "synthetic failing ruff gate",
        [sys.executable, "-c", "import sys; print('demo.py:1:1: F401 unused'); print('err', file=sys.stderr); raise SystemExit(1)"],
        "synthetic.json",
        30,
    )

    payload = _run_one(command, tmp_path)

    assert payload["started_at"]
    assert payload["completed_at"]
    assert payload["duration_seconds"] >= 0
    assert payload["timeout_seconds"] == 30
    assert payload["exit_code"] == 1
    assert payload["timed_out"] is False
    assert payload["green"] is False
    assert payload["failure_classification"] == "static_quality_violations"
    assert payload["remaining_violation_count"] == 1
    assert (tmp_path / "synthetic.stdout.txt").read_text()
    assert (tmp_path / "synthetic.stderr.txt").read_text()


def test_coverage_timeout_counts_observed_pytest_failures():
    stdout = "F........FF............................................................. [  2%]\n.....F...F [  4%]\n"

    assert _remaining_violation_count("coverage_execution", stdout, "", None) == 5
