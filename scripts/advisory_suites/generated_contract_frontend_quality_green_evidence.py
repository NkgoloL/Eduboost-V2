"""Generated-contract and frontend-quality green-evidence helpers.

PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4 is the first execution slice that is
allowed to turn the generated-contract and frontend-quality blockers green. It
is intentionally fail-closed: evidence capture is not valid until the command
outputs prove that OpenAPI/route inventory are current and the frontend release
quality command succeeds in the repository environment.
"""
from __future__ import annotations

import json
import os
import shutil
from scripts._subprocess import run
from scripts.true_state_remediation.core import require_reviewed_artifact
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/roadmap/production_readiness/generated_contract_frontend_quality_green_evidence_contract.json"
PREVIOUS_CONTRACT = ROOT / "docs/roadmap/production_readiness/generated_contract_frontend_quality_green_run_contract.json"
PRODUCTION_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
DEFAULT_OUTPUT_DIR = ROOT / "var/prd11/runtime-restore/execution-4/generated-contract-frontend-green-evidence"

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4"
NEXT_AFTER_EVIDENCE = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5"
FRESHNESS_MAX_AGE_DAYS = 21
FALSE_BOUNDARIES = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "prd12_implementation_authorised",
)
REQUIRED_GATE_IDS = (
    "openapi_regenerate",
    "route_inventory_regenerate",
    "generated_contract_readonly_check",
    "frontend_release_quality",
    "frontend_build_side_effect_check",
)
REQUIRED_EVIDENCE_TYPES = (
    "independent_command_output",
    "exit_code",
    "stdout_tail",
    "stderr_tail",
    "fresh_artifact_reference",
    "blocker_record_when_not_green",
)


@dataclass(frozen=True)
class GateCommand:
    gate_id: str
    command: list[str]
    cwd: str
    output_artifact: str
    release_blocking: bool = True
    repairs_blocker: str | None = None


def _python() -> str:
    return sys.executable


def _pnpm() -> str:
    return os.environ.get("PNPM_BIN") or shutil.which("pnpm") or "pnpm"


def _git() -> str:
    return os.environ.get("GIT_BIN") or shutil.which("git") or "git"


def green_evidence_command_plan(root: Path = ROOT) -> list[dict[str, Any]]:
    py = _python()
    pnpm = _pnpm()
    git = _git()
    commands = (
        GateCommand(
            "openapi_regenerate",
            [py, "scripts/generate_openapi.py"],
            ".",
            "openapi-regenerate.json",
            True,
            "openapi_regenerate",
        ),
        GateCommand(
            "route_inventory_regenerate",
            [py, "scripts/generate_route_inventory.py"],
            ".",
            "route-inventory-regenerate.json",
            True,
            "route_inventory_regenerate",
        ),
        GateCommand(
            "generated_contract_readonly_check",
            [py, "scripts/generate_openapi.py", "--check", "&&", py, "scripts/generate_route_inventory.py", "--check"],
            ".",
            "generated-contract-readonly-check.json",
            True,
            "generated_contract_readonly_check",
        ),
        GateCommand(
            "frontend_release_quality",
            [pnpm, "run", "quality:release"],
            "app/frontend",
            "frontend-release-quality.json",
            True,
            "frontend_release_quality",
        ),
        GateCommand(
            "frontend_build_side_effect_check",
            [git, "diff", "--exit-code", "--", "app/frontend/next-env.d.ts", "app/frontend/public/sw.js"],
            ".",
            "frontend-build-side-effect-check.json",
            True,
            "frontend_release_quality",
        ),
    )
    return [asdict(command) for command in commands]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _age_days(value: Any, *, now: datetime | None = None) -> int | None:
    stamp = _parse_datetime(value)
    if stamp is None:
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return max(0, ((now or datetime.now(timezone.utc)) - stamp).days)


def _run_single(command: list[str], cwd: Path) -> dict[str, Any]:
    try:
        completed = run(command, cwd=cwd, text=True, capture_output=True)
        return {
            "command": " ".join(command),
            "exit_code": completed.returncode,
            "stdout_tail": completed.stdout[-8000:],
            "stderr_tail": completed.stderr[-8000:],
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
    except FileNotFoundError as exc:
        return {
            "command": " ".join(command),
            "exit_code": 127,
            "stdout_tail": "",
            "stderr_tail": f"Executable not found: {exc.filename}",
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }


def _run_command(command: list[str], cwd: Path) -> dict[str, Any]:
    if "&&" not in command:
        return _run_single(command, cwd)
    parts: list[list[str]] = []
    current: list[str] = []
    for token in command:
        if token == "&&":
            if current:
                parts.append(current)
                current = []
            continue
        current.append(token)
    if current:
        parts.append(current)
    stdout: list[str] = []
    stderr: list[str] = []
    exit_code = 0
    executed: list[str] = []
    for part in parts:
        result = _run_single(part, cwd)
        executed.append(result["command"])
        stdout.append(result.get("stdout_tail", ""))
        stderr.append(result.get("stderr_tail", ""))
        if result.get("exit_code") != 0:
            exit_code = int(result.get("exit_code") or 1)
            break
    return {
        "command": " && ".join(executed),
        "exit_code": exit_code,
        "stdout_tail": "\n".join(stdout)[-8000:],
        "stderr_tail": "\n".join(stderr)[-8000:],
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }


def execute_green_evidence(
    root: Path = ROOT,
    *,
    gates: Iterable[str] | None = None,
    output_dir: Path | None = None,
    continue_on_failure: bool = True,
) -> dict[str, Any]:
    wanted = set(gates or [])
    out = output_dir or DEFAULT_OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for item in green_evidence_command_plan(root):
        if wanted and item["gate_id"] not in wanted:
            continue
        result = _run_command(list(item["command"]), root / item["cwd"])
        green = result["exit_code"] == 0
        payload = {**item, **result, "green": green}
        _write_json(out / item["output_artifact"], payload)
        results.append(payload)
        if not green and not continue_on_failure:
            break
    blockers = [item["gate_id"] for item in results if item.get("release_blocking") and not item.get("green")]
    summary = {
        "prd_id": PRD_ID,
        "executed": True,
        "results": results,
        "generated_contracts_green": all(
            item.get("green") is True
            for item in results
            if item.get("gate_id") in {"openapi_regenerate", "route_inventory_regenerate", "generated_contract_readonly_check"}
        ),
        "frontend_quality_green": all(
            item.get("green") is True
            for item in results
            if item.get("gate_id") in {"frontend_release_quality", "frontend_build_side_effect_check"}
        ),
        "all_green": bool(results) and not blockers and len(results) == len(REQUIRED_GATE_IDS),
        "blockers": blockers,
        "artifact_dir": str(out.relative_to(root) if out.is_relative_to(root) else out),
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(out / "summary.json", summary)
    return summary


def load_green_evidence_summary(root: Path = ROOT, *, output_dir: Path | None = None) -> dict[str, Any]:
    path = (output_dir or DEFAULT_OUTPUT_DIR) / "summary.json"
    return _load(path)


def _gate_valid(item: dict[str, Any]) -> bool:
    return all([
        item.get("id") in REQUIRED_GATE_IDS,
        item.get("release_blocking") is True,
        item.get("evidence_source") == "independent_command_result",
        item.get("must_execute_in_repo_environment") is True,
        item.get("presence_only_evidence_allowed") is False,
        item.get("governance_substitution_allowed") is False,
        isinstance(item.get("command"), list) and len(item.get("command")) >= 2,
        isinstance(item.get("required_evidence"), list) and set(REQUIRED_EVIDENCE_TYPES).issubset(set(item.get("required_evidence"))),
        item.get("blocker_when_nonzero_exit") is True,
    ])


def _result_valid(item: dict[str, Any]) -> bool:
    return all([
        item.get("gate_id") in REQUIRED_GATE_IDS,
        isinstance(item.get("command"), str) and item.get("command"),
        isinstance(item.get("exit_code"), int),
        isinstance(item.get("output_artifact"), str) and item.get("output_artifact"),
        isinstance(item.get("captured_at"), str) and item.get("captured_at"),
        isinstance(item.get("green"), bool),
    ])


def evaluate_governance_alignment(root: Path = ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    prod = _load(root / PRODUCTION_REGISTER.relative_to(ROOT))
    prd11 = _load(root / PRD11_REGISTER.relative_to(ROOT))
    prod_next = prod.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    prd11_boundaries = prd11.get("authority_boundaries", {}) if isinstance(prd11.get("authority_boundaries"), dict) else {}
    release_boundaries_locked = all(boundaries.get(key) is False and prd11_boundaries.get(key) is False for key in FALSE_BOUNDARIES)
    ages = {
        "production_register_age_days": _age_days(prod.get("last_recorded_at"), now=now),
        "prd11_register_age_days": _age_days(prd11.get("last_recorded_at"), now=now),
        "contract_age_days": _age_days(_load(root / CONTRACT.relative_to(ROOT)).get("last_reviewed_at"), now=now),
    }
    fresh = all(age is not None and age <= FRESHNESS_MAX_AGE_DAYS for age in ages.values())
    # The Execution-4 contract is historical; the register has since progressed to Execution-7.
    allowed = {PRD_ID, NEXT_AFTER_EVIDENCE, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION", "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"}
    return {
        "valid": prod_next == prd11_next and prod_next in allowed and fresh and release_boundaries_locked,
        "state_agrees": prod_next == prd11_next and prod_next in allowed,
        "production_register_next_authorised_item": prod_next,
        "prd11_register_next_authorised_item": prd11_next,
        "release_boundaries_locked": release_boundaries_locked,
        "fresh": fresh,
        **ages,
        "freshness_max_age_days": FRESHNESS_MAX_AGE_DAYS,
    }


def evaluate_green_evidence_contract(root: Path = ROOT, *, require_green: bool = False) -> dict[str, Any]:
    contract = _load(root / CONTRACT.relative_to(ROOT))
    gates = contract.get("gates", []) if isinstance(contract.get("gates"), list) else []
    gate_ids = {item.get("id") for item in gates if isinstance(item, dict)}
    missing_gates = [gate_id for gate_id in REQUIRED_GATE_IDS if gate_id not in gate_ids]
    gates_valid = all(_gate_valid(item) for item in gates if isinstance(item, dict)) and not missing_gates
    policy = contract.get("execution_policy", {}) if isinstance(contract.get("execution_policy"), dict) else {}
    policy_valid = all([
        policy.get("regenerate_then_readonly_check_required") is True,
        policy.get("frontend_release_quality_required") is True,
        policy.get("frontend_build_side_effect_check_required") is True,
        policy.get("green_status_requires_all_release_blocking_commands_zero") is True,
        policy.get("captured_command_outputs_are_required") is True,
        policy.get("presence_only_outputs_forbidden") is True,
        policy.get("governance_records_cannot_override_failed_gate") is True,
    ])
    previous_contract = _load(root / PREVIOUS_CONTRACT.relative_to(ROOT))
    previous_valid = previous_contract.get("prd_id") == "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3"
    governance = evaluate_governance_alignment(root)
    manual_review = require_reviewed_artifact(root, "B01", PRD_ID, CONTRACT.relative_to(ROOT))
    command_plan = green_evidence_command_plan(root)
    command_plan_valid = {item["gate_id"] for item in command_plan} == set(REQUIRED_GATE_IDS)
    green_summary = load_green_evidence_summary(root)
    results = green_summary.get("results", []) if isinstance(green_summary.get("results"), list) else []
    results_valid = bool(results) and all(_result_valid(item) for item in results if isinstance(item, dict))
    all_green = green_summary.get("all_green") is True
    base_valid = all([
        contract.get("prd_id") == PRD_ID,
        contract.get("schema_version") == "prd11.0r/runtime-restore-execution-4/generated-frontend-green-evidence/v1",
        gates_valid,
        policy_valid,
        previous_valid,
        command_plan_valid,
        governance["valid"],
        manual_review["valid"],
    ])
    valid = base_valid and results_valid and all_green
    return {
        "valid": valid,
        "base_valid": base_valid,
        "prd_id": contract.get("prd_id"),
        "missing_gates": missing_gates,
        "gate_count": len(gates),
        "gates_valid": gates_valid,
        "policy_valid": policy_valid,
        "previous_execution_3_contract_valid": previous_valid,
        "command_plan_valid": command_plan_valid,
        "results_valid": results_valid,
        "all_green": all_green,
        "generated_contracts_green": green_summary.get("generated_contracts_green") is True,
        "frontend_quality_green": green_summary.get("frontend_quality_green") is True,
        "green_summary_present": bool(green_summary),
        "blockers": green_summary.get("blockers", []),
        "governance_alignment_valid": governance["valid"],
        "governance_alignment": governance,
        "manual_review": manual_review,
        "next_after_evidence": contract.get("next_after_evidence"),
        "commands": command_plan,
    }
