#!/usr/bin/env python3
"""Audit RR-008 operational readiness anchors."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_DOCS = {
    "operational_readiness_policy": Path("docs/operations/readiness/rr008_operational_readiness_policy.md"),
    "incident_response_runbook_index": Path("docs/operations/readiness/rr008_incident_response_runbook_index.md"),
    "slo_definitions": Path("docs/operations/readiness/rr008_slo_definitions.md"),
    "capacity_planning": Path("docs/operations/readiness/rr008_capacity_planning.md"),
    "llm_cost_model": Path("docs/operations/readiness/rr008_llm_cost_model.md"),
    "grafana_alert_linkage": Path("docs/operations/readiness/rr008_grafana_alert_linkage.md"),
    "operational_readiness_manifest": Path("docs/operations/readiness/rr008_operational_readiness_manifest.json"),
}

REFERENCE_DOCS = {
    "existing_observability_doc": Path("docs/operations/observability.md"),
    "existing_incident_response_doc": Path("docs/incident_response.md"),
    "existing_breach_response_doc": Path("docs/operations/breach_response.md"),
    "existing_security_incident_runbook": Path("docs/operations/runbooks/security_incident.md"),
}

WORKFLOW = Path(".github/workflows/rr008-operational-readiness.yml")

REQUIRED_MARKERS = {
    "incident_response_runbook_index": "Incident response runbook index recorded: true",
    "slo_definitions": "SLO definitions recorded: true",
    "capacity_planning": "Capacity planning recorded: true",
    "llm_cost_model": "LLM cost model recorded: true",
    "grafana_alert_linkage": "Grafana alert linkage recorded: true",
}

REQUIRED_MANIFEST_FLAGS = (
    "incident_response_runbook_recorded",
    "slo_definitions_recorded",
    "capacity_planning_recorded",
    "llm_cost_model_recorded",
    "grafana_alert_linkage_recorded",
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


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []
    doc_results: dict[str, bool] = {}

    for key, rel in REQUIRED_DOCS.items():
        exists = (root / rel).exists()
        doc_results[f"{key}_exists"] = exists
        if not exists:
            errors.append(f"missing required RR-008 document: {rel}")

    for key, marker in REQUIRED_MARKERS.items():
        rel = REQUIRED_DOCS[key]
        contains = marker in _read(root, rel)
        doc_results[f"{key}_marker_present"] = contains
        if not contains:
            errors.append(f"missing marker in {rel}: {marker}")

    reference_results: dict[str, bool] = {}
    for key, rel in REFERENCE_DOCS.items():
        exists = (root / rel).exists()
        reference_results[f"{key}_exists"] = exists
        if not exists:
            warnings.append(f"reference operations document not found: {rel}")

    manifest = _json(root, REQUIRED_DOCS["operational_readiness_manifest"])
    if manifest.get("__json_error__"):
        errors.append(f"RR-008 manifest JSON invalid: {manifest['__json_error__']}")
    elif not manifest:
        errors.append("RR-008 operational readiness manifest is missing")
    else:
        if manifest.get("rr_id") != "RR-008":
            errors.append("RR-008 manifest rr_id must be RR-008")
        for flag in REQUIRED_MANIFEST_FLAGS:
            if manifest.get(flag) is not True:
                errors.append(f"RR-008 manifest flag must be true: {flag}")
        for flag in (
            "production_release_authorised",
            "deployment_authorised",
            "release_tag_authorised",
            "public_beta_authorised",
            "runtime_kg_implementation_claimed",
        ):
            if manifest.get(flag) is not False:
                errors.append(f"RR-008 manifest boundary flag must be false: {flag}")

    workflow_text = _read(root, WORKFLOW)
    workflow_checks = {
        "rr008_workflow_exists": (root / WORKFLOW).exists(),
        "rr008_workflow_runs_verifier": "verify_rr008_operational_readiness.py" in workflow_text,
        "rr008_workflow_mentions_operational_readiness": "operational readiness" in workflow_text.lower(),
    }
    for key, passed in workflow_checks.items():
        if not passed:
            errors.append(f"workflow check failed: {key}")

    policy = _read(root, REQUIRED_DOCS["operational_readiness_policy"])
    if "RR-003" not in policy or "0.0" not in policy:
        errors.append("RR-008 policy must carry the RR-003 fallback coverage caveat")
    if "RR-006" not in policy or "non-required" not in policy:
        errors.append("RR-008 policy must carry the RR-006 non-required checks caveat")
    if "Runtime KG" not in policy or "not authorised" not in policy:
        errors.append("RR-008 policy must preserve runtime KG boundary")
    if "RR-016" not in policy or "drill" not in policy.lower():
        errors.append("RR-008 policy must distinguish readiness from RR-016 operational drills")

    valid = not errors
    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "documents": doc_results,
        "reference_documents": reference_results,
        "workflow_checks": workflow_checks,
        "manifest": manifest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("RR-008 operational readiness audit:", "valid" if result["valid"] else "invalid")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
