"""PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7 advisory green helpers.

Execution-7 is the point where coverage, backend static quality,
dependency security, and secret-baseline review stop being contract-only.
The helper executes release-blocking commands and records real exit codes.
Green evidence requires every gate to be backed by independent command
output, with blocker records when anything fails.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/roadmap/production_readiness/coverage_static_security_green_contract.json"
OUTPUT_DIR = ROOT / "var/prd11/runtime-restore/execution-7/coverage-static-security-green"
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8"
REQUIRED_GATE_IDS = (
    "coverage_execution",
    "ruff_release_static_quality",
    "mypy_release_static_quality",
    "bandit_release_security",
    "python_dependency_security_audit",
    "frontend_dependency_security_audit",
    "secret_baseline_review",
)
PREVIOUS_GREEN_FIELDS = (
    "runtime_baseline_green",
    "runtime_stack_green",
    "database_lineage_green",
    "schema_contract_green",
    "redis_readiness_green",
    "ready_probe_green",
    "generated_contracts_green",
    "frontend_quality_green",
    "product_gate_green",
    "product_runtime_gate_green",
    "critical_product_flows_green",
)


@dataclass(frozen=True)
class CoverageStaticSecurityCommand:
    gate_id: str
    description: str
    command: list[str]
    artifact: str
    timeout_seconds: int
    release_blocking: bool = True
    requires_positive_path: bool = True
    requires_negative_or_failure_path: bool = True


def _py() -> str:
    return sys.executable


def command_plan() -> list[CoverageStaticSecurityCommand]:
    return [
        CoverageStaticSecurityCommand(
            "coverage_execution",
            "Fresh documentation-defined coverage report with failure exit state preserved.",
            ["make", "test-coverage", "COVERAGE_THRESHOLD=70", f"PYTHON={_py()}"],
            "coverage-execution.json",
            900,
        ),
        CoverageStaticSecurityCommand(
            "ruff_release_static_quality",
            "Release-blocking Ruff quality check over app and tests.",
            [_py(), "-m", "ruff", "check", "app", "tests"],
            "ruff-release-static-quality.json",
            300,
        ),
        CoverageStaticSecurityCommand(
            "mypy_release_static_quality",
            "Release-blocking mypy type-check over app.",
            [_py(), "-m", "mypy", "app"],
            "mypy-release-static-quality.json",
            600,
        ),
        CoverageStaticSecurityCommand(
            "bandit_release_security",
            "Bandit security scan over application and script code.",
            [_py(), "-m", "bandit", "-r", "app", "scripts", "-q"],
            "bandit-release-security.json",
            600,
        ),
        CoverageStaticSecurityCommand(
            "python_dependency_security_audit",
            "Python dependency audit over base and development requirements.",
            [_py(), "-m", "pip_audit", "-r", "requirements/base.txt", "-r", "requirements/dev.txt"],
            "python-dependency-security-audit.json",
            600,
        ),
        CoverageStaticSecurityCommand(
            "frontend_dependency_security_audit",
            "Frontend production dependency audit.",
            ["bash", "-lc", "cd app/frontend && pnpm audit --prod"],
            "frontend-dependency-security-audit.json",
            300,
        ),
        CoverageStaticSecurityCommand(
            "secret_baseline_review",
            "Secret-baseline drift/reviewability scan over release-relevant source paths.",
            ["bash", "-lc", "detect-secrets scan --baseline .secrets.baseline app scripts .github"],
            "secret-baseline-review.json",
            300,
        ),
    ]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _artifact_ref(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def load_summary(root: Path = ROOT, *, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    return _load(root / output_dir.relative_to(ROOT) / "summary.json")


def _previous_green(root: Path = ROOT) -> dict[str, Any]:
    record = _load(root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_6_product_critical_flow_green_record.json")
    missing = [field for field in PREVIOUS_GREEN_FIELDS if record.get(field) is not True]
    return {"green": not missing, "missing_or_false": missing, "record": record}


def evaluate_coverage_static_security_contract(root: Path = ROOT, *, require_green: bool = False, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    contract = _load(root / CONTRACT.relative_to(ROOT))
    gates = contract.get("gates", []) if isinstance(contract.get("gates"), list) else []
    gate_ids = {item.get("id") for item in gates if isinstance(item, dict)}
    missing = [gate_id for gate_id in REQUIRED_GATE_IDS if gate_id not in gate_ids]
    policy = contract.get("execution_policy", {}) if isinstance(contract.get("execution_policy"), dict) else {}
    gates_valid = all(
        isinstance(item, dict)
        and item.get("id") in REQUIRED_GATE_IDS
        and item.get("class") == "advisory"
        and item.get("release_blocking") is True
        and item.get("evidence_source") == "independent_command_result"
        and item.get("requires_positive_path") is True
        and item.get("requires_negative_or_failure_path") is True
        and item.get("presence_only_evidence_allowed") is False
        and item.get("governance_substitution_allowed") is False
        and isinstance(item.get("command_id"), str)
        and item.get("command_id") in REQUIRED_GATE_IDS
        and isinstance(item.get("expected_artifacts"), list)
        and len(item.get("expected_artifacts")) >= 1
        for item in gates
    ) and not missing
    policy_valid = all([
        policy.get("fresh_coverage_report_required") is True,
        policy.get("coverage_failure_exit_state_preserved") is True,
        policy.get("ruff_mypy_bandit_required") is True,
        policy.get("dependency_audits_must_resolve") is True,
        policy.get("secret_baseline_must_be_reviewable") is True,
        policy.get("green_status_requires_all_gate_results_green") is True,
        policy.get("presence_only_outputs_forbidden") is True,
        policy.get("governance_records_cannot_override_failed_gate") is True,
    ])
    previous = _previous_green(root)
    summary = load_summary(root, output_dir=output_dir)
    base_valid = all([
        contract.get("prd_id") == PRD_ID,
        contract.get("schema_version") == "prd11.0r/runtime-restore-execution-7/coverage-static-security-green/v1",
        contract.get("next_after_green_evidence") == NEXT,
        gates_valid,
        policy_valid,
        previous["green"],
    ])
    green_valid = (not require_green) or summary.get("all_green") is True
    return {
        "valid": base_valid and green_valid,
        "base_valid": base_valid,
        "prd_id": contract.get("prd_id"),
        "missing_gate_ids": missing,
        "gates_valid": gates_valid,
        "execution_policy_valid": policy_valid,
        "previous_green": previous["green"],
        "previous_green_blockers": previous["missing_or_false"],
        "command_plan": [asdict(item) for item in command_plan()],
        "coverage_static_security_results_green": summary.get("all_green") is True,
        "summary_path": str(output_dir / "summary.json"),
        "blockers": summary.get("blockers", []),
    }


def _first_int(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return int(match.group(1)) if match else None


def _remaining_violation_count(gate_id: str, stdout: str, stderr: str, exit_code: int | None) -> int:
    if exit_code == 0:
        return 0
    text = f"{stdout}\n{stderr}"
    if gate_id == "ruff_release_static_quality":
        return _first_int(r"Found (\d+) errors?", text) or len(re.findall(r"^[^:\n]+:\d+:\d+: [A-Z]\d+", text, re.MULTILINE))
    if gate_id == "mypy_release_static_quality":
        return _first_int(r"Found (\d+) errors?", text) or len(re.findall(r": error:", text))
    if gate_id == "bandit_release_security":
        counts = [
            _first_int(r"Low:\s+(\d+)", text) or 0,
            _first_int(r"Medium:\s+(\d+)", text) or 0,
            _first_int(r"High:\s+(\d+)", text) or 0,
        ]
        issue_count = sum(counts)
        return issue_count or len(re.findall(r">> Issue:", text))
    if gate_id == "python_dependency_security_audit":
        return _first_int(r"Found (\d+) known vulnerabilit", text) or len(re.findall(r"\b(PYSEC|GHSA)-", text))
    if gate_id == "frontend_dependency_security_audit":
        return _first_int(r"(\d+) vulnerabilities found", text) or len(re.findall(r"More info\s+\|", text))
    if gate_id == "secret_baseline_review":
        return len(re.findall(r"Secret Type:", text)) or (1 if "command not found" in text else 0)
    if gate_id == "coverage_execution":
        counts = [
            _first_int(r"(\d+) failed", text) or 0,
            _first_int(r"(\d+) errors?", text) or 0,
        ]
        return sum(counts) or len(re.findall(r"^(FAILED|ERROR) ", text, re.MULTILINE))
    return 1


def _failure_classification(gate_id: str, stdout: str, stderr: str, exit_code: int | None, *, timed_out: bool) -> str:
    if timed_out:
        return "timeout"
    if exit_code == 0:
        return "green"
    text = f"{stdout}\n{stderr}".lower()
    if "command not found" in text or "no module named" in text:
        return "missing_tool"
    if "resolutionimpossible" in text or "cannot install" in text:
        return "dependency_resolution_conflict"
    if "vulnerabilities found" in text or "known vulnerabilities" in text:
        return "dependency_vulnerabilities"
    if gate_id == "coverage_execution":
        return "test_or_coverage_failures"
    if gate_id in {"ruff_release_static_quality", "mypy_release_static_quality"}:
        return "static_quality_violations"
    if gate_id in {"bandit_release_security", "secret_baseline_review"}:
        return "security_review_findings"
    return "command_failed"


def _run_one(item: CoverageStaticSecurityCommand, output_dir: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "." + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env.setdefault("APP_ENV", "test")
    env.setdefault("ENVIRONMENT", "test")
    env.setdefault("DEBUG", "false")
    started_at = datetime.now(timezone.utc)
    monotonic_started = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(
            item.command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            env=env,
            timeout=item.timeout_seconds,
        )
        exit_code: int | None = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = None
        stdout = _text(exc.stdout)
        stderr = _text(exc.stderr) + f"\nCommand timed out after {item.timeout_seconds} seconds.\n"
    completed_at = datetime.now(timezone.utc)
    duration_seconds = round(time.monotonic() - monotonic_started, 3)
    stdout_artifact = output_dir / item.artifact.replace(".json", ".stdout.txt")
    stderr_artifact = output_dir / item.artifact.replace(".json", ".stderr.txt")
    _write_text(stdout_artifact, stdout)
    _write_text(stderr_artifact, stderr)
    classification = _failure_classification(item.gate_id, stdout, stderr, exit_code, timed_out=timed_out)
    remaining_count = _remaining_violation_count(item.gate_id, stdout, stderr, exit_code)
    payload = {
        "gate_id": item.gate_id,
        "description": item.description,
        "command": item.command,
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_seconds": duration_seconds,
        "timeout_seconds": item.timeout_seconds,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "green": exit_code == 0,
        "failure_classification": classification,
        "remaining_violation_count": remaining_count,
        "release_blocking": item.release_blocking,
        "requires_positive_path": item.requires_positive_path,
        "requires_negative_or_failure_path": item.requires_negative_or_failure_path,
        "stdout_artifact": _artifact_ref(stdout_artifact),
        "stderr_artifact": _artifact_ref(stderr_artifact),
        "stdout_tail": stdout[-12000:],
        "stderr_tail": stderr[-12000:],
        "captured_at": completed_at.isoformat(),
    }
    _write(output_dir / item.artifact, payload)
    return payload


def run_coverage_static_security_green(
    *,
    execute: bool,
    output_dir: Path = OUTPUT_DIR,
    gate_ids: set[str] | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    full_plan = command_plan()
    plan = [item for item in full_plan if gate_ids is None or item.gate_id in gate_ids]
    if not execute:
        payload = {
            "executed": False,
            "valid": True,
            "partial": gate_ids is not None,
            "selected_gate_ids": [item.gate_id for item in plan],
            "command_plan": [asdict(item) for item in plan],
        }
        _write(output_dir / "summary.json", payload)
        return payload
    results = [_run_one(item, output_dir) for item in plan]
    blockers = [item["gate_id"] for item in results if not item["green"] and item.get("release_blocking")]
    remaining = {item["gate_id"]: item["remaining_violation_count"] for item in results}
    payload = {
        "executed": True,
        "partial": gate_ids is not None,
        "selected_gate_ids": [item.gate_id for item in plan],
        "all_green": not blockers,
        "blockers": blockers,
        "remaining_violation_counts": remaining,
        "total_remaining_violations": sum(remaining.values()),
        "results": results,
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    _write(output_dir / "summary.json", payload)
    return payload


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--require-green", action="store_true")
    parser.add_argument("--gate-id", action="append", choices=REQUIRED_GATE_IDS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = run_coverage_static_security_green(
        execute=args.execute,
        gate_ids=set(args.gate_id) if args.gate_id else None,
    )
    if args.require_green and payload.get("all_green") is not True:
        payload["valid"] = False
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
        return 1
    payload.setdefault("valid", True if not args.execute else payload.get("all_green") is True)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
    return 0 if payload.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
