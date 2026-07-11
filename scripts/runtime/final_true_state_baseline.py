"""Final true-state baseline proof and controlled-handoff helpers.

PRD-11.0R.RUNTIME-RESTORE-6 consolidates the runtime, product, coverage,
frontend, advisory/static, dependency, generated-contract, and secret-baseline
contracts into one fail-closed release preflight decision.  It is intentionally
not a production-release authorisation.  It only authorises handoff back to
PRD-11.0-11.4 when every hard gate is independently green.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.advisory_suites.advisory_gate import evaluate_advisory_quality_gate_contract
from scripts.coverage_suites.coverage_contract import evaluate_coverage_contract
from scripts.production_readiness.collect_prd1100r_true_state_runtime_baseline import collect_baseline
from scripts.test_suites.product_gate_execution import evaluate_product_gate_execution_contract
from scripts.test_suites.product_runtime_gate import evaluate_product_runtime_gate_contract

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/roadmap/production_readiness/final_true_state_baseline_handoff_contract.json"
PRODUCTION_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-6"
NEXT_IF_GREEN = "PRD-11.0-11.4"
NEXT_IF_RED = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION"
FRESHNESS_MAX_AGE_DAYS = 21
REQUIRED_GATE_IDS = (
    "runtime_baseline",
    "disposable_stack_schema_lineage",
    "product_runtime_gates",
    "product_critical_flows",
    "coverage_execution",
    "frontend_quality",
    "advisory_static_quality",
    "generated_contract_drift",
    "dependency_security_audit",
    "secret_baseline_review",
)
REQUIRED_EVIDENCE_TYPES = (
    "independent_command_output",
    "positive_path_result",
    "negative_or_failure_path_result",
    "fresh_artifact_reference",
    "blocker_record_when_not_green",
)
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


@dataclass(frozen=True)
class FinalGateCommand:
    gate_id: str
    command: str
    evidence_artifact: str
    release_blocking: bool
    requires_live_stack: bool
    negative_path_command: str


FINAL_GATE_COMMANDS: tuple[FinalGateCommand, ...] = (
    FinalGateCommand(
        "runtime_baseline",
        "PYTHONPATH=. python3 scripts/production_readiness/collect_prd1100r_true_state_runtime_baseline.py --run-expensive-checks --json",
        "true-state-runtime-baseline.json",
        True,
        True,
        "PYTHONPATH=. python3 scripts/runtime/verify_runtime_stack_readiness.py --json",
    ),
    FinalGateCommand(
        "disposable_stack_schema_lineage",
        "PYTHONPATH=. python3 scripts/runtime/verify_disposable_stack_schema_lineage.py --require-live --json",
        "disposable-stack-schema-lineage.json",
        True,
        True,
        "PYTHONPATH=. python3 scripts/runtime/verify_disposable_stack_schema_lineage.py --json",
    ),
    FinalGateCommand(
        "product_runtime_gates",
        "PYTHONPATH=. python3 scripts/test_suites/run_product_runtime_gates.py combined --json",
        "product-runtime-gates.json",
        True,
        True,
        "PYTHONPATH=. python3 scripts/test_suites/verify_product_runtime_test_gates.py --json",
    ),
    FinalGateCommand(
        "product_critical_flows",
        "PYTHONPATH=. python3 scripts/test_suites/run_product_gate_execution.py combined --json",
        "product-critical-flows.json",
        True,
        True,
        "PYTHONPATH=. python3 scripts/test_suites/verify_product_gate_execution.py --json",
    ),
    FinalGateCommand(
        "coverage_execution",
        "make test-coverage COVERAGE_THRESHOLD=70",
        "coverage-execution.json",
        True,
        False,
        "PYTHONPATH=. python3 scripts/coverage_suites/verify_coverage_contract.py --json",
    ),
    FinalGateCommand(
        "frontend_quality",
        "cd app/frontend && pnpm lint && pnpm test:run && pnpm build",
        "frontend-quality.json",
        True,
        False,
        "cd app/frontend && pnpm lint --max-warnings=0",
    ),
    FinalGateCommand(
        "advisory_static_quality",
        "python3 -m ruff check app tests && python3 -m mypy app && python3 -m bandit -r app scripts -q",
        "advisory-static-quality.json",
        True,
        False,
        "python3 -m ruff check app tests --select F,E9",
    ),
    FinalGateCommand(
        "generated_contract_drift",
        "python3 scripts/generate_openapi.py --check && python3 scripts/generate_route_inventory.py --check",
        "generated-contract-drift.json",
        True,
        False,
        "python3 scripts/generate_openapi.py --check",
    ),
    FinalGateCommand(
        "dependency_security_audit",
        "pip-audit -r requirements/base.txt -r requirements/dev.txt && cd app/frontend && pnpm audit --prod",
        "dependency-security-audit.json",
        True,
        False,
        "pip-audit -r requirements/base.txt --strict",
    ),
    FinalGateCommand(
        "secret_baseline_review",
        "detect-secrets scan --baseline .secrets.baseline app scripts .github && detect-secrets audit .secrets.baseline",
        "secret-baseline-review.json",
        True,
        False,
        "detect-secrets audit .secrets.baseline",
    ),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


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


def gate_command_plan() -> list[dict[str, Any]]:
    return [asdict(command) for command in FINAL_GATE_COMMANDS]


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    return _load(root / CONTRACT.relative_to(ROOT))


def _gate_valid(item: dict[str, Any]) -> bool:
    return all([
        item.get("id") in REQUIRED_GATE_IDS,
        item.get("release_blocking") is True,
        item.get("evidence_source") == "independent_command_result",
        item.get("requires_positive_path") is True,
        item.get("requires_negative_or_failure_path") is True,
        item.get("presence_only_evidence_allowed") is False,
        item.get("governance_substitution_allowed") is False,
        item.get("controls_handoff_to_prd1100_1104") is True,
        isinstance(item.get("command"), str) and bool(item.get("command")),
        isinstance(item.get("negative_or_failure_command"), str) and bool(item.get("negative_or_failure_command")),
        isinstance(item.get("required_evidence"), list) and set(REQUIRED_EVIDENCE_TYPES).issubset(set(item.get("required_evidence"))),
    ])


def evaluate_governance_alignment(root: Path = ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    prod = _load(root / PRODUCTION_REGISTER.relative_to(ROOT))
    prd11 = _load(root / PRD11_REGISTER.relative_to(ROOT))
    prod_next = prod.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    release_boundaries_locked = all(boundaries.get(key) is False for key in FALSE_BOUNDARIES[:-1])
    ages = {
        "production_register_age_days": _age_days(prod.get("last_recorded_at"), now=now),
        "prd11_register_age_days": _age_days(prd11.get("last_recorded_at"), now=now),
        "final_handoff_contract_age_days": _age_days(load_contract(root).get("last_reviewed_at"), now=now),
    }
    fresh = all(age is not None and age <= FRESHNESS_MAX_AGE_DAYS for age in ages.values())
    allowed = {PRD_ID, NEXT_IF_RED, NEXT_IF_GREEN}
    return {
        "valid": prod_next == prd11_next and prod_next in allowed and fresh and release_boundaries_locked,
        "state_agrees": prod_next == prd11_next and prod_next in allowed,
        "production_register_next_authorised_item": prod_next,
        "prd11_register_next_authorised_item": prd11_next,
        "fresh": fresh,
        "freshness_max_age_days": FRESHNESS_MAX_AGE_DAYS,
        "release_boundaries_locked": release_boundaries_locked,
        **ages,
    }


def evaluate_final_true_state_handoff_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_contract(root)
    gates = contract.get("gates", []) if isinstance(contract.get("gates"), list) else []
    gate_ids = {item.get("id") for item in gates if isinstance(item, dict)}
    missing_gates = [gate_id for gate_id in REQUIRED_GATE_IDS if gate_id not in gate_ids]
    policy = contract.get("handoff_policy", {}) if isinstance(contract.get("handoff_policy"), dict) else {}
    gates_valid = all(_gate_valid(item) for item in gates if isinstance(item, dict)) and not missing_gates
    policy_valid = all([
        policy.get("all_release_blocking_gates_must_be_green") is True,
        policy.get("runtime_baseline_green_required") is True,
        policy.get("product_gate_green_required") is True,
        policy.get("coverage_gate_green_required") is True,
        policy.get("frontend_quality_green_required") is True,
        policy.get("advisory_static_gate_green_required") is True,
        policy.get("dependency_security_gate_green_required") is True,
        policy.get("generated_contracts_green_required") is True,
        policy.get("secret_baseline_gate_green_required") is True,
        policy.get("presence_only_evidence_allowed") is False,
        policy.get("governance_substitution_allowed") is False,
        policy.get("green_handoff_target") == NEXT_IF_GREEN,
        policy.get("red_handoff_target") == NEXT_IF_RED,
    ])
    governance = evaluate_governance_alignment(root)
    valid = all([
        contract.get("prd_id") == PRD_ID,
        contract.get("schema_version") == "prd11.0r/runtime-restore-6/final-true-state-baseline-handoff/v1",
        gates_valid,
        policy_valid,
        governance.get("valid") is True,
        contract.get("next_if_green") == NEXT_IF_GREEN,
        contract.get("next_if_red") == NEXT_IF_RED,
    ])
    return {
        "valid": valid,
        "prd_id": contract.get("prd_id"),
        "schema_version": contract.get("schema_version"),
        "required_gate_ids": list(REQUIRED_GATE_IDS),
        "gate_ids": sorted(str(item) for item in gate_ids if item),
        "missing_gates": missing_gates,
        "gates_valid": gates_valid,
        "policy_valid": policy_valid,
        "governance_alignment": governance,
        "commands": gate_command_plan(),
        "next_if_green": contract.get("next_if_green"),
        "next_if_red": contract.get("next_if_red"),
    }


def _read_green_state(root: Path) -> dict[str, bool]:
    prod = _load(root / PRODUCTION_REGISTER.relative_to(ROOT))
    return {
        "runtime_baseline_green": prod.get("runtime_baseline_green") is True,
        "product_runtime_gate_green": prod.get("product_runtime_gate_green") is True,
        "product_gate_green": prod.get("product_gate_green") is True,
        "coverage_gate_green": prod.get("coverage_gate_green") is True,
        "frontend_quality_green": prod.get("frontend_quality_green") is True,
        "advisory_static_gate_green": prod.get("advisory_static_gate_green") is True,
        "dependency_audit_gate_green": prod.get("dependency_audit_gate_green") is True,
        "generated_contracts_green": prod.get("generated_contracts_green") is True,
        "secret_baseline_gate_green": prod.get("secret_baseline_gate_green") is True,
    }


def collect_final_true_state_baseline(root: Path = ROOT, *, run_expensive_checks: bool = False) -> dict[str, Any]:
    contract = evaluate_final_true_state_handoff_contract(root)
    runtime_baseline = collect_baseline(root, run_expensive_checks=run_expensive_checks)
    coverage_contract = evaluate_coverage_contract(root)
    product_runtime_contract = evaluate_product_runtime_gate_contract(root)
    product_gate_contract = evaluate_product_gate_execution_contract(root)
    advisory_contract = evaluate_advisory_quality_gate_contract(root)
    green_state = _read_green_state(root)
    green_state["runtime_baseline_green"] = bool(runtime_baseline.get("runtime_baseline_green"))
    all_release_gates_green = all(green_state.values())
    next_item = NEXT_IF_GREEN if all_release_gates_green else NEXT_IF_RED
    blockers = list(runtime_baseline.get("blockers", []))
    blockers.extend(name for name, is_green in green_state.items() if not is_green and name not in blockers)
    return {
        "prd_id": PRD_ID,
        "contract_valid": contract.get("valid") is True,
        "runtime_baseline": runtime_baseline,
        "coverage_contract_valid": coverage_contract.get("valid") is True,
        "product_runtime_contract_valid": product_runtime_contract.get("valid") is True,
        "product_gate_contract_valid": product_gate_contract.get("valid") is True,
        "advisory_contract_valid": advisory_contract.get("valid") is True,
        "green_state": green_state,
        "all_release_gates_green": all_release_gates_green,
        "controlled_handoff_to_prd1100_1104_authorised": all_release_gates_green,
        "controlled_beta_activation_operational_hold": not all_release_gates_green,
        "live_learner_traffic_operationally_safe": all_release_gates_green,
        "production_release_evidence_blocked_until_runtime_baseline_green": not all_release_gates_green,
        "next_authorised_item": next_item,
        "blockers": sorted(set(str(item) for item in blockers)),
        "release_evidence_mode": "independent_command_outputs_required_for_green_handoff",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--run-expensive-checks", action="store_true")
    args = parser.parse_args()
    result = collect_final_true_state_baseline(ROOT, run_expensive_checks=args.run_expensive_checks)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result["contract_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
