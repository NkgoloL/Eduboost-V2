"""PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6 product critical-flow green helpers.

Execution-6 is the point where product gates stop being contract-only.  The
helper below executes curated product critical-flow commands and records their
real exit codes.  Green evidence requires every release-blocking product flow
to produce command-backed proof, including denial/negative-path coverage where
applicable.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
from scripts._subprocess import run
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/roadmap/production_readiness/product_critical_flow_green_contract.json"
OUTPUT_DIR = ROOT / "var/prd11/runtime-restore/execution-6/product-critical-flow-green"
PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7"
REQUIRED_FLOW_IDS = (
    "auth_authorisation",
    "popia_lifecycle",
    "billing_commercial",
    "learner_journeys",
    "diagnostics_assessments",
    "audit_trail",
)
RUNTIME_PREREQUISITES = (
    "runtime_baseline_green",
    "runtime_stack_green",
    "database_lineage_green",
    "schema_contract_green",
    "redis_readiness_green",
    "ready_probe_green",
)


@dataclass(frozen=True)
class ProductFlowCommand:
    flow_id: str
    description: str
    command: list[str]
    artifact: str
    requires_live_stack: bool
    requires_positive_path: bool = True
    requires_negative_path: bool = True
    release_blocking: bool = True


# These are intentionally explicit files rather than broad markers.  The
# product marker taxonomy remains useful, but release evidence must point to
# concrete commands with stable outputs and blockers.
def _py() -> str:
    return sys.executable


def command_plan() -> list[ProductFlowCommand]:
    return [
        ProductFlowCommand(
            "auth_authorisation",
            "Auth, role, token, and object-authorisation unit/HTTP-contract proof.",
            [_py(), "-m", "pytest", "-q", "tests/unit/test_authorization_policy.py", "tests/unit/test_auth_context_claims.py", "tests/unit/test_auth_token_claims_contracts.py", "tests/unit/test_check_learner_authz_coverage.py", "--no-cov"],
            "auth-authorisation.json",
            False,
        ),
        ProductFlowCommand(
            "popia_lifecycle",
            "POPIA lifecycle HTTP/runtime response contracts and data-subject rights proof.",
            [_py(), "-m", "pytest", "-q", "tests/integration/test_popia_lifecycle_response_contract.py", "tests/integration/test_popia_lifecycle_runtime_contract.py", "tests/integration/test_popia_data_subject_rights.py", "--no-cov"],
            "popia-lifecycle.json",
            True,
        ),
        ProductFlowCommand(
            "billing_commercial",
            "Billing/commercial route, entitlement, and non-live safety proof.",
            [_py(), "-m", "pytest", "-q", "tests/unit/test_billing_router_contract.py", "tests/unit/test_billing_monetization_production_readiness.py", "tests/unit/roadmap_reconciliation/test_rr011_live_billing_provider_integration.py", "--no-cov"],
            "billing-commercial.json",
            False,
        ),
        ProductFlowCommand(
            "learner_journeys",
            "Learner/guardian progress, lesson/study-plan, and denial-path proof.",
            [_py(), "-m", "pytest", "-q", "tests/integration/test_learner_flow_contract.py", "tests/integration/test_parent_progress_authorization.py", "tests/integration/test_study_plan_authorization.py", "tests/integration/test_lesson_generation_authorization.py", "--no-cov"],
            "learner-journeys.json",
            True,
        ),
        ProductFlowCommand(
            "diagnostics_assessments",
            "Diagnostic assessment, attempt, session, IRT/schema-backed route proof.",
            [_py(), "-m", "pytest", "-q", "tests/integration/test_assessment_production_path.py", "tests/integration/test_diagnostic_session.py", "tests/integration/test_diagnostics_session_binding_routes.py", "tests/integration/test_diagnostic_items_authorization.py", "--no-cov"],
            "diagnostics-assessments.json",
            True,
        ),
        ProductFlowCommand(
            "audit_trail",
            "Audit service, event contract, and immutability proof for critical actions.",
            [_py(), "-m", "pytest", "-q", "tests/unit/test_audit_event_contracts.py", "tests/unit/test_audit_service_v2.py", "tests/integration/test_audit_immutability.py", "--no-cov"],
            "audit-trail.json",
            True,
        ),
    ]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _contract(root: Path = ROOT) -> dict[str, Any]:
    return _load(root / CONTRACT.relative_to(ROOT))


def _runtime_prerequisites_green(root: Path = ROOT) -> dict[str, Any]:
    runtime_record = _load(root / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_5_runtime_stack_db_lineage_ready_green_record.json")
    missing = [key for key in RUNTIME_PREREQUISITES if runtime_record.get(key) is not True]
    return {"green": not missing, "missing_or_false": missing, "record": runtime_record}


def evaluate_product_critical_flow_contract(root: Path = ROOT, *, require_green: bool = False, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    contract = _contract(root)
    flows = contract.get("critical_flows", []) if isinstance(contract.get("critical_flows"), list) else []
    flow_ids = {item.get("id") for item in flows if isinstance(item, dict)}
    missing = [flow_id for flow_id in REQUIRED_FLOW_IDS if flow_id not in flow_ids]
    policy = contract.get("execution_policy", {}) if isinstance(contract.get("execution_policy"), dict) else {}
    flow_records_valid = all(
        item.get("class") == "product"
        and item.get("release_blocking") is True
        and item.get("evidence_source") == "independent_command_result"
        and item.get("requires_positive_path") is True
        and item.get("requires_negative_path") is True
        and item.get("presence_only_evidence_allowed") is False
        and item.get("governance_substitution_allowed") is False
        and item.get("command_id") in REQUIRED_FLOW_IDS
        for item in flows
        if isinstance(item, dict)
    ) and not missing
    policy_valid = all([
        policy.get("runtime_baseline_must_be_green_before_product_green_claim") is True,
        policy.get("capture_independent_command_outputs") is True,
        policy.get("positive_and_negative_paths_required") is True,
        policy.get("runtime_context_required_for_db_backed_flows") is True,
        policy.get("presence_only_outputs_forbidden") is True,
        policy.get("known_failures_must_be_recorded_as_blockers") is True,
        policy.get("green_status_requires_all_flow_results_green") is True,
        policy.get("governance_records_cannot_override_failed_flow") is True,
    ])
    runtime = _runtime_prerequisites_green(root)
    summary = load_flow_summary(root, output_dir=output_dir)
    base_valid = all([
        contract.get("prd_id") == PRD_ID,
        contract.get("schema_version") == "prd11.0r/runtime-restore-execution-6/product-critical-flow-green/v1",
        contract.get("next_after_green_evidence") == NEXT,
        flow_records_valid,
        policy_valid,
        runtime["green"],
    ])
    green_valid = (not require_green) or summary.get("all_green") is True
    return {
        "valid": base_valid and green_valid,
        "base_valid": base_valid,
        "prd_id": contract.get("prd_id"),
        "missing_flow_ids": missing,
        "flow_records_valid": flow_records_valid,
        "execution_policy_valid": policy_valid,
        "runtime_prerequisites_green": runtime["green"],
        "runtime_prerequisite_blockers": runtime["missing_or_false"],
        "command_plan": [asdict(item) for item in command_plan()],
        "product_flow_results_green": summary.get("all_green") is True,
        "summary_path": str(output_dir / "summary.json"),
        "blockers": summary.get("blockers", []),
    }


def _run_one(item: ProductFlowCommand, output_dir: Path) -> dict[str, Any]:
    env = os.environ.copy()
    # These gate commands validate release-readiness in non-release mode; the
    # sandbox shell can export DEBUG=release, which breaks pydantic settings
    # loading during collection. Force the child test processes into the
    # expected non-release configuration so the gate runs deterministically.
    env["DEBUG"] = "false"
    env["APP_ENV"] = "test"
    env["ENVIRONMENT"] = "test"
    env["PYTHONPATH"] = "." + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    completed = run(item.command, cwd=ROOT, text=True, capture_output=True, env=env)
    payload = {
        "flow_id": item.flow_id,
        "description": item.description,
        "command": item.command,
        "exit_code": completed.returncode,
        "green": completed.returncode == 0,
        "requires_live_stack": item.requires_live_stack,
        "requires_positive_path": item.requires_positive_path,
        "requires_negative_path": item.requires_negative_path,
        "release_blocking": item.release_blocking,
        "stdout_tail": completed.stdout[-8000:],
        "stderr_tail": completed.stderr[-8000:],
    }
    _write_json(output_dir / item.artifact, payload)
    return payload


def run_product_flow_green(*, execute: bool, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = command_plan()
    if not execute:
        payload = {"executed": False, "valid": True, "command_plan": [asdict(item) for item in plan]}
        _write_json(output_dir / "summary.json", payload)
        return payload
    results = [_run_one(item, output_dir) for item in plan]
    blockers = [item["flow_id"] for item in results if item.get("green") is not True]
    payload = {
        "executed": True,
        "all_green": not blockers,
        "valid": not blockers,
        "blockers": blockers,
        "results": results,
        "command_plan": [asdict(item) for item in plan],
    }
    _write_json(output_dir / "summary.json", payload)
    return payload


def load_flow_summary(root: Path = ROOT, *, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    return _load(output_dir / "summary.json")
