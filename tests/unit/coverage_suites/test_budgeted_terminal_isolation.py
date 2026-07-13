from __future__ import annotations

import json
from pathlib import Path
import time

from scripts.coverage_suites.budgeted_terminal_isolation import (
    ExecutionBudget,
    ProgressJournal,
    atomic_write_json,
    build_attempt_fingerprint,
    package_terminal_artifacts,
)
from scripts.coverage_suites.unit_shard_stabilisation import parse_pytest_diagnostics
from scripts.coverage_suites.verify_budgeted_terminal_isolation import verify


def test_small_budget_preserves_packaging_reserve_and_reports_exhaustion() -> None:
    budget = ExecutionBudget.start(2, 1)

    assert budget.can_start(2) is False
    time.sleep(1.05)
    assert budget.snapshot()["budget_exhausted"] is True


def test_atomic_json_replaces_complete_document(tmp_path: Path) -> None:
    path = tmp_path / "progress.json"
    atomic_write_json(path, {"state": "first"})
    atomic_write_json(path, {"state": "second", "complete": True})

    assert json.loads(path.read_text(encoding="utf-8")) == {
        "complete": True,
        "state": "second",
    }
    assert not path.with_name(".progress.json.tmp").exists()


def test_attempt_fingerprint_changes_with_test_content(tmp_path: Path) -> None:
    test_file = tmp_path / "tests/unit/test_demo.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_demo(): assert True\n", encoding="utf-8")
    command = ["python", "-m", "pytest", "tests/unit/test_demo.py"]

    first, _ = build_attempt_fingerprint(
        root=tmp_path,
        command=command,
        timeout_seconds=60,
        test_files=["tests/unit/test_demo.py"],
        marker_expression="not slow",
        revision="abc",
    )
    test_file.write_text("def test_demo(): assert False\n", encoding="utf-8")
    second, _ = build_attempt_fingerprint(
        root=tmp_path,
        command=command,
        timeout_seconds=60,
        test_files=["tests/unit/test_demo.py"],
        marker_expression="not slow",
        revision="abc",
    )

    assert first != second


def test_progress_journal_reuses_compatible_attempt(tmp_path: Path) -> None:
    budget = ExecutionBudget.start(60, 10)
    journal = ProgressJournal(
        output_dir=tmp_path,
        revision="abc",
        plan_fingerprint="plan",
        resume=True,
        budget=budget,
    )
    identity = {"command": ["pytest"]}
    result = {"green": True, "exit_code": 0}
    journal.record_attempt(
        kind="node",
        attempt_id="node-1",
        fingerprint="fingerprint",
        identity=identity,
        result=result,
        reused=False,
    )

    resumed = ProgressJournal(
        output_dir=tmp_path,
        revision="abc",
        plan_fingerprint="plan",
        resume=True,
        budget=budget,
    )

    assert resumed.load_cached("fingerprint")["green"] is True
    assert "node-1" in resumed.payload["completed_node_attempt_ids"]


def test_diagnostics_record_every_terminal_status() -> None:
    stdout = """
tests/unit/test_a.py::test_pass PASSED [ 16%]
tests/unit/test_a.py::test_fail FAILED [ 33%]
tests/unit/test_a.py::test_error ERROR [ 50%]
tests/unit/test_a.py::test_skip SKIPPED [ 66%]
tests/unit/test_a.py::test_xfail XFAIL [ 83%]
tests/unit/test_a.py::test_xpass XPASS [100%]
"""
    result = parse_pytest_diagnostics(stdout, "")

    assert result["completed_node_count"] == 6
    assert result["passed_nodeids"] == ["tests/unit/test_a.py::test_pass"]
    assert result["skipped_nodeids"] == ["tests/unit/test_a.py::test_skip"]
    assert result["xfailed_nodeids"] == ["tests/unit/test_a.py::test_xfail"]
    assert result["xpassed_nodeids"] == ["tests/unit/test_a.py::test_xpass"]


def test_partial_terminal_artifacts_are_packaged(tmp_path: Path) -> None:
    atomic_write_json(tmp_path / "summary.json", {"valid": True, "partial": True})
    atomic_write_json(tmp_path / "terminal-progress.json", {"resume_supported": True})
    atomic_write_json(tmp_path / "resume-manifest.json", {"resume_supported": True})
    terminal = tmp_path / "terminal-isolation"
    terminal.mkdir()
    (terminal / "attempt.txt").write_text("done\n", encoding="utf-8")

    package = package_terminal_artifacts(tmp_path)

    assert Path(package["archive"]).is_file()
    assert Path(package["checksum"]).is_file()
    assert package["sha256"] in Path(package["checksum"]).read_text(encoding="utf-8")


def test_budgeted_terminal_contract_is_valid() -> None:
    result = verify()

    assert result["valid"] is True
    assert result["execution_8_authorised"] is False
