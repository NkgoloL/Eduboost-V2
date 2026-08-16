from pathlib import Path

from scripts.advisory_suites.generated_contract_frontend_quality_green_evidence import (
    REQUIRED_GATE_IDS,
    evaluate_green_evidence_contract,
    execute_green_evidence,
    green_evidence_command_plan,
)


def test_green_evidence_command_plan_contains_all_release_blockers():
    plan = green_evidence_command_plan()
    assert {item["gate_id"] for item in plan} == set(REQUIRED_GATE_IDS)
    assert all(item["release_blocking"] for item in plan)
    assert any(item["gate_id"] == "frontend_build_side_effect_check" for item in plan)


def test_green_evidence_contract_fails_closed_without_manual_review():
    result = evaluate_green_evidence_contract(require_green=False)
    assert result["base_valid"] is False
    assert result["valid"] is False
    assert result["manual_review"]["missing"] == ["PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4"]
    assert result["all_green"] is False


def test_green_evidence_execute_records_missing_executable_as_blocker(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PNPM_BIN", "definitely-missing-pnpm-for-prd11-test")
    payload = execute_green_evidence(gates=["frontend_release_quality"], output_dir=tmp_path)
    assert payload["all_green"] is False
    assert payload["blockers"] == ["frontend_release_quality"]
    assert (tmp_path / "summary.json").exists()
