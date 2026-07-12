"""Adaptive unit-shard stabilisation for Execution-7 coverage remediation.

The first deterministic coverage split proved that both integration shards complete,
while six large unit shards time out and two complete with concrete failures. This
module keeps the original eight-parent authority model, but adaptively bisects only
unit work that times out. Each leaf executes in a disposable Git worktree so tracked
file mutation can be attributed to the exact leaf without dirtying the operator's
branch.

This remains remediation machinery. It neither captures green Execution-7 evidence
nor authorises Execution-8.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Sequence

from scripts.coverage_suites.coverage_baseline_stabilisation import (
    DEFAULT_UNIT_SHARDS,
    MARKER_EXPRESSION,
    PRD_ID,
    ROOT,
    CoverageShard,
    build_shard_plan,
    run_bounded_command,
)

REMEDIATION_ID = "PRD-11.0R.EXECUTION-7.UNIT-SHARD-STABILISATION"
OUTPUT_DIR = ROOT / "var/prd11/runtime-restore/execution-7/unit-shard-stabilisation"
CONTRACT = ROOT / "docs/roadmap/production_readiness/unit_shard_stabilisation_contract.json"
DEFAULT_INITIAL_LEAF_SHARDS = 2
DEFAULT_MAX_BISECTION_DEPTH = 3
DEFAULT_LEAF_TIMEOUT_SECONDS = 300
DEFAULT_TERMINAL_NODE_TIMEOUT_SECONDS = 60
DEFAULT_WORKERS = 2


@dataclass(frozen=True)
class UnitLeafShard:
    leaf_id: str
    parent_shard_id: str
    depth: int
    ordinal: int
    test_files: tuple[str, ...]
    estimated_bytes: int
    timeout_seconds: int


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _artifact_ref(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _estimated_size(root: Path, relative: str) -> int:
    try:
        return (root / relative).stat().st_size
    except OSError:
        return 1


def _balanced_leaf_groups(root: Path, files: Sequence[str], group_count: int) -> list[tuple[str, ...]]:
    if not files:
        return []
    count = max(1, min(group_count, len(files)))
    buckets: list[list[str]] = [[] for _ in range(count)]
    weights = [0 for _ in range(count)]
    ordered = sorted(files, key=lambda item: (-_estimated_size(root, item), item))
    for item in ordered:
        index = min(range(count), key=lambda value: (weights[value], len(buckets[value]), value))
        buckets[index].append(item)
        weights[index] += _estimated_size(root, item)
    return [tuple(sorted(bucket)) for bucket in buckets if bucket]


def parent_unit_shards(root: Path = ROOT, *, parent_shard_count: int = DEFAULT_UNIT_SHARDS) -> list[CoverageShard]:
    plan = build_shard_plan(root, unit_shards=parent_shard_count)
    return [CoverageShard(**item) for item in plan["unit_shards"]]


def split_unit_leaf(
    root: Path,
    *,
    parent_shard_id: str,
    files: Sequence[str],
    depth: int,
    group_count: int,
    timeout_seconds: int,
    prefix: str | None = None,
) -> list[UnitLeafShard]:
    groups = _balanced_leaf_groups(root, files, group_count)
    base = prefix or parent_shard_id
    total = len(groups)
    leaves: list[UnitLeafShard] = []
    for ordinal, group in enumerate(groups, start=1):
        leaf_id = f"{base}.d{depth}-{ordinal:02d}-of-{total:02d}"
        leaves.append(
            UnitLeafShard(
                leaf_id=leaf_id,
                parent_shard_id=parent_shard_id,
                depth=depth,
                ordinal=ordinal,
                test_files=group,
                estimated_bytes=sum(_estimated_size(root, item) for item in group),
                timeout_seconds=timeout_seconds,
            )
        )
    return leaves


def build_unit_stabilisation_plan(
    root: Path = ROOT,
    *,
    parent_shard_count: int = DEFAULT_UNIT_SHARDS,
    initial_leaf_shards: int = DEFAULT_INITIAL_LEAF_SHARDS,
    max_bisection_depth: int = DEFAULT_MAX_BISECTION_DEPTH,
    leaf_timeout_seconds: int = DEFAULT_LEAF_TIMEOUT_SECONDS,
    parent_shard_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    parents = parent_unit_shards(root, parent_shard_count=parent_shard_count)
    selected = set(parent_shard_ids or [item.shard_id for item in parents])
    unknown = sorted(selected - {item.shard_id for item in parents})
    if unknown:
        raise ValueError(f"unknown parent unit shard ids: {', '.join(unknown)}")
    selected_parents = [item for item in parents if item.shard_id in selected]
    initial: list[UnitLeafShard] = []
    for parent in selected_parents:
        initial.extend(
            split_unit_leaf(
                root,
                parent_shard_id=parent.shard_id,
                files=parent.test_files,
                depth=1,
                group_count=initial_leaf_shards,
                timeout_seconds=leaf_timeout_seconds,
            )
        )
    return {
        "parent_shard_count": len(parents),
        "selected_parent_shard_ids": [item.shard_id for item in selected_parents],
        "selected_parent_test_file_count": sum(len(item.test_files) for item in selected_parents),
        "initial_leaf_shards": [asdict(item) for item in initial],
        "initial_leaf_shard_count": len(initial),
        "max_bisection_depth": max_bisection_depth,
        "leaf_timeout_seconds": leaf_timeout_seconds,
        "execution_isolation": "disposable_git_worktree_per_leaf",
    }


def parse_pytest_diagnostics(stdout: str, stderr: str) -> dict[str, Any]:
    text = f"{stdout}\n{stderr}"
    status_pattern = re.compile(
        r"^(?P<nodeid>tests/[^\s]+?::[^\s]+)\s+(?P<status>PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)",
        flags=re.MULTILINE,
    )
    status_rows = [(match.group("nodeid"), match.group("status")) for match in status_pattern.finditer(text)]
    failed = [nodeid for nodeid, status in status_rows if status == "FAILED"]
    errors = [nodeid for nodeid, status in status_rows if status == "ERROR"]
    for pattern, target in (
        (re.compile(r"^FAILED\s+(tests/\S+)", flags=re.MULTILINE), failed),
        (re.compile(r"^ERROR\s+(tests/\S+)", flags=re.MULTILINE), errors),
    ):
        for match in pattern.finditer(text):
            if match.group(1) not in target:
                target.append(match.group(1))
    active_lines = [line.strip() for line in text.splitlines() if "tests/" in line and "::" in line]
    duration_rows = []
    duration_pattern = re.compile(r"^\s*(\d+(?:\.\d+)?)s\s+\w+\s+(tests/\S+)", flags=re.MULTILINE)
    for match in duration_pattern.finditer(text):
        duration_rows.append({"seconds": float(match.group(1)), "nodeid": match.group(2)})
    return {
        "failed_nodeids": sorted(set(failed)),
        "error_nodeids": sorted(set(errors)),
        "last_active_test_line": active_lines[-1] if active_lines else None,
        "completed_node_count": len(status_rows),
        "slowest_tests": sorted(duration_rows, key=lambda item: (-item["seconds"], item["nodeid"]))[:25],
    }


def _leaf_command(leaf: UnitLeafShard) -> list[str]:
    return [
        sys.executable,
        "-m",
        "coverage",
        "run",
        "--parallel-mode",
        "-m",
        "pytest",
        "-c",
        "pytest.ini",
        *leaf.test_files,
        "-m",
        MARKER_EXPRESSION,
        "-vv",
        "--tb=short",
        "--durations=25",
        "--durations-min=1.0",
        "-ra",
    ]


def _terminal_file_command(test_file: str) -> list[str]:
    return [
        sys.executable,
        "-X",
        "faulthandler",
        "-m",
        "coverage",
        "run",
        "--parallel-mode",
        "-m",
        "pytest",
        "-c",
        "pytest.ini",
        test_file,
        "-m",
        MARKER_EXPRESSION,
        "-vv",
        "--tb=short",
        "--durations=10",
        "--durations-min=1.0",
        "-ra",
    ]


def _collect_only_command(test_file: str) -> list[str]:
    return [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        "pytest.ini",
        test_file,
        "-m",
        MARKER_EXPRESSION,
        "--collect-only",
        "-q",
    ]


def _terminal_node_command(nodeid: str) -> list[str]:
    return [
        sys.executable,
        "-X",
        "faulthandler",
        "-m",
        "pytest",
        "-c",
        "pytest.ini",
        nodeid,
        "-vv",
        "--tb=short",
        "-ra",
    ]


def _git_available(root: Path) -> bool:
    return (root / ".git").exists() and shutil.which("git") is not None


def _git_output(root: Path, *args: str) -> tuple[int, str, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def _remove_coverage_attempt(coverage_data_dir: Path, leaf_id: str) -> None:
    for path in coverage_data_dir.glob(f".coverage.{leaf_id}*"):
        path.unlink(missing_ok=True)


def _run_leaf_in_worktree(
    *,
    root: Path,
    output_dir: Path,
    coverage_data_dir: Path,
    leaf: UnitLeafShard,
) -> dict[str, Any]:
    if not _git_available(root):
        raise RuntimeError("disposable Git worktree execution requires a Git checkout")
    worktree_parent = Path(tempfile.mkdtemp(prefix="eduboost-unit-leaf-"))
    worktree = worktree_parent / "repo"
    code, _, stderr = _git_output(root, "worktree", "add", "--detach", "--quiet", str(worktree), "HEAD")
    if code != 0:
        shutil.rmtree(worktree_parent, ignore_errors=True)
        raise RuntimeError(f"git worktree add failed for {leaf.leaf_id}: {stderr.strip()}")

    source_venv = root / ".venv"
    if source_venv.exists() and not (worktree / ".venv").exists():
        (worktree / ".venv").symlink_to(source_venv, target_is_directory=True)

    env = _base_isolated_env(output_dir, worktree_parent, coverage_data_dir, leaf.leaf_id)

    try:
        result = run_bounded_command(
            root=worktree,
            output_dir=output_dir / "leaves",
            command_id=leaf.leaf_id,
            command=_leaf_command(leaf),
            timeout_seconds=leaf.timeout_seconds,
            env=env,
        )
        status_code, status_stdout, status_stderr = _git_output(worktree, "status", "--porcelain=v1", "--untracked-files=no")
        _, names_stdout, _ = _git_output(worktree, "diff", "--name-only")
        _, stat_stdout, _ = _git_output(worktree, "diff", "--stat")
        _, patch_stdout, patch_stderr = _git_output(worktree, "diff", "--binary")
        patch_path = output_dir / "mutations" / f"{leaf.leaf_id}.patch"
        _write_text(patch_path, patch_stdout if patch_stdout else patch_stderr)
        stdout_path = output_dir / "leaves" / f"{leaf.leaf_id}.stdout.txt"
        stderr_path = output_dir / "leaves" / f"{leaf.leaf_id}.stderr.txt"
        stdout = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
        stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
        diagnostics = parse_pytest_diagnostics(stdout, stderr_text)
        mutation_entries = sorted(line for line in status_stdout.splitlines() if line.strip())
        result.update(
            {
                "parent_shard_id": leaf.parent_shard_id,
                "leaf_depth": leaf.depth,
                "test_file_count": len(leaf.test_files),
                "test_files": list(leaf.test_files),
                "estimated_bytes": leaf.estimated_bytes,
                "pytest_diagnostics": diagnostics,
                "isolated_worktree_used": True,
                "isolated_worktree_status_exit_code": status_code,
                "isolated_worktree_status_stderr": status_stderr[-4000:],
                "tracked_mutation_entries": mutation_entries,
                "tracked_mutation_files": sorted(line for line in names_stdout.splitlines() if line.strip()),
                "tracked_mutation_stat": stat_stdout[-12000:],
                "tracked_mutation_patch": _artifact_ref(patch_path, root),
                "source_worktree_mutated": bool(mutation_entries),
                "stdout_artifact": _artifact_ref(stdout_path, root),
                "stderr_artifact": _artifact_ref(stderr_path, root),
            }
        )
        if result.get("timed_out") is True:
            _remove_coverage_attempt(coverage_data_dir, leaf.leaf_id)
        _write_json(output_dir / "leaves" / f"{leaf.leaf_id}.json", result)
        return result
    finally:
        _git_output(root, "worktree", "remove", "--force", str(worktree))
        _git_output(root, "worktree", "prune")
        shutil.rmtree(worktree_parent, ignore_errors=True)


def _base_isolated_env(output_dir: Path, worktree_parent: Path, coverage_data_dir: Path, command_id: str) -> dict[str, str]:
    leaf_tmp = worktree_parent / "tmp"
    leaf_home = worktree_parent / "home"
    leaf_tmp.mkdir(parents=True, exist_ok=True)
    leaf_home.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PYTHONPATH"] = "." + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["APP_ENV"] = "test"
    env["ENVIRONMENT"] = "test"
    env["DEBUG"] = "false"
    env["PYTHONHASHSEED"] = "0"
    env["TMPDIR"] = str(leaf_tmp)
    env["TEMP"] = str(leaf_tmp)
    env["TMP"] = str(leaf_tmp)
    env["HOME"] = str(leaf_home)
    env["XDG_CACHE_HOME"] = str(leaf_home / ".cache")
    env["COVERAGE_FILE"] = str(coverage_data_dir / f".coverage.{command_id}")
    env["EDUBOOST_TEST_ARTIFACT_ROOT"] = str(output_dir / "test-artifacts" / command_id)
    return env


def _parse_collected_nodeids(stdout: str, test_file: str) -> list[str]:
    nodeids: list[str] = []
    prefix = f"{test_file}::"
    for line in stdout.splitlines():
        value = line.strip()
        if value.startswith(prefix) and value not in nodeids:
            nodeids.append(value)
    return nodeids


def _run_terminal_isolation_in_worktree(
    *,
    root: Path,
    output_dir: Path,
    coverage_data_dir: Path,
    leaf: UnitLeafShard,
    node_timeout_seconds: int,
) -> dict[str, Any]:
    if not _git_available(root):
        raise RuntimeError("terminal isolation requires a Git checkout")
    worktree_parent = Path(tempfile.mkdtemp(prefix="eduboost-terminal-leaf-"))
    worktree = worktree_parent / "repo"
    code, _, stderr = _git_output(root, "worktree", "add", "--detach", "--quiet", str(worktree), "HEAD")
    if code != 0:
        shutil.rmtree(worktree_parent, ignore_errors=True)
        raise RuntimeError(f"git worktree add failed for terminal {leaf.leaf_id}: {stderr.strip()}")

    source_venv = root / ".venv"
    if source_venv.exists() and not (worktree / ".venv").exists():
        (worktree / ".venv").symlink_to(source_venv, target_is_directory=True)

    terminal_dir = output_dir / "terminal-isolation"
    file_attempts: list[dict[str, Any]] = []
    node_attempts: list[dict[str, Any]] = []
    timeout_nodeids: list[str] = []
    failed_nodeids: list[str] = []
    error_nodeids: list[str] = []
    green_nodeids: list[str] = []
    unresolved_files: list[str] = []

    try:
        for test_file in leaf.test_files:
            safe_file_id = test_file.replace("/", "_").replace(":", "_").removesuffix(".py")
            file_command_id = f"{leaf.leaf_id}__file__{safe_file_id}"
            file_env = _base_isolated_env(output_dir, worktree_parent, coverage_data_dir, file_command_id)
            file_result = run_bounded_command(
                root=worktree,
                output_dir=terminal_dir / "files",
                command_id=file_command_id,
                command=_terminal_file_command(test_file),
                timeout_seconds=leaf.timeout_seconds,
                env=file_env,
            )
            file_result["test_file"] = test_file
            file_attempts.append(file_result)
            if file_result.get("timed_out") is not True:
                stdout_path = terminal_dir / "files" / f"{file_command_id}.stdout.txt"
                stderr_path = terminal_dir / "files" / f"{file_command_id}.stderr.txt"
                stdout = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
                stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
                diagnostics = parse_pytest_diagnostics(stdout, stderr_text)
                failed_nodeids.extend(diagnostics["failed_nodeids"])
                error_nodeids.extend(diagnostics["error_nodeids"])
                if file_result.get("green") is True:
                    green_nodeids.extend(_parse_collected_nodeids(stdout, test_file))
                continue

            _remove_coverage_attempt(coverage_data_dir, file_command_id)
            collect_command_id = f"{leaf.leaf_id}__collect__{safe_file_id}"
            collect_env = _base_isolated_env(output_dir, worktree_parent, coverage_data_dir, collect_command_id)
            collect_result = run_bounded_command(
                root=worktree,
                output_dir=terminal_dir / "collect",
                command_id=collect_command_id,
                command=_collect_only_command(test_file),
                timeout_seconds=min(leaf.timeout_seconds, 120),
                env=collect_env,
            )
            collect_result["test_file"] = test_file
            node_attempts.append(collect_result)
            collect_stdout = (terminal_dir / "collect" / f"{collect_command_id}.stdout.txt").read_text(
                encoding="utf-8",
                errors="replace",
            )
            nodeids = _parse_collected_nodeids(collect_stdout, test_file)
            if not nodeids:
                unresolved_files.append(test_file)
                continue
            for nodeid in nodeids:
                safe_node_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid)
                node_command_id = f"{leaf.leaf_id}__node__{safe_node_id}"[:220]
                node_env = _base_isolated_env(output_dir, worktree_parent, coverage_data_dir, node_command_id)
                node_result = run_bounded_command(
                    root=worktree,
                    output_dir=terminal_dir / "nodes",
                    command_id=node_command_id,
                    command=_terminal_node_command(nodeid),
                    timeout_seconds=node_timeout_seconds,
                    env=node_env,
                )
                node_result["nodeid"] = nodeid
                node_result["test_file"] = test_file
                node_attempts.append(node_result)
                if node_result.get("timed_out") is True:
                    timeout_nodeids.append(nodeid)
                elif node_result.get("green") is True:
                    green_nodeids.append(nodeid)
                else:
                    stdout_path = terminal_dir / "nodes" / f"{node_command_id}.stdout.txt"
                    stderr_path = terminal_dir / "nodes" / f"{node_command_id}.stderr.txt"
                    stdout = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
                    stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
                    diagnostics = parse_pytest_diagnostics(stdout, stderr_text)
                    failed_nodeids.extend(diagnostics["failed_nodeids"] or [nodeid])
                    error_nodeids.extend(diagnostics["error_nodeids"])
        status_code, status_stdout, status_stderr = _git_output(worktree, "status", "--porcelain=v1", "--untracked-files=no")
        return {
            "leaf_id": leaf.leaf_id,
            "test_files": list(leaf.test_files),
            "terminal_file_attempt_count": len(file_attempts),
            "terminal_node_attempt_count": len([item for item in node_attempts if "__node__" in item.get("command_id", "")]),
            "terminal_collect_attempt_count": len([item for item in node_attempts if "__collect__" in item.get("command_id", "")]),
            "terminal_timeout_nodeids": sorted(set(timeout_nodeids)),
            "terminal_failed_nodeids": sorted(set(failed_nodeids)),
            "terminal_error_nodeids": sorted(set(error_nodeids)),
            "terminal_green_nodeids": sorted(set(green_nodeids)),
            "terminal_unresolved_files": sorted(set(unresolved_files)),
            "terminal_green": not timeout_nodeids and not failed_nodeids and not error_nodeids and not unresolved_files,
            "file_attempts": file_attempts,
            "node_attempts": node_attempts,
            "isolated_worktree_status": {
                "exit_code": status_code,
                "entries": sorted(line for line in status_stdout.splitlines() if line.strip()),
                "stderr": status_stderr[-4000:],
            },
        }
    finally:
        _git_output(root, "worktree", "remove", "--force", str(worktree))
        _git_output(root, "worktree", "prune")
        shutil.rmtree(worktree_parent, ignore_errors=True)


def run_terminal_isolation(
    *,
    root: Path,
    output_dir: Path,
    coverage_data_dir: Path,
    timed_out_results: Sequence[dict[str, Any]],
    leaf_timeout_seconds: int,
    node_timeout_seconds: int = DEFAULT_TERMINAL_NODE_TIMEOUT_SECONDS,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for result in sorted(timed_out_results, key=lambda item: item["command_id"]):
        leaf = _leaf_from_result(result, timeout_seconds=leaf_timeout_seconds)
        terminal_result = _run_terminal_isolation_in_worktree(
            root=root,
            output_dir=output_dir,
            coverage_data_dir=coverage_data_dir,
            leaf=leaf,
            node_timeout_seconds=node_timeout_seconds,
        )
        _write_json(output_dir / "terminal-isolation" / "leaves" / f"{leaf.leaf_id}.json", terminal_result)
        results.append(terminal_result)
    return results


def _execute_leaf_batch(
    *,
    root: Path,
    output_dir: Path,
    coverage_data_dir: Path,
    leaves: Sequence[UnitLeafShard],
    workers: int,
) -> list[dict[str, Any]]:
    if not leaves:
        return []
    count = max(1, min(workers, len(leaves)))
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=count) as executor:
        futures = {
            executor.submit(
                _run_leaf_in_worktree,
                root=root,
                output_dir=output_dir,
                coverage_data_dir=coverage_data_dir,
                leaf=leaf,
            ): leaf
            for leaf in leaves
        }
        for future in as_completed(futures):
            leaf = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:  # pragma: no cover - defensive evidence path
                failure = {
                    "command_id": leaf.leaf_id,
                    "parent_shard_id": leaf.parent_shard_id,
                    "leaf_depth": leaf.depth,
                    "test_files": list(leaf.test_files),
                    "test_file_count": len(leaf.test_files),
                    "started_at": _utc_now(),
                    "completed_at": _utc_now(),
                    "timed_out": False,
                    "exit_code": None,
                    "green": False,
                    "failure_classification": "worktree_execution_error",
                    "remaining_failure_count": 1,
                    "error": str(exc),
                    "tracked_mutation_entries": [],
                    "tracked_mutation_files": [],
                    "source_worktree_mutated": False,
                    "pytest_diagnostics": {
                        "failed_nodeids": [],
                        "error_nodeids": [],
                        "last_active_test_line": None,
                        "completed_node_count": 0,
                        "slowest_tests": [],
                    },
                }
                _write_json(output_dir / "leaves" / f"{leaf.leaf_id}.json", failure)
                results.append(failure)
    return sorted(results, key=lambda item: item["command_id"])


def _timed_out(result: dict[str, Any]) -> bool:
    return result.get("timed_out") is True


def _leaf_from_result(result: dict[str, Any], *, timeout_seconds: int) -> UnitLeafShard:
    return UnitLeafShard(
        leaf_id=str(result["command_id"]),
        parent_shard_id=str(result["parent_shard_id"]),
        depth=int(result["leaf_depth"]),
        ordinal=1,
        test_files=tuple(result.get("test_files", [])),
        estimated_bytes=int(result.get("estimated_bytes", 0)),
        timeout_seconds=timeout_seconds,
    )


def run_unit_shard_stabilisation(
    *,
    root: Path = ROOT,
    output_dir: Path = OUTPUT_DIR,
    coverage_data_dir: Path | None = None,
    execute: bool,
    parent_shard_count: int = DEFAULT_UNIT_SHARDS,
    parent_shard_ids: Sequence[str] | None = None,
    initial_leaf_shards: int = DEFAULT_INITIAL_LEAF_SHARDS,
    max_bisection_depth: int = DEFAULT_MAX_BISECTION_DEPTH,
    leaf_timeout_seconds: int = DEFAULT_LEAF_TIMEOUT_SECONDS,
    workers: int = DEFAULT_WORKERS,
) -> dict[str, Any]:
    plan = build_unit_stabilisation_plan(
        root,
        parent_shard_count=parent_shard_count,
        initial_leaf_shards=initial_leaf_shards,
        max_bisection_depth=max_bisection_depth,
        leaf_timeout_seconds=leaf_timeout_seconds,
        parent_shard_ids=parent_shard_ids,
    )
    planned = {
        "prd_id": PRD_ID,
        "remediation_id": REMEDIATION_ID,
        "executed": False,
        "valid": True,
        "marker_expression": MARKER_EXPRESSION,
        "adaptive_bisection": True,
        "workers": workers,
        "plan": plan,
        "governance_boundary": {
            "execution_7_complete_claimed": False,
            "execution_8_authorised": False,
            "green_evidence_capture_performed": False,
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "plan.json", planned)
    if not execute:
        _write_json(output_dir / "summary.json", planned)
        return planned
    if not _git_available(root):
        raise RuntimeError("unit shard stabilisation must run from a Git checkout")

    data_dir = coverage_data_dir or (output_dir / "coverage-data")
    data_dir.mkdir(parents=True, exist_ok=True)
    started_at = _utc_now()
    pending = [UnitLeafShard(**item) for item in plan["initial_leaf_shards"]]
    all_attempts: list[dict[str, Any]] = []
    final_results: list[dict[str, Any]] = []

    while pending:
        batch_results = _execute_leaf_batch(
            root=root,
            output_dir=output_dir,
            coverage_data_dir=data_dir,
            leaves=pending,
            workers=workers,
        )
        all_attempts.extend(batch_results)
        next_pending: list[UnitLeafShard] = []
        for result in batch_results:
            files = tuple(result.get("test_files", []))
            depth = int(result.get("leaf_depth", 1))
            can_bisect = _timed_out(result) and depth < max_bisection_depth and len(files) > 1
            if can_bisect:
                parent_leaf = _leaf_from_result(result, timeout_seconds=leaf_timeout_seconds)
                children = split_unit_leaf(
                    root,
                    parent_shard_id=parent_leaf.parent_shard_id,
                    files=parent_leaf.test_files,
                    depth=depth + 1,
                    group_count=2,
                    timeout_seconds=leaf_timeout_seconds,
                    prefix=parent_leaf.leaf_id,
                )
                next_pending.extend(children)
            else:
                final_results.append(result)
        pending = next_pending

    timed_out_results = [item for item in final_results if item.get("timed_out") is True]
    terminal_results = run_terminal_isolation(
        root=root,
        output_dir=output_dir,
        coverage_data_dir=data_dir,
        timed_out_results=timed_out_results,
        leaf_timeout_seconds=leaf_timeout_seconds,
    ) if timed_out_results else []
    terminal_timeout_nodeids = sorted(
        {
            nodeid
            for item in terminal_results
            for nodeid in item.get("terminal_timeout_nodeids", [])
        }
    )
    terminal_failed_nodeids = sorted(
        {
            nodeid
            for item in terminal_results
            for nodeid in item.get("terminal_failed_nodeids", [])
        }
    )
    terminal_error_nodeids = sorted(
        {
            nodeid
            for item in terminal_results
            for nodeid in item.get("terminal_error_nodeids", [])
        }
    )
    terminal_green_nodeids = sorted(
        {
            nodeid
            for item in terminal_results
            for nodeid in item.get("terminal_green_nodeids", [])
        }
    )
    terminal_unresolved_files = sorted(
        {
            test_file
            for item in terminal_results
            for test_file in item.get("terminal_unresolved_files", [])
        }
    )
    unresolved_timeout_leaf_ids = sorted(
        item["leaf_id"]
        for item in terminal_results
        if item.get("terminal_unresolved_files")
    )
    timed_out_ids = sorted(item["command_id"] for item in timed_out_results)
    failed_results = [item for item in final_results if item.get("green") is not True and not _timed_out(item)]
    failed_nodeids = sorted(
        {
            nodeid
            for item in final_results
            for nodeid in item.get("pytest_diagnostics", {}).get("failed_nodeids", [])
        }
        | set(terminal_failed_nodeids)
    )
    error_nodeids = sorted(
        {
            nodeid
            for item in final_results
            for nodeid in item.get("pytest_diagnostics", {}).get("error_nodeids", [])
        }
        | set(terminal_error_nodeids)
    )
    mutation_map = {
        item["command_id"]: item.get("tracked_mutation_files", [])
        for item in final_results
        if item.get("tracked_mutation_files")
    }
    terminal_leaf_ids = {item["leaf_id"] for item in terminal_results}
    unresolved_timed_out_results = [
        item
        for item in timed_out_results
        if item["command_id"] not in terminal_leaf_ids or item["command_id"] in unresolved_timeout_leaf_ids
    ]
    incomplete = bool(unresolved_timed_out_results) or any(
        item.get("exit_code") is None and item.get("command_id") not in terminal_leaf_ids
        for item in final_results
    )
    tests_green = (
        bool(final_results)
        and all(item.get("green") is True for item in final_results if item.get("command_id") not in terminal_leaf_ids)
        and bool(terminal_results) == bool(timed_out_results)
        and all(item.get("terminal_green") is True for item in terminal_results)
    )
    worktree_hygiene_green = not mutation_map
    blockers: list[str] = []
    if incomplete:
        blockers.append("unit_shard_execution_incomplete")
    if failed_results:
        blockers.append("unit_test_failures")
    if terminal_timeout_nodeids:
        blockers.append("terminal_timeout_nodes")
    if terminal_failed_nodeids or terminal_error_nodeids:
        blockers.append("terminal_test_failures")
    if mutation_map:
        blockers.append("tracked_worktree_mutation_attributed")

    completed_at = _utc_now()
    tracked_mutation_files = sorted({path for paths in mutation_map.values() for path in paths})
    isolated_statuses = {
        item["command_id"]: {
            "exit_code": item.get("isolated_worktree_status_exit_code"),
            "stderr": item.get("isolated_worktree_status_stderr"),
            "tracked_mutation_entries": item.get("tracked_mutation_entries", []),
        }
        for item in final_results
    }
    isolated_statuses.update(
        {
            item["leaf_id"]: item.get("isolated_worktree_status", {})
            for item in terminal_results
        }
    )
    summary = {
        **planned,
        "executed": True,
        "valid": not blockers,
        "all_green": not blockers,
        "started_at": started_at,
        "completed_at": completed_at,
        "unit_execution_complete": not incomplete,
        "unit_tests_green": tests_green,
        "worktree_hygiene_green": worktree_hygiene_green,
        "terminal_isolation_performed": bool(terminal_results),
        "terminal_file_attempt_count": sum(int(item.get("terminal_file_attempt_count", 0)) for item in terminal_results),
        "terminal_node_attempt_count": sum(int(item.get("terminal_node_attempt_count", 0)) for item in terminal_results),
        "terminal_timeout_nodeids": terminal_timeout_nodeids,
        "terminal_failed_nodeids": terminal_failed_nodeids,
        "terminal_error_nodeids": terminal_error_nodeids,
        "terminal_green_nodeids": terminal_green_nodeids,
        "terminal_unresolved_files": terminal_unresolved_files,
        "confirmed_failed_leaf_count": len(failed_results),
        "unresolved_timeout_leaf_count": len(unresolved_timeout_leaf_ids),
        "initial_attempt_count": plan["initial_leaf_shard_count"],
        "total_attempt_count": len(all_attempts),
        "final_leaf_count": len(final_results),
        "timed_out_leaf_ids": timed_out_ids,
        "unresolved_timeout_leaf_ids": unresolved_timeout_leaf_ids,
        "failed_leaf_ids": sorted(item["command_id"] for item in failed_results),
        "failed_nodeids": failed_nodeids,
        "error_nodeids": error_nodeids,
        "remaining_failure_count": len(failed_nodeids) + len(error_nodeids) + len(terminal_timeout_nodeids),
        "mutation_attribution": mutation_map,
        "tracked_mutation_file_count": len(tracked_mutation_files),
        "tracked_mutation_files": tracked_mutation_files,
        "untracked_runtime_artifact_count": 0,
        "outer_worktree_status": {},
        "isolated_worktree_statuses": isolated_statuses,
        "blockers": blockers,
        "coverage_data_dir": _artifact_ref(data_dir, root),
        "all_attempt_results": all_attempts,
        "final_leaf_results": final_results,
        "terminal_isolation_results": terminal_results,
    }
    _write_json(output_dir / "summary.json", summary)
    return summary


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    path = root / CONTRACT.relative_to(ROOT)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def evaluate_unit_shard_stabilisation_contract(
    root: Path = ROOT,
    *,
    require_green: bool = False,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    contract = load_contract(root)
    target_output = output_dir or (root / OUTPUT_DIR.relative_to(ROOT))
    summary_path = target_output / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    makefile = (root / "Makefile").read_text(encoding="utf-8") if (root / "Makefile").exists() else ""
    baseline_path = root / "scripts/coverage_suites/coverage_baseline_stabilisation.py"
    baseline = baseline_path.read_text(encoding="utf-8") if baseline_path.exists() else ""
    registers = []
    for relative in (
        "docs/roadmap/production_readiness/production_readiness_register.json",
        "docs/roadmap/production_readiness/prd11_production_release_register.json",
        "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_7_coverage_static_security_green_record.json",
    ):
        path = root / relative
        registers.append(json.loads(path.read_text(encoding="utf-8")) if path.exists() else {})

    contract_valid = all(
        [
            contract.get("schema_version") == "prd11.0r/execution-7/unit-shard-stabilisation/v1",
            contract.get("prd_id") == PRD_ID,
            contract.get("remediation_id") == REMEDIATION_ID,
            contract.get("parent_unit_shards") == DEFAULT_UNIT_SHARDS,
            contract.get("adaptive_timeout_bisection") is True,
            contract.get("disposable_git_worktree_per_leaf") is True,
            contract.get("coverage_threshold_unchanged") is True,
            contract.get("green_evidence_capture_allowed") is False,
            contract.get("execution_8_authorised") is False,
        ]
    )
    wiring_valid = all(
        [
            "unit-shard-stabilisation:" in makefile,
            "unit-shard-stabilisation-verify:" in makefile,
            "run_unit_shard_stabilisation" in baseline,
            "coverage_execution_complete" in baseline,
            "coverage_incomplete_shards" in baseline,
        ]
    )
    governance_valid = all(record.get("next_authorised_item") == PRD_ID for record in registers) and registers[-1].get("evidence_recorded") is False
    green_valid = (not require_green) or summary.get("all_green") is True
    return {
        "valid": contract_valid and wiring_valid and governance_valid and green_valid,
        "contract_valid": contract_valid,
        "wiring_valid": wiring_valid,
        "governance_boundary_valid": governance_valid,
        "unit_shard_stabilisation_green": summary.get("all_green") is True,
        "summary_path": _artifact_ref(summary_path, root),
        "blockers": summary.get("blockers", []),
        "next_authorised_item": PRD_ID,
        "execution_8_authorised": False,
    }


def _parse_parent_ids(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        result.extend(item.strip() for item in value.split(",") if item.strip())
    return result


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--require-green", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--parent-shard-id", action="append", default=[])
    parser.add_argument("--parent-shards", type=int, default=DEFAULT_UNIT_SHARDS)
    parser.add_argument("--initial-leaf-shards", type=int, default=DEFAULT_INITIAL_LEAF_SHARDS)
    parser.add_argument("--max-bisection-depth", type=int, default=DEFAULT_MAX_BISECTION_DEPTH)
    parser.add_argument("--leaf-timeout-seconds", type=int, default=DEFAULT_LEAF_TIMEOUT_SECONDS)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--coverage-data-dir", type=Path)
    args = parser.parse_args()
    parent_ids = _parse_parent_ids(args.parent_shard_id)
    result = run_unit_shard_stabilisation(
        execute=args.execute,
        output_dir=args.output_dir,
        coverage_data_dir=args.coverage_data_dir,
        parent_shard_count=args.parent_shards,
        parent_shard_ids=parent_ids or None,
        initial_leaf_shards=args.initial_leaf_shards,
        max_bisection_depth=args.max_bisection_depth,
        leaf_timeout_seconds=args.leaf_timeout_seconds,
        workers=args.workers,
    )
    if args.require_green and result.get("all_green") is not True:
        result["valid"] = False
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result.get("valid") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
