from __future__ import annotations

from pathlib import Path

from scripts.runtime.runtime_stack_db_ready_green import (
    command_plan,
    evaluate_runtime_green_contract,
    run_runtime_stack_db_ready_green,
)


def test_runtime_green_command_plan_requires_live_runtime_gates() -> None:
    gate_ids = {item["gate_id"] for item in command_plan()}
    assert {
        "compose_contract",
        "alembic_upgrade_head",
        "disposable_stack_schema_lineage_live",
        "redis_readiness",
        "ready_http_probe",
    }.issubset(gate_ids)


def test_runtime_green_dry_run_is_not_green(tmp_path: Path) -> None:
    result = run_runtime_stack_db_ready_green(execute=False, output_dir=tmp_path)
    assert result["all_green"] is False
    assert "runtime_green_commands_not_executed" in result["blockers"]


def test_runtime_green_contract_installed() -> None:
    result = evaluate_runtime_green_contract()
    assert result["base_valid"] is True
    assert result["valid"] is True
    checks = result["checks"]
    assert checks["requires_alembic_upgrade_proof"] is True
    assert checks["requires_schema_lineage_live"] is True
    assert checks["requires_redis_probe"] is True
    assert checks["requires_ready_probe"] is True
