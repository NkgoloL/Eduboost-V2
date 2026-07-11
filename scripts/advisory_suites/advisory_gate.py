"""Coverage, frontend-quality, and advisory/static gate contract helpers.

PRD-11.0R.RUNTIME-RESTORE-5 does not claim these gates are green. It records
which commands and evidence artifacts are release-blocking, and requires later
execution evidence from independent command outputs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/roadmap/production_readiness/coverage_frontend_advisory_gate_contract.json"
COVERAGE_CONTRACT = ROOT / "docs/roadmap/production_readiness/coverage_contract.json"
PRODUCT_GATE_CONTRACT = ROOT / "docs/roadmap/production_readiness/product_gate_execution_contract.json"
PRODUCT_RUNTIME_CONTRACT = ROOT / "docs/roadmap/production_readiness/product_runtime_test_gate_contract.json"
TEST_TAXONOMY = ROOT / "docs/roadmap/production_readiness/test_suite_taxonomy.json"
SCRIPT_TAXONOMY = ROOT / "docs/roadmap/production_readiness/script_taxonomy.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-5"
NEXT_AFTER_EVIDENCE = "PRD-11.0R.RUNTIME-RESTORE-6"
FRESHNESS_MAX_AGE_DAYS = 21
REQUIRED_GATE_IDS = (
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
ALLOWED_NEXT = (PRD_ID, NEXT_AFTER_EVIDENCE)


@dataclass(frozen=True)
class AdvisoryGateCommand:
    gate_id: str
    command: str
    evidence_artifact: str
    release_blocking: bool
    requires_live_stack: bool = False
    negative_path_command: str | None = None


DEFAULT_GATE_COMMANDS: tuple[AdvisoryGateCommand, ...] = (
    AdvisoryGateCommand(
        "coverage_execution",
        "make test-coverage COVERAGE_THRESHOLD=70",
        "coverage-execution.json",
        True,
        False,
        "python3 scripts/coverage_suites/verify_coverage_contract.py --json",
    ),
    AdvisoryGateCommand(
        "frontend_quality",
        "cd app/frontend && pnpm lint && pnpm test:run && pnpm build",
        "frontend-quality.json",
        True,
        False,
        "cd app/frontend && pnpm lint --max-warnings=0",
    ),
    AdvisoryGateCommand(
        "advisory_static_quality",
        "python3 -m ruff check app tests && python3 -m mypy app && python3 -m bandit -r app scripts -q",
        "advisory-static-quality.json",
        True,
        False,
        "python3 -m ruff check app tests --select F,E9",
    ),
    AdvisoryGateCommand(
        "generated_contract_drift",
        "python3 scripts/generate_openapi.py --check && python3 scripts/generate_route_inventory.py --check",
        "generated-contract-drift.json",
        True,
        False,
        "python3 scripts/generate_openapi.py --check",
    ),
    AdvisoryGateCommand(
        "dependency_security_audit",
        "pip-audit -r requirements/base.txt -r requirements/dev.txt && cd app/frontend && pnpm audit --prod",
        "dependency-security-audit.json",
        True,
        False,
        "pip-audit -r requirements/base.txt --strict",
    ),
    AdvisoryGateCommand(
        "secret_baseline_review",
        "detect-secrets scan --baseline .secrets.baseline app scripts .github",
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
    return [asdict(command) for command in DEFAULT_GATE_COMMANDS]


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    return _load(root / CONTRACT.relative_to(ROOT))


def _freshness(root: Path, *, now: datetime | None = None) -> dict[str, Any]:
    files = {
        "production_register_age_days": (root / PROD_REGISTER.relative_to(ROOT), "last_recorded_at"),
        "prd11_register_age_days": (root / PRD11_REGISTER.relative_to(ROOT), "last_recorded_at"),
        "test_taxonomy_age_days": (root / TEST_TAXONOMY.relative_to(ROOT), "last_reviewed_at"),
        "script_taxonomy_age_days": (root / SCRIPT_TAXONOMY.relative_to(ROOT), "last_reviewed_at"),
        "coverage_contract_age_days": (root / COVERAGE_CONTRACT.relative_to(ROOT), "last_reviewed_at"),
        "product_runtime_contract_age_days": (root / PRODUCT_RUNTIME_CONTRACT.relative_to(ROOT), "last_reviewed_at"),
        "product_gate_contract_age_days": (root / PRODUCT_GATE_CONTRACT.relative_to(ROOT), "last_reviewed_at"),
        "coverage_frontend_advisory_contract_age_days": (root / CONTRACT.relative_to(ROOT), "last_reviewed_at"),
    }
    ages: dict[str, Any] = {}
    for key, (path, field) in files.items():
        ages[key] = _age_days(_load(path).get(field), now=now)
    ages["fresh"] = all(age is not None and age <= FRESHNESS_MAX_AGE_DAYS for age in ages.values())
    ages["freshness_max_age_days"] = FRESHNESS_MAX_AGE_DAYS
    return ages


def evaluate_governance_alignment(root: Path = ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    prod = _load(root / PROD_REGISTER.relative_to(ROOT))
    prd11 = _load(root / PRD11_REGISTER.relative_to(ROOT))
    prod_next = prod.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    boundaries_locked = all(boundaries.get(key) is False for key in (
        "production_release_authorised",
        "deployment_authorised",
        "release_tag_authorised",
        "public_beta_authorised",
        "public_beta_live_traffic_authorised",
        "billing_launch_authorised",
        "live_payment_processing_authorised",
    ))
    freshness = _freshness(root, now=now)
    state_agrees = prod_next == prd11_next and prod_next in ALLOWED_NEXT
    return {
        "valid": state_agrees and boundaries_locked and freshness["fresh"],
        "state_agrees": state_agrees,
        "production_register_next_authorised_item": prod_next,
        "prd11_register_next_authorised_item": prd11_next,
        "release_boundaries_locked": boundaries_locked,
        **freshness,
    }


def _gate_valid(item: dict[str, Any]) -> bool:
    return all([
        item.get("id") in REQUIRED_GATE_IDS,
        item.get("class") in {"product", "runtime", "advisory"},
        item.get("release_blocking") is True,
        item.get("evidence_source") == "independent_command_result",
        item.get("requires_positive_path") is True,
        item.get("requires_negative_or_failure_path") is True,
        item.get("presence_only_evidence_allowed") is False,
        item.get("governance_substitution_allowed") is False,
        isinstance(item.get("command"), str) and bool(item.get("command")),
        isinstance(item.get("negative_or_failure_command"), str) and bool(item.get("negative_or_failure_command")),
        isinstance(item.get("required_evidence"), list) and set(REQUIRED_EVIDENCE_TYPES).issubset(set(item.get("required_evidence"))),
        isinstance(item.get("known_failure_modes"), list) and len(item.get("known_failure_modes")) >= 1,
    ])


def _execution_result_valid(item: dict[str, Any]) -> bool:
    required = (
        "gate_id",
        "command",
        "exit_code",
        "output_artifact",
        "captured_at",
        "commit_or_stack_context",
    )
    return all(key in item for key in required)


def evaluate_advisory_quality_gate_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_contract(root)
    gates = contract.get("gates", []) if isinstance(contract.get("gates"), list) else []
    gate_ids = {item.get("id") for item in gates if isinstance(item, dict)}
    missing_gates = [gate_id for gate_id in REQUIRED_GATE_IDS if gate_id not in gate_ids]
    gates_valid = all(_gate_valid(item) for item in gates if isinstance(item, dict)) and not missing_gates
    policy = contract.get("execution_policy", {}) if isinstance(contract.get("execution_policy"), dict) else {}
    policy_valid = all([
        policy.get("fresh_coverage_report_required") is True,
        policy.get("frontend_lint_vitest_build_required") is True,
        policy.get("advisory_static_gates_required") is True,
        policy.get("generated_contract_drift_must_be_clean") is True,
        policy.get("dependency_audit_must_resolve_and_report") is True,
        policy.get("secret_baseline_must_be_reviewable") is True,
        policy.get("presence_only_outputs_forbidden") is True,
        policy.get("governance_records_cannot_override_failed_gate") is True,
        policy.get("green_status_requires_all_gate_results_green") is True,
    ])
    execution_results = contract.get("execution_results", []) if isinstance(contract.get("execution_results"), list) else []
    recorded_results_valid = all(_execution_result_valid(item) for item in execution_results if isinstance(item, dict))
    governance_alignment = evaluate_governance_alignment(root)
    valid = all([
        contract.get("prd_id") == PRD_ID,
        contract.get("schema_version") == "prd11.0r/runtime-restore-5/coverage-frontend-advisory/v1",
        gates_valid,
        policy_valid,
        recorded_results_valid,
        contract.get("coverage_gate_green") is False,
        contract.get("frontend_quality_green") is False,
        contract.get("advisory_static_gate_green") is False,
        contract.get("next_after_evidence") == NEXT_AFTER_EVIDENCE,
        governance_alignment["valid"],
    ])
    return {
        "valid": valid,
        "prd_id": contract.get("prd_id"),
        "missing_gates": missing_gates,
        "gate_count": len(gates),
        "gates_valid": gates_valid,
        "policy_valid": policy_valid,
        "execution_results_valid": recorded_results_valid,
        "coverage_gate_green": contract.get("coverage_gate_green") is True,
        "frontend_quality_green": contract.get("frontend_quality_green") is True,
        "advisory_static_gate_green": contract.get("advisory_static_gate_green") is True,
        "governance_alignment_valid": governance_alignment["valid"],
        "governance_alignment": governance_alignment,
        "next_after_evidence": contract.get("next_after_evidence"),
        "commands": gate_command_plan(),
    }
