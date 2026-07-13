"""Verify Execution-7 budgeted terminal-isolation authority and wiring."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.coverage_suites.budgeted_terminal_isolation import (
    DEFAULT_MAX_BISECTION_DEPTH,
    DEFAULT_MAX_GENERATED_LEAVES,
    DEFAULT_OUTER_GATE_TIMEOUT_SECONDS,
    DEFAULT_OVERALL_BUDGET_SECONDS,
    DEFAULT_PACKAGING_RESERVE_SECONDS,
    PRD_ID,
    REMEDIATION_ID,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/roadmap/production_readiness/budgeted_terminal_isolation_contract.json"


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def verify(root: Path = ROOT) -> dict[str, Any]:
    contract = _load(root / CONTRACT.relative_to(ROOT))
    unit = (root / "scripts/coverage_suites/unit_shard_stabilisation.py").read_text(
        encoding="utf-8"
    )
    baseline = (
        root / "scripts/coverage_suites/coverage_baseline_stabilisation.py"
    ).read_text(encoding="utf-8")
    advisory = (
        root / "scripts/advisory_suites/coverage_static_security_green.py"
    ).read_text(encoding="utf-8")
    makefile = (root / "Makefile").read_text(encoding="utf-8")
    registers = [
        _load(root / relative)
        for relative in (
            "docs/roadmap/production_readiness/production_readiness_register.json",
            "docs/roadmap/production_readiness/prd11_production_release_register.json",
            "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_7_coverage_static_security_green_record.json",
        )
    ]
    contract_valid = all(
        [
            contract.get("schema_version")
            == "prd11.0r/execution-7/budgeted-terminal-isolation/v1",
            contract.get("prd_id") == PRD_ID,
            contract.get("remediation_id") == REMEDIATION_ID,
            contract.get("inner_budget_seconds") == DEFAULT_OVERALL_BUDGET_SECONDS,
            contract.get("outer_gate_timeout_seconds")
            == DEFAULT_OUTER_GATE_TIMEOUT_SECONDS,
            contract.get("packaging_reserve_seconds")
            == DEFAULT_PACKAGING_RESERVE_SECONDS,
            contract.get("maximum_bisection_depth")
            == DEFAULT_MAX_BISECTION_DEPTH,
            contract.get("maximum_generated_leaves")
            == DEFAULT_MAX_GENERATED_LEAVES,
            contract.get("progressive_file_isolation") is True,
            contract.get("suspect_only_node_probing") is True,
            contract.get("atomic_checkpoint_after_each_attempt") is True,
            contract.get("resume_attempt_fingerprints") is True,
            contract.get("partial_diagnostic_package_required") is True,
            contract.get("coverage_threshold") == 70,
            contract.get("coverage_threshold_unchanged") is True,
            contract.get("green_evidence_capture_allowed") is False,
            contract.get("execution_7_complete_claim_allowed") is False,
            contract.get("execution_8_authorised") is False,
        ]
    )
    wiring_valid = all(
        [
            "ProgressJournal" in unit,
            "suspect_only_probing" in unit,
            "pending_due_to_budget" in unit,
            "package_terminal_artifacts" in unit,
            "--overall-budget-seconds" in baseline,
            "--packaging-reserve-seconds" in baseline,
            "--resume" in baseline,
            '"3900"' in advisory,
            "4200" in advisory,
            "budgeted-terminal-isolation-verify:" in makefile,
        ]
    )
    governance_valid = (
        all(record.get("next_authorised_item") == PRD_ID for record in registers)
        and registers[-1].get("evidence_recorded") is False
    )
    return {
        "valid": contract_valid and wiring_valid and governance_valid,
        "contract_valid": contract_valid,
        "wiring_valid": wiring_valid,
        "governance_boundary_valid": governance_valid,
        "next_authorised_item": PRD_ID,
        "execution_7_complete_claimed": False,
        "execution_8_authorised": False,
        "green_evidence_capture_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
