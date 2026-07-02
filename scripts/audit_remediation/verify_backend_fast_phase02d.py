#!/usr/bin/env python3
"""Verify Technical Audit Phase 02D backend-fast remediation assets."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def verify() -> dict[str, object]:
    checks: list[Check] = []

    readiness = _read("app/services/content_staging_readiness.py")
    checks.append(Check(
        "staging_all_scopes_defaults_to_active_scopes",
        "include_review_scopes: bool = False" in readiness
        and "self.scope_registry.list_active_scopes()" in readiness
        and "self.scope_registry.list_scopes()" in readiness,
        "verify_all_scopes defaults to active scopes and has explicit review-scope opt-in",
    ))

    seed_script = _read("scripts/curriculum/seed_staging_review_scopes.py")
    checks.append(Check(
        "seed_script_defaults_to_active_scopes",
        "--include-all-review-scopes" in seed_script
        and "registry.list_active_scopes()" in seed_script
        and "include_all_review_scopes" in seed_script,
        "review-scope seeding requires explicit opt-in when no scope_id is supplied",
    ))

    req_paths = ["requirements/base.in", "requirements/base.txt", "requirements/dev.in", "requirements/dev.txt", "requirements.txt", "requirements-dev.txt"]
    missing_req = [path for path in req_paths if "mcp[cli]" not in _read(path)]
    checks.append(Check(
        "mcp_dependency_declared",
        not missing_req,
        "mcp[cli] declared in backend runtime/dev dependency inputs and locks" if not missing_req else f"missing from {missing_req}",
    ))

    runtime_dep = _read("scripts/audit_remediation/verify_backend_fast_runtime_dependencies.py")
    sync_dep = _read("scripts/audit_remediation/sync_backend_fast_runtime_dependencies.sh")
    checks.append(Check(
        "mcp_dependency_is_required_for_backend_fast_authority",
        '"mcp": "mcp[cli]"' in runtime_dep and "mcp[cli]>=1.0.0" in sync_dep,
        "runtime dependency verifier and sync script include MCP",
    ))

    workflow = _read(".github/workflows/auth-refresh-db-proof.yml")
    checks.append(Check(
        "auth_refresh_db_uses_upload_artifact_v4",
        "actions/upload-artifact@v4" in workflow and "auth-refresh-db-proof" in workflow,
        "auth refresh DB proof workflow uploads evidence with actions/upload-artifact@v4",
    ))

    contract = _read("scripts/ci/content_factory_schema_contract.py")
    required_enum_values = {"revision_required", "published", "superseded"}
    enum_present = all(f'"{value}"' in contract for value in required_enum_values)
    model_present = all(
        name in contract
        for name in ["ContentAnswerKeyVerification", "ContentReviewDecision", "ContentStateTransitionEvent"]
    )
    table_present = all(
        table in contract
        for table in ["content_answer_key_verifications", "content_review_decisions", "content_state_transition_events"]
    )
    checks.append(Check(
        "content_factory_schema_contract_declares_existing_models_and_enums",
        enum_present and model_present and table_present,
        "schema contract includes existing ORM state tables and extended artifact statuses",
    ))

    blocker = json.loads(_read("docs/roadmap/execution/technical_audit_remediation/blocker_register.json"))
    checks.append(Check(
        "blocker_register_marks_phase02d_active",
        blocker.get("active_slice") == "02d-backend-fast-staging-contracts",
        "blocker register points to Phase 02D slice",
    ))

    valid = all(check.passed for check in checks)
    return {
        "valid": valid,
        "phase": "TA-02D",
        "slice": "backend-fast-staging-contracts",
        "checks": [asdict(check) for check in checks],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("TA Phase 02D verification:", "valid" if result["valid"] else "invalid")
        for check in result["checks"]:
            print(f"- {check['name']}: {'pass' if check['passed'] else 'fail'}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
