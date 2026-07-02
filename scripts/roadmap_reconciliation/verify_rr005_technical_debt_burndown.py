#!/usr/bin/env python3
"""Verify RR-005 technical debt burn-down authority and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-005"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RR004_RECORD = Path("docs/roadmap/reconciliation/rr_004_workspace_hygiene_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_005_technical_debt_burndown_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_005_technical_debt_burndown.md")
POLICY = Path("docs/engineering/technical_debt/rr005_technical_debt_burndown_policy.md")
RUFF_DOC = Path("docs/engineering/technical_debt/rr005_ruff_debt_inventory.md")
IMPORT_DOC = Path("docs/engineering/technical_debt/rr005_import_linter_exception_register.md")
ROUTE_DOC = Path("docs/engineering/technical_debt/rr005_stale_route_comment_audit.md")
MIGRATION_DOC = Path("docs/engineering/technical_debt/rr005_migration_history_audit.md")
ROUTER_DOC = Path("docs/engineering/technical_debt/rr005_dormant_router_review.md")
AUDIT_SCRIPT = Path("scripts/technical_debt/audit_rr005_technical_debt.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr005_technical_debt_burndown_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr005_technical_debt_burndown.py")
MAKEFILE = Path("Makefile")

BOUNDARY_FALSE_KEYS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)
REQUIRED_TRUE_KEYS = (
    "technical_debt_burndown_recorded",
    "ruff_debt_captured",
    "import_linter_exceptions_registered",
    "stale_route_comments_audited",
    "migration_history_audited",
    "dormant_router_review_recorded",
    "debt_burndown_backlog_recorded",
)


def _read(root: Path, path: Path) -> str:
    full = root / path
    return full.read_text(encoding="utf-8") if full.exists() else ""


def _json(root: Path, path: Path) -> dict[str, Any]:
    full = root / path
    if not full.exists():
        return {}
    try:
        return json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"__json_error__": str(exc)}


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    register = _read(root, REGISTER)
    rr004_record = _json(root, RR004_RECORD)
    record = _json(root, RECORD)
    rr_doc = _read(root, RR_DOC)
    policy = _read(root, POLICY)
    ruff_doc = _read(root, RUFF_DOC)
    import_doc = _read(root, IMPORT_DOC)
    route_doc = _read(root, ROUTE_DOC)
    migration_doc = _read(root, MIGRATION_DOC)
    router_doc = _read(root, ROUTER_DOC)
    audit_script = _read(root, AUDIT_SCRIPT)
    makefile = _read(root, MAKEFILE)

    checks = {
        "rr005_in_outstanding_register": RR_ID in register and "Technical debt burn-down" in register,
        "rr004_predecessor_recorded": rr004_record.get("workspace_hygiene_recorded") is True,
        "rr_doc_exists": (root / RR_DOC).exists(),
        "record_exists": (root / RECORD).exists(),
        "policy_exists": (root / POLICY).exists(),
        "ruff_inventory_doc_exists": (root / RUFF_DOC).exists(),
        "import_linter_exception_doc_exists": (root / IMPORT_DOC).exists(),
        "stale_route_comment_doc_exists": (root / ROUTE_DOC).exists(),
        "migration_history_doc_exists": (root / MIGRATION_DOC).exists(),
        "dormant_router_doc_exists": (root / ROUTER_DOC).exists(),
        "audit_script_exists": (root / AUDIT_SCRIPT).exists(),
        "capture_script_exists": (root / CAPTURE_SCRIPT).exists(),
        "verify_script_exists": (root / VERIFY_SCRIPT).exists(),
        "rr_doc_cites_register_id": RR_ID in rr_doc,
        "policy_mentions_no_runtime_kg": "Runtime KG" in policy and "not authorised" in policy,
        "policy_mentions_rr003_caveat": "RR-003" in policy and "0.0" in policy,
        "ruff_doc_mentions_ruff_check": "ruff check app tests scripts" in ruff_doc,
        "import_doc_mentions_ignore_imports": "ignore_imports" in import_doc,
        "route_doc_mentions_router_comments": "stale route comments" in route_doc.lower(),
        "migration_doc_has_squash_decision": "squash decision" in migration_doc.lower(),
        "dormant_router_doc_mentions_call_site_proof": "call-site proof" in router_doc,
        "audit_script_collects_all_five_areas": all(
            token in audit_script
            for token in (
                "collect_ruff_debt",
                "collect_import_linter_exceptions",
                "collect_stale_route_comments",
                "collect_migration_history",
                "collect_dormant_router_review",
            )
        ),
        "makefile_has_rr005_audit_target": "rr005-technical-debt-audit" in makefile,
        "makefile_has_rr005_check_target": "rr005-technical-debt-check" in makefile,
    }

    for key, passed in checks.items():
        if not passed:
            errors.append(f"missing or failed check: {key}")

    if record.get("__json_error__"):
        errors.append(f"record JSON invalid: {record['__json_error__']}")
    elif record:
        if record.get("rr_id") != RR_ID:
            errors.append(f"record rr_id must be {RR_ID}")
        for key in BOUNDARY_FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"boundary flag must remain false: {key}")
        if record.get("technical_debt_burndown_recorded") is True:
            for key in REQUIRED_TRUE_KEYS:
                if record.get(key) is not True:
                    errors.append(f"record flag must be true after evidence capture: {key}")
            if not isinstance(record.get("technical_debt_audit"), dict):
                errors.append("technical_debt_audit must be embedded after capture")
            if record.get("rr003_fallback_coverage_caveat_visible") is not True:
                errors.append("RR-003 fallback coverage caveat must remain visible")
        else:
            warnings.append("record is still pending evidence capture")
    else:
        errors.append("record JSON is missing")

    authority_errors = [
        err for err in errors
        if not err.startswith("record flag must be true")
        and err != "technical_debt_audit must be embedded after capture"
        and err != "RR-003 fallback coverage caveat must remain visible"
    ]
    authority_valid = not authority_errors
    valid = not errors and record.get("technical_debt_burndown_recorded") is True

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "technical_debt_burndown_recorded": record.get("technical_debt_burndown_recorded") is True,
        "ruff_debt_captured": record.get("ruff_debt_captured") is True,
        "import_linter_exceptions_registered": record.get("import_linter_exceptions_registered") is True,
        "stale_route_comments_audited": record.get("stale_route_comments_audited") is True,
        "migration_history_audited": record.get("migration_history_audited") is True,
        "dormant_router_review_recorded": record.get("dormant_router_review_recorded") is True,
        "debt_burndown_backlog_recorded": record.get("debt_burndown_backlog_recorded") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        **{key: record.get(key) is True for key in BOUNDARY_FALSE_KEYS},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    parser.add_argument("--authority-only", action="store_true")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("RR-005 technical debt burn-down verification")
        print(f"valid: {result['valid']}")
        print(f"authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
