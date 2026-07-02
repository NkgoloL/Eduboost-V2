#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/roadmap/reconciliation/rr_003_coverage_ci_route_authority_record.json"
POLICY = ROOT / "docs/release/coverage_ci_route_policy.json"

REQUIRED_FILES = [
    "docs/roadmap/reconciliation/outstanding_work_register.md",
    "docs/roadmap/reconciliation/rr_003_coverage_ci_route_authority.md",
    "docs/roadmap/reconciliation/rr_003_coverage_ci_route_authority_record.json",
    "docs/release/coverage_ci_route_authority.md",
    "docs/release/coverage_ci_route_policy.json",
    "docs/release/dormant_router_inventory.md",
    "docs/release/route_alias_matrix.md",
    "docs/release/route_alias_exceptions.txt",
    ".github/workflows/rr003-release-authority.yml",
    "scripts/check_route_alias_matrix.py",
    "scripts/generate_route_alias_matrix.py",
]

REQUIRED_MARKERS = {
    "docs/roadmap/reconciliation/outstanding_work_register.md": [
        "RR-003",
        "Coverage / CI / route authority",
    ],
    "docs/release/coverage_ci_route_authority.md": [
        "RR-003",
        "Coverage baseline required",
        "Release-blocking checks visible in CI",
        "`/api/v2` is canonical",
        "`/v2` is compatibility-only",
        "Dormant routers must be inventoried",
    ],
    "docs/release/dormant_router_inventory.md": [
        "Dormant Router Inventory",
        "app/modules/diagnostics/bias_review_router.py",
        "app/modules/lessons/lesson_coverage_router.py",
        "app/modules/lessons/lesson_review_router.py",
        "app/modules/practice/router.py",
    ],
    ".github/workflows/rr003-release-authority.yml": [
        "RR-003 Release Authority",
        "make test-fast",
        "make route-alias-policy-check",
        "make openapi-check",
        "verify_rr003_coverage_ci_route_authority.py",
    ],
}

BOUNDARY_FALSE_FIELDS = [
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
]

COMPLETION_FIELDS = [
    "coverage_baseline_recorded",
    "coverage_threshold_decided",
    "release_checks_visible_in_ci",
    "route_alias_policy_enforced",
    "dormant_router_inventory_recorded",
    "release_docs_point_to_current_evidence",
]


def _json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        return {"__json_error__": str(exc)}


def verify() -> dict[str, Any]:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            errors.append(f"required file missing: {rel}")

    for rel, markers in REQUIRED_MARKERS.items():
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"missing marker in {rel}: {marker}")

    policy = _json(POLICY)
    if policy.get("__json_error__"):
        errors.append(f"policy JSON invalid: {policy['__json_error__']}")
    elif policy:
        if policy.get("rr_id") != "RR-003":
            errors.append("policy rr_id must be RR-003")
        if policy.get("canonical_prefix") != "/api/v2":
            errors.append("policy canonical_prefix must be /api/v2")
        if policy.get("compatibility_prefix") != "/v2":
            errors.append("policy compatibility_prefix must be /v2")
        if not policy.get("coverage_baseline_required"):
            errors.append("policy must require coverage baseline")
        if not policy.get("release_blocking_checks_visible_in_ci"):
            errors.append("policy must require visible release-blocking CI checks")
        if not policy.get("new_unapproved_route_alias_exceptions_blocked"):
            errors.append("policy must block new unapproved route alias exceptions")

    record = _json(RECORD)
    if record.get("__json_error__"):
        errors.append(f"record JSON invalid: {record['__json_error__']}")
    elif record:
        if record.get("rr_id") != "RR-003":
            errors.append("record rr_id must be RR-003")
        for field in BOUNDARY_FALSE_FIELDS:
            if record.get(field) is not False:
                errors.append(f"boundary field must remain false: {field}")
        if record.get("coverage_ci_route_authority_recorded"):
            for field in COMPLETION_FIELDS:
                if record.get(field) is not True:
                    errors.append(f"claimed completion missing field: {field}")
            baseline = record.get("coverage_baseline_percent")
            threshold = record.get("coverage_threshold_percent")
            if not isinstance(baseline, (int, float)):
                errors.append("coverage_baseline_percent must be numeric when recorded")
            if not isinstance(threshold, (int, float)):
                errors.append("coverage_threshold_percent must be numeric when recorded")
            if isinstance(baseline, (int, float)) and isinstance(threshold, (int, float)) and baseline < threshold:
                errors.append("coverage baseline is below threshold")

    return {
        "valid": not errors,
        "rr_id": "RR-003",
        "errors": errors,
        "record_path": str(RECORD.relative_to(ROOT)),
        "policy_path": str(POLICY.relative_to(ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result["valid"] else "invalid")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
