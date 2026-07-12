"""Execution-7 coverage baseline stabilisation helpers.

The original Execution-7 coverage gate used one monolithic ``make test-coverage``
process. On the merged Execution-6/Execution-7 authority base that process was
still actively running when the 900 second gate timeout expired. This module
replaces that opaque execution path with deterministic test-file shards,
independent bounded subprocesses, isolated coverage data, and tracked-worktree
mutation detection.

This is remediation machinery only. It does not mark Execution-7 complete and it
does not authorise Execution-8.
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
import signal
import subprocess
import sys
import time
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"
REMEDIATION_ID = "PRD-11.0R.EXECUTION-7.COVERAGE-BASELINE-STABILISATION"
OUTPUT_DIR = ROOT / "var/prd11/runtime-restore/execution-7/coverage-baseline-stabilisation"
CONTRACT = ROOT / "docs/roadmap/production_readiness/coverage_baseline_stabilisation_contract.json"
MARKER_EXPRESSION = "not governance and not slow and not llm and not e2e"
DEFAULT_THRESHOLD = 70
DEFAULT_UNIT_SHARDS = 8
DEFAULT_INTEGRATION_SHARDS = 2
DEFAULT_WORKERS = 4
DEFAULT_COLLECTION_TIMEOUT_SECONDS = 300
DEFAULT_UNIT_SHARD_TIMEOUT_SECONDS = 600
DEFAULT_INTEGRATION_SHARD_TIMEOUT_SECONDS = 900


@dataclass(frozen=True)
class CoverageShard:
    shard_id: str
    suite: str
    index: int
    test_files: tuple[str, ...]
    estimated_bytes: int
    timeout_seconds: int


@dataclass(frozen=True)
class CommandResult:
    command_id: str
    command: tuple[str, ...]
    started_at: str
    completed_at: str
    duration_seconds: float
    timeout_seconds: int
    timed_out: bool
    exit_code: int | None
    green: bool
    failure_classification: str
    remaining_failure_count: int
    stdout_artifact: str
    stderr_artifact: str
    stdout_tail: str
    stderr_tail: str


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _artifact_ref(path: Path, *, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def discover_test_files(root: Path, suite: str) -> list[Path]:
    """Return deterministic test-file discovery for a supported coverage suite."""
    if suite not in {"unit", "integration"}:
        raise ValueError(f"unsupported coverage suite: {suite}")
    suite_root = root / "tests" / suite
    if not suite_root.exists():
        return []
    return sorted(
        (path.relative_to(root) for path in suite_root.rglob("test_*.py") if path.is_file()),
        key=lambda value: value.as_posix(),
    )


def _estimated_size(root: Path, relative_path: Path) -> int:
    try:
        return (root / relative_path).stat().st_size
    except OSError:
        return 1


def balanced_shards(
    root: Path,
    files: Sequence[Path],
    *,
    suite: str,
    shard_count: int,
    timeout_seconds: int,
) -> list[CoverageShard]:
    """Distribute files deterministically using file size as a stable first estimate.

    The largest files are assigned first to the currently lightest shard. This is
    not claimed to be a runtime-perfect model; the emitted per-shard durations are
    intended to make later balancing evidence-based.
    """
    if shard_count < 1:
        raise ValueError("shard_count must be at least 1")
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be at least 1")
    if not files:
        return []

    count = min(shard_count, len(files))
    buckets: list[list[Path]] = [[] for _ in range(count)]
    weights = [0 for _ in range(count)]
    ordered = sorted(
        files,
        key=lambda path: (-_estimated_size(root, path), path.as_posix()),
    )
    for path in ordered:
        index = min(range(count), key=lambda item: (weights[item], len(buckets[item]), item))
        buckets[index].append(path)
        weights[index] += _estimated_size(root, path)

    shards: list[CoverageShard] = []
    for index, bucket in enumerate(buckets, start=1):
        ordered_bucket = tuple(sorted((item.as_posix() for item in bucket)))
        shards.append(
            CoverageShard(
                shard_id=f"{suite}-{index:02d}-of-{count:02d}",
                suite=suite,
                index=index,
                test_files=ordered_bucket,
                estimated_bytes=sum(_estimated_size(root, Path(item)) for item in ordered_bucket),
                timeout_seconds=timeout_seconds,
            )
        )
    return shards


def build_shard_plan(
    root: Path = ROOT,
    *,
    unit_shards: int = DEFAULT_UNIT_SHARDS,
    integration_shards: int = DEFAULT_INTEGRATION_SHARDS,
    unit_timeout_seconds: int = DEFAULT_UNIT_SHARD_TIMEOUT_SECONDS,
    integration_timeout_seconds: int = DEFAULT_INTEGRATION_SHARD_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    unit_files = discover_test_files(root, "unit")
    integration_files = discover_test_files(root, "integration")
    unit_plan = balanced_shards(
        root,
        unit_files,
        suite="unit",
        shard_count=unit_shards,
        timeout_seconds=unit_timeout_seconds,
    )
    integration_plan = balanced_shards(
        root,
        integration_files,
        suite="integration",
        shard_count=integration_shards,
        timeout_seconds=integration_timeout_seconds,
    )
    return {
        "unit_test_file_count": len(unit_files),
        "integration_test_file_count": len(integration_files),
        "total_test_file_count": len(unit_files) + len(integration_files),
        "unit_shards": [asdict(item) for item in unit_plan],
        "integration_shards": [asdict(item) for item in integration_plan],
    }


def _parse_collected_count(stdout: str, stderr: str) -> int | None:
    text = f"{stdout}\n{stderr}"
    patterns = (
        r"collected\s+(\d+)\s+items?",
        r"(\d+)\s+tests?\s+collected",
        r"(\d+)\s+items?\s+collected",
    )
    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            return int(matches[-1])
    return None


def _remaining_failure_count(stdout: str, stderr: str, exit_code: int | None) -> int:
    if exit_code == 0:
        return 0
    text = f"{stdout}\n{stderr}"
    counts = []
    for pattern in (r"(\d+) failed", r"(\d+) errors?", r"(\d+) xfailed"):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            counts.append(int(match.group(1)))
    if counts:
        return sum(counts)
    node_failures = len(re.findall(r"^(FAILED|ERROR)\s+", text, flags=re.MULTILINE))
    return node_failures or 1


def _classify_failure(
    *,
    command_id: str,
    stdout: str,
    stderr: str,
    exit_code: int | None,
    timed_out: bool,
) -> str:
    if timed_out:
        if command_id.startswith("collection-"):
            return "collection_timeout"
        if command_id.startswith("unit-") or command_id.startswith("integration-"):
            return "test_execution_timeout"
        return "timeout"
    if exit_code == 0:
        return "green"
    text = f"{stdout}\n{stderr}".lower()
    if "no module named" in text or "command not found" in text:
        return "missing_tool"
    if "database" in text and any(token in text for token in ("connection refused", "could not connect", "timeout")):
        return "database_wait_or_connection_failure"
    if "redis" in text and any(token in text for token in ("connection refused", "could not connect", "timeout")):
        return "external_service_wait_or_connection_failure"
    if command_id.startswith("collection-"):
        return "collection_failed"
    if command_id.startswith("unit-") or command_id.startswith("integration-"):
        return "test_failures"
    if command_id == "coverage-combine":
        return "coverage_combine_failed"
    if command_id.startswith("coverage-report"):
        return "coverage_report_generation_failed"
    return "command_failed"


def _terminate_process_group(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (AttributeError, ProcessLookupError, PermissionError):
        process.terminate()
    try:
        process.wait(timeout=5)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (AttributeError, ProcessLookupError, PermissionError):
        process.kill()
    process.wait(timeout=5)


def run_bounded_command(
    *,
    root: Path,
    output_dir: Path,
    command_id: str,
    command: Sequence[str],
    timeout_seconds: int,
    env: dict[str, str],
) -> dict[str, Any]:
    """Execute one subprocess and persist complete stdout/stderr artifacts."""
    started = _utc_now()
    monotonic_started = time.monotonic()
    timed_out = False
    process = subprocess.Popen(
        list(command),
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        exit_code: int | None = process.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        partial_stdout = _text(exc.stdout)
        partial_stderr = _text(exc.stderr)
        _terminate_process_group(process)
        tail_stdout, tail_stderr = process.communicate()
        stdout = partial_stdout + _text(tail_stdout)
        stderr = partial_stderr + _text(tail_stderr)
        stderr += f"\nCommand timed out after {timeout_seconds} seconds.\n"
        exit_code = None

    completed = _utc_now()
    stdout_path = output_dir / f"{command_id}.stdout.txt"
    stderr_path = output_dir / f"{command_id}.stderr.txt"
    _write_text(stdout_path, stdout)
    _write_text(stderr_path, stderr)
    result = CommandResult(
        command_id=command_id,
        command=tuple(command),
        started_at=started.isoformat(),
        completed_at=completed.isoformat(),
        duration_seconds=round(time.monotonic() - monotonic_started, 3),
        timeout_seconds=timeout_seconds,
        timed_out=timed_out,
        exit_code=exit_code,
        green=exit_code == 0,
        failure_classification=_classify_failure(
            command_id=command_id,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=timed_out,
        ),
        remaining_failure_count=_remaining_failure_count(stdout, stderr, exit_code),
        stdout_artifact=_artifact_ref(stdout_path, root=root),
        stderr_artifact=_artifact_ref(stderr_path, root=root),
        stdout_tail=stdout[-12000:],
        stderr_tail=stderr[-12000:],
    )
    payload = asdict(result)
    _write_json(output_dir / f"{command_id}.json", payload)
    return payload


def _git_tracked_status(root: Path) -> dict[str, Any]:
    if not (root / ".git").exists() or shutil.which("git") is None:
        return {"available": False, "entries": [], "clean": None}
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=no"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    entries = sorted(line.rstrip() for line in completed.stdout.splitlines() if line.strip())
    return {
        "available": completed.returncode == 0,
        "exit_code": completed.returncode,
        "entries": entries,
        "clean": completed.returncode == 0 and not entries,
        "stderr": completed.stderr[-4000:],
    }


def _new_tracked_mutations(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    before_entries = set(before.get("entries", []))
    after_entries = set(after.get("entries", []))
    return sorted(after_entries - before_entries)


def _base_env(root: Path, coverage_data_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "." + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env.setdefault("APP_ENV", "test")
    env.setdefault("ENVIRONMENT", "test")
    env.setdefault("DEBUG", "false")
    env["COVERAGE_FILE"] = str(coverage_data_dir / ".coverage")
    env["PYTHONHASHSEED"] = "0"
    return env


def _collection_command(root: Path, suite: str) -> list[str]:
    return [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        "pytest.ini",
        str(Path("tests") / suite),
        "-m",
        MARKER_EXPRESSION,
        "--collect-only",
        "-q",
    ]


def _shard_command(shard: CoverageShard) -> list[str]:
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
        *shard.test_files,
        "-m",
        MARKER_EXPRESSION,
        "-q",
        "--tb=short",
    ]


def _run_shards_parallel(
    *,
    root: Path,
    output_dir: Path,
    shards: Sequence[CoverageShard],
    workers: int,
    env: dict[str, str],
) -> list[dict[str, Any]]:
    if not shards:
        return []
    worker_count = max(1, min(workers, len(shards)))
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map = {
            executor.submit(
                run_bounded_command,
                root=root,
                output_dir=output_dir / "shards",
                command_id=shard.shard_id,
                command=_shard_command(shard),
                timeout_seconds=shard.timeout_seconds,
                env=env,
            ): shard
            for shard in shards
        }
        for future in as_completed(future_map):
            results.append(future.result())
    return sorted(results, key=lambda item: item["command_id"])


def _run_shards_sequential(
    *,
    root: Path,
    output_dir: Path,
    shards: Sequence[CoverageShard],
    env: dict[str, str],
) -> list[dict[str, Any]]:
    return [
        run_bounded_command(
            root=root,
            output_dir=output_dir / "shards",
            command_id=shard.shard_id,
            command=_shard_command(shard),
            timeout_seconds=shard.timeout_seconds,
            env=env,
        )
        for shard in shards
    ]


def _load_coverage_percent(path: Path) -> float | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    totals = payload.get("totals", {}) if isinstance(payload.get("totals"), dict) else {}
    value = totals.get("percent_covered")
    return float(value) if isinstance(value, (int, float)) else None


def run_coverage_baseline_stabilisation(
    *,
    root: Path = ROOT,
    output_dir: Path = OUTPUT_DIR,
    execute: bool,
    threshold: int = DEFAULT_THRESHOLD,
    unit_shards: int = DEFAULT_UNIT_SHARDS,
    integration_shards: int = DEFAULT_INTEGRATION_SHARDS,
    workers: int = DEFAULT_WORKERS,
    collection_timeout_seconds: int = DEFAULT_COLLECTION_TIMEOUT_SECONDS,
    unit_timeout_seconds: int = DEFAULT_UNIT_SHARD_TIMEOUT_SECONDS,
    integration_timeout_seconds: int = DEFAULT_INTEGRATION_SHARD_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    plan = build_shard_plan(
        root,
        unit_shards=unit_shards,
        integration_shards=integration_shards,
        unit_timeout_seconds=unit_timeout_seconds,
        integration_timeout_seconds=integration_timeout_seconds,
    )
    planned = {
        "prd_id": PRD_ID,
        "remediation_id": REMEDIATION_ID,
        "executed": False,
        "valid": True,
        "marker_expression": MARKER_EXPRESSION,
        "coverage_threshold": threshold,
        "unit_parallel_workers": workers,
        "integration_execution": "sequential",
        "coverage_artifacts_isolated": True,
        "tracked_worktree_clean_required": True,
        "plan": plan,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "plan.json", planned)
    if not execute:
        _write_json(output_dir / "summary.json", planned)
        return planned

    started_at = _utc_now()
    coverage_data_dir = output_dir / "coverage-data"
    if coverage_data_dir.exists():
        shutil.rmtree(coverage_data_dir)
    coverage_data_dir.mkdir(parents=True, exist_ok=True)
    for stale in (output_dir / "coverage.json", output_dir / "coverage.xml"):
        stale.unlink(missing_ok=True)
    html_dir = output_dir / "html"
    if html_dir.exists():
        shutil.rmtree(html_dir)

    before_status = _git_tracked_status(root)
    env = _base_env(root, coverage_data_dir)

    collection_results: list[dict[str, Any]] = []
    collection_counts: dict[str, int | None] = {}
    for suite in ("unit", "integration"):
        result = run_bounded_command(
            root=root,
            output_dir=output_dir / "collection",
            command_id=f"collection-{suite}",
            command=_collection_command(root, suite),
            timeout_seconds=collection_timeout_seconds,
            env=env,
        )
        result["collected_test_count"] = _parse_collected_count(result["stdout_tail"], result["stderr_tail"])
        _write_json(output_dir / "collection" / f"collection-{suite}.json", result)
        collection_results.append(result)
        collection_counts[suite] = result["collected_test_count"]

    integration_plan = [CoverageShard(**item) for item in plan["integration_shards"]]

    # Unit execution now uses adaptive timeout bisection in disposable Git
    # worktrees. Import locally to avoid a module-level circular dependency:
    # the unit stabiliser reuses this module's deterministic parent plan and
    # bounded-command evidence contract.
    from scripts.coverage_suites.unit_shard_stabilisation import (
        run_unit_shard_stabilisation,
    )

    unit_stabilisation = run_unit_shard_stabilisation(
        root=root,
        output_dir=output_dir / "unit-shard-stabilisation",
        coverage_data_dir=coverage_data_dir,
        execute=True,
        parent_shard_count=unit_shards,
        leaf_timeout_seconds=min(unit_timeout_seconds, 300),
        workers=max(1, min(workers, 2)),
    )
    unit_results = list(unit_stabilisation.get("final_leaf_results", []))
    integration_results = _run_shards_sequential(
        root=root,
        output_dir=output_dir,
        shards=integration_plan,
        env=env,
    )
    shard_results = unit_results + integration_results

    coverage_execution_complete = bool(shard_results) and all(
        item.get("timed_out") is not True and item.get("exit_code") is not None
        for item in shard_results
    )
    report_results: list[dict[str, Any]] = []
    if coverage_execution_complete:
        combine_result = run_bounded_command(
            root=root,
            output_dir=output_dir / "reports",
            command_id="coverage-combine",
            command=[sys.executable, "-m", "coverage", "combine", "--keep", str(coverage_data_dir)],
            timeout_seconds=120,
            env=env,
        )
        report_results.append(combine_result)

        report_commands: list[tuple[str, list[str], int]] = [
            ("coverage-report-json", [sys.executable, "-m", "coverage", "json", "-o", str(output_dir / "coverage.json")], 120),
            ("coverage-report-xml", [sys.executable, "-m", "coverage", "xml", "-o", str(output_dir / "coverage.xml")], 120),
            ("coverage-report-html", [sys.executable, "-m", "coverage", "html", "-d", str(html_dir)], 180),
            ("coverage-report-threshold", [sys.executable, "-m", "coverage", "report", f"--fail-under={threshold}"], 120),
        ]
        for command_id, command, timeout_seconds in report_commands:
            report_results.append(
                run_bounded_command(
                    root=root,
                    output_dir=output_dir / "reports",
                    command_id=command_id,
                    command=command,
                    timeout_seconds=timeout_seconds,
                    env=env,
                )
            )

    after_status = _git_tracked_status(root)
    mutations = _new_tracked_mutations(before_status, after_status)
    collection_green = all(
        item.get("green") is True
        and isinstance(item.get("collected_test_count"), int)
        and item.get("collected_test_count", 0) > 0
        for item in collection_results
    )
    shards_green = bool(shard_results) and all(item.get("green") is True for item in shard_results)
    reports_green = coverage_execution_complete and bool(report_results) and all(
        item.get("green") is True for item in report_results
    )
    threshold_green = coverage_execution_complete and next(
        (item.get("green") is True for item in report_results if item.get("command_id") == "coverage-report-threshold"),
        False,
    )
    git_available = before_status.get("available") is True and after_status.get("available") is True
    worktree_clean = (
        git_available
        and before_status.get("clean") is True
        and after_status.get("clean") is True
        and not mutations
    )
    coverage_percent = _load_coverage_percent(output_dir / "coverage.json")

    blockers: list[str] = []
    if not collection_green:
        blockers.append("coverage_collection")
    if not shards_green:
        blockers.append("coverage_test_shards")
    if not coverage_execution_complete:
        blockers.append("coverage_incomplete_shards")
    elif not reports_green:
        blockers.append("coverage_report_generation")
    if coverage_execution_complete and not threshold_green:
        blockers.append("coverage_threshold")
    if not git_available:
        blockers.append("git_worktree_observation_unavailable")
    elif not worktree_clean:
        blockers.append("tracked_worktree_mutation")

    all_results = collection_results + shard_results + report_results
    timed_out_ids = [item["command_id"] for item in all_results if item.get("timed_out") is True]
    failed_ids = [item["command_id"] for item in all_results if item.get("green") is not True]
    remaining_failure_count = sum(int(item.get("remaining_failure_count", 0)) for item in shard_results)
    completed_at = _utc_now()
    summary = {
        "prd_id": PRD_ID,
        "remediation_id": REMEDIATION_ID,
        "executed": True,
        "valid": not blockers,
        "all_green": not blockers,
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_seconds": round((completed_at - started_at).total_seconds(), 3),
        "marker_expression": MARKER_EXPRESSION,
        "coverage_threshold": threshold,
        "coverage_percent": coverage_percent,
        "collection_green": collection_green,
        "collection_counts": collection_counts,
        "shards_green": shards_green,
        "coverage_execution_complete": coverage_execution_complete,
        "reports_green": reports_green,
        "threshold_green": threshold_green,
        "git_observation_available": git_available,
        "tracked_worktree_clean": worktree_clean,
        "tracked_worktree_before": before_status,
        "tracked_worktree_after": after_status,
        "new_tracked_mutations": mutations,
        "timed_out_command_ids": timed_out_ids,
        "failed_command_ids": failed_ids,
        "remaining_test_failure_count": remaining_failure_count,
        "blockers": blockers,
        "plan": plan,
        "collection_results": collection_results,
        "unit_shard_stabilisation": unit_stabilisation,
        "unit_shard_results": unit_results,
        "integration_shard_results": integration_results,
        "report_results": report_results,
        "coverage_json_artifact": _artifact_ref(output_dir / "coverage.json", root=root),
        "coverage_xml_artifact": _artifact_ref(output_dir / "coverage.xml", root=root),
        "coverage_html_artifact": _artifact_ref(html_dir, root=root),
        "governance_boundary": {
            "execution_7_complete_claimed": False,
            "execution_8_authorised": False,
            "green_evidence_capture_performed": False,
        },
    }
    _write_json(output_dir / "summary.json", summary)
    return summary


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    path = root / CONTRACT.relative_to(ROOT)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def evaluate_coverage_baseline_stabilisation_contract(
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
    advisory_path = root / "scripts/advisory_suites/coverage_static_security_green.py"
    advisory_text = advisory_path.read_text(encoding="utf-8") if advisory_path.exists() else ""
    production_register_path = root / "docs/roadmap/production_readiness/production_readiness_register.json"
    prd11_register_path = root / "docs/roadmap/production_readiness/prd11_production_release_register.json"
    execution_record_path = root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_7_coverage_static_security_green_record.json"
    registers = []
    for path in (production_register_path, prd11_register_path, execution_record_path):
        registers.append(json.loads(path.read_text(encoding="utf-8")) if path.exists() else {})

    contract_valid = all(
        [
            contract.get("schema_version") == "prd11.0r/execution-7/coverage-baseline-stabilisation/v1",
            contract.get("prd_id") == PRD_ID,
            contract.get("remediation_id") == REMEDIATION_ID,
            contract.get("coverage_threshold") == DEFAULT_THRESHOLD,
            contract.get("marker_expression") == MARKER_EXPRESSION,
            contract.get("unit_execution") == "deterministic_parallel_shards",
            contract.get("integration_execution") == "deterministic_sequential_shards",
            contract.get("isolated_coverage_artifacts") is True,
            contract.get("tracked_worktree_clean_required") is True,
            contract.get("green_evidence_capture_allowed") is False,
            contract.get("execution_8_authorised") is False,
        ]
    )
    wiring_valid = all(
        [
            "coverage-baseline-stabilisation:" in makefile,
            "coverage-baseline-stabilisation-verify:" in makefile,
            "run_coverage_baseline_stabilisation.py" in advisory_text,
            "--require-green" in advisory_text,
            "3600" in advisory_text,
        ]
    )
    governance_valid = all(
        record.get("next_authorised_item") == PRD_ID for record in registers
    ) and registers[-1].get("evidence_recorded") is False
    green_valid = (not require_green) or summary.get("all_green") is True
    return {
        "valid": contract_valid and wiring_valid and governance_valid and green_valid,
        "contract_valid": contract_valid,
        "wiring_valid": wiring_valid,
        "governance_boundary_valid": governance_valid,
        "coverage_baseline_green": summary.get("all_green") is True,
        "summary_path": _artifact_ref(summary_path, root=root),
        "blockers": summary.get("blockers", []),
        "next_authorised_item": PRD_ID,
        "execution_8_authorised": False,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--require-green", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--unit-shards", type=int, default=DEFAULT_UNIT_SHARDS)
    parser.add_argument("--integration-shards", type=int, default=DEFAULT_INTEGRATION_SHARDS)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--collection-timeout-seconds", type=int, default=DEFAULT_COLLECTION_TIMEOUT_SECONDS)
    parser.add_argument("--unit-timeout-seconds", type=int, default=DEFAULT_UNIT_SHARD_TIMEOUT_SECONDS)
    parser.add_argument("--integration-timeout-seconds", type=int, default=DEFAULT_INTEGRATION_SHARD_TIMEOUT_SECONDS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    result = run_coverage_baseline_stabilisation(
        execute=args.execute,
        output_dir=args.output_dir,
        threshold=args.threshold,
        unit_shards=args.unit_shards,
        integration_shards=args.integration_shards,
        workers=args.workers,
        collection_timeout_seconds=args.collection_timeout_seconds,
        unit_timeout_seconds=args.unit_timeout_seconds,
        integration_timeout_seconds=args.integration_timeout_seconds,
    )
    if args.require_green and result.get("all_green") is not True:
        result["valid"] = False
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result.get("valid") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
