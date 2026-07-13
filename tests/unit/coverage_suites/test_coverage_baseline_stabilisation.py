from __future__ import annotations

import json
from pathlib import Path
import sys

from scripts.advisory_suites.coverage_static_security_green import command_plan
from scripts.coverage_suites.coverage_baseline_stabilisation import (
    MARKER_EXPRESSION,
    balanced_shards,
    build_shard_plan,
    discover_test_files,
    evaluate_coverage_baseline_stabilisation_contract,
    run_bounded_command,
    run_coverage_baseline_stabilisation,
)


def test_discovery_and_sharding_cover_every_test_file_once(tmp_path: Path) -> None:
    for relative in (
        "tests/unit/test_a.py",
        "tests/unit/test_b.py",
        "tests/unit/nested/test_c.py",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    files = discover_test_files(tmp_path, "unit")
    shards = balanced_shards(
        tmp_path,
        files,
        suite="unit",
        shard_count=2,
        timeout_seconds=30,
    )

    flattened = [item for shard in shards for item in shard.test_files]
    assert sorted(flattened) == sorted(path.as_posix() for path in files)
    assert len(flattened) == len(set(flattened))
    assert [shard.shard_id for shard in shards] == ["unit-01-of-02", "unit-02-of-02"]


def test_shard_plan_is_deterministic_for_current_repository() -> None:
    first = build_shard_plan()
    second = build_shard_plan()

    assert first == second
    assert first["unit_test_file_count"] > 0
    assert first["integration_test_file_count"] > 0
    assert len(first["unit_shards"]) == 8
    assert len(first["integration_shards"]) == 2


def test_plan_mode_writes_isolated_summary(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "tests/unit").mkdir(parents=True)
    (root / "tests/integration").mkdir(parents=True)
    (root / "tests/unit/test_one.py").write_text("def test_one(): assert True\n", encoding="utf-8")
    (root / "tests/integration/test_two.py").write_text("def test_two(): assert True\n", encoding="utf-8")
    output = tmp_path / "evidence"

    result = run_coverage_baseline_stabilisation(
        root=root,
        output_dir=output,
        execute=False,
        unit_shards=1,
        integration_shards=1,
    )

    assert result["valid"] is True
    assert result["executed"] is False
    assert result["marker_expression"] == MARKER_EXPRESSION
    assert json.loads((output / "summary.json").read_text())["plan"]["total_test_file_count"] == 2


def test_bounded_command_records_timeout_and_artifacts(tmp_path: Path) -> None:
    result = run_bounded_command(
        root=tmp_path,
        output_dir=tmp_path / "artifacts",
        command_id="unit-01-of-01",
        command=[sys.executable, "-c", "import time; print('active', flush=True); time.sleep(2)"],
        timeout_seconds=1,
        env=dict(**__import__("os").environ),
    )

    assert result["timed_out"] is True
    assert result["exit_code"] is None
    assert result["failure_classification"] == "test_execution_timeout"
    assert (tmp_path / "artifacts/unit-01-of-01.stdout.txt").exists()
    assert (tmp_path / "artifacts/unit-01-of-01.stderr.txt").exists()


def test_bounded_command_classifies_threshold_failure_separately(tmp_path: Path) -> None:
    result = run_bounded_command(
        root=tmp_path,
        output_dir=tmp_path / "artifacts",
        command_id="coverage-report-threshold",
        command=[
            sys.executable,
            "-c",
            "print('Coverage failure: total of 63.0 is less than fail-under=70.0'); raise SystemExit(2)",
        ],
        timeout_seconds=5,
        env=dict(**__import__("os").environ),
    )

    assert result["timed_out"] is False
    assert result["exit_code"] == 2
    assert result["failure_classification"] == "coverage_threshold"


def test_contract_is_valid_without_green_execution() -> None:
    result = evaluate_coverage_baseline_stabilisation_contract(require_green=False)

    assert result["contract_valid"] is True
    assert result["wiring_valid"] is True
    assert result["governance_boundary_valid"] is True
    assert result["valid"] is True
    assert result["execution_8_authorised"] is False


def test_execution_7_coverage_gate_uses_stabilised_runner() -> None:
    gate = next(item for item in command_plan() if item.gate_id == "coverage_execution")

    assert "scripts/coverage_suites/run_coverage_baseline_stabilisation.py" in gate.command
    assert "--execute" in gate.command
    assert "--require-green" in gate.command
    assert "--overall-budget-seconds" in gate.command
    assert "--resume" in gate.command
    assert gate.timeout_seconds == 4200
