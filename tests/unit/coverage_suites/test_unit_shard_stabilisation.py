from __future__ import annotations

import json
from pathlib import Path
import subprocess

from scripts.coverage_suites.unit_shard_stabilisation import (
    build_unit_stabilisation_plan,
    evaluate_unit_shard_stabilisation_contract,
    parse_pytest_diagnostics,
    run_unit_shard_stabilisation,
    split_unit_leaf,
)


def test_default_plan_preserves_eight_parents_and_creates_sixteen_initial_leaves() -> None:
    plan = build_unit_stabilisation_plan()

    assert plan["parent_shard_count"] == 8
    assert len(plan["selected_parent_shard_ids"]) == 8
    assert plan["initial_leaf_shard_count"] == 16
    assert plan["execution_isolation"] == "disposable_git_worktree_per_leaf"


def test_leaf_split_covers_every_parent_file_once(tmp_path: Path) -> None:
    files = []
    for index in range(5):
        relative = f"tests/unit/test_{index}.py"
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_ok(): assert True\n", encoding="utf-8")
        files.append(relative)

    leaves = split_unit_leaf(
        tmp_path,
        parent_shard_id="unit-01-of-08",
        files=files,
        depth=1,
        group_count=2,
        timeout_seconds=30,
    )

    flattened = [item for leaf in leaves for item in leaf.test_files]
    assert sorted(flattened) == sorted(files)
    assert len(flattened) == len(set(flattened))
    assert all(leaf.parent_shard_id == "unit-01-of-08" for leaf in leaves)


def test_pytest_diagnostics_extract_failures_last_activity_and_durations() -> None:
    stdout = """
tests/unit/test_a.py::test_ok PASSED [ 33%]
tests/unit/test_b.py::test_bad FAILED [ 66%]
============================= slowest 25 durations =============================
2.50s call     tests/unit/test_b.py::test_bad
FAILED tests/unit/test_b.py::test_bad - AssertionError
"""
    result = parse_pytest_diagnostics(stdout, "")

    assert result["failed_nodeids"] == ["tests/unit/test_b.py::test_bad"]
    assert result["last_active_test_line"] is not None
    assert result["completed_node_count"] == 2
    assert result["slowest_tests"][0]["seconds"] == 2.5


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)


def test_disposable_worktree_attributes_mutation_without_dirtying_source(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "tests/unit").mkdir(parents=True)
    (root / "tests/integration").mkdir(parents=True)
    (root / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (root / "tracked.txt").write_text("original\n", encoding="utf-8")
    (root / "tests/unit/test_mutation.py").write_text(
        "from pathlib import Path\n"
        "def test_mutation():\n"
        "    Path('tracked.txt').write_text('changed\\n')\n"
        "    assert True\n",
        encoding="utf-8",
    )
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "fixture")

    output = tmp_path / "evidence"
    result = run_unit_shard_stabilisation(
        root=root,
        output_dir=output,
        execute=True,
        parent_shard_count=1,
        initial_leaf_shards=1,
        max_bisection_depth=1,
        leaf_timeout_seconds=30,
        workers=1,
    )

    assert result["worktree_hygiene_green"] is False
    assert result["mutation_attribution"]
    assert (root / "tracked.txt").read_text(encoding="utf-8") == "original\n"
    assert _git(root, "status", "--porcelain=v1").stdout == ""


def test_contract_and_canonical_wiring_are_valid() -> None:
    result = evaluate_unit_shard_stabilisation_contract(require_green=False)

    assert result["contract_valid"] is True
    assert result["wiring_valid"] is True
    assert result["governance_boundary_valid"] is True
    assert result["valid"] is True
    assert result["execution_8_authorised"] is False


def test_plan_summary_is_json_serializable(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "tests/unit").mkdir(parents=True)
    (root / "tests/integration").mkdir(parents=True)
    (root / "tests/unit/test_one.py").write_text("def test_one(): assert True\n", encoding="utf-8")
    output = tmp_path / "output"

    result = run_unit_shard_stabilisation(
        root=root,
        output_dir=output,
        execute=False,
        parent_shard_count=1,
        initial_leaf_shards=1,
    )

    assert result["executed"] is False
    assert json.loads((output / "summary.json").read_text(encoding="utf-8"))["valid"] is True
