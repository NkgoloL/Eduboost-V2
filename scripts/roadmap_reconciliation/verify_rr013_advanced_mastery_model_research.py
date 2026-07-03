#!/usr/bin/env python3
"""Verify RR-013 advanced mastery-model research authority and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.mastery_research.audit_rr013_advanced_mastery_model_research import audit

RR_ID = "RR-013"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RR012_RECORD = Path("docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_013_advanced_mastery_model_research_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_013_advanced_mastery_model_research.md")
WORKFLOW = Path(".github/workflows/rr013-advanced-mastery-model-research.yml")
AUDIT_SCRIPT = Path("scripts/mastery_research/audit_rr013_advanced_mastery_model_research.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr013_advanced_mastery_model_research_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr013_advanced_mastery_model_research.py")
MAKEFILE = Path("Makefile")

BOUNDARY_FALSE_KEYS = (
    "model_deployment_authorised",
    "learner_facing_model_change_authorised",
    "production_learner_data_retraining_authorised",
    "runtime_kg_implementation_claimed",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
)

REQUIRED_TRUE_KEYS = (
    "advanced_mastery_model_research_recorded",
    "rr012_production_telemetry_dashboard_valid",
    "research_only_boundary_recorded",
    "existing_mastery_model_preserved",
    "literature_review_recorded",
    "model_candidates_compared",
    "evaluation_protocol_recorded",
    "data_readiness_ethics_reviewed",
    "caps_alignment_evaluation_required",
    "human_review_required_before_deployment",
    "no_learner_pii_exported_for_research",
    "runtime_kg_north_star_boundary_preserved",
    "research_decision_memo_recorded",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr014_public_beta_expansion_remaining_visible",
    "rr015_external_approvals_remaining_visible",
    "rr016_operational_drills_remaining_visible",
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
    checks: dict[str, bool] = {}

    required_paths = {
        "register": REGISTER,
        "rr012_record": RR012_RECORD,
        "record": RECORD,
        "rr_doc": RR_DOC,
        "workflow": WORKFLOW,
        "audit_script": AUDIT_SCRIPT,
        "capture_script": CAPTURE_SCRIPT,
        "verify_script": VERIFY_SCRIPT,
    }
    for name, path in required_paths.items():
        exists = (root / path).exists()
        checks[f"{name}_exists"] = exists
        if not exists:
            errors.append(f"missing required RR-013 file: {path}")

    register = _read(root, REGISTER)
    checks["register_mentions_rr013"] = "RR-013" in register and "Advanced mastery-model research" in register
    if not checks["register_mentions_rr013"]:
        errors.append("outstanding work register must mention RR-013 advanced mastery-model research")

    rr012 = _json(root, RR012_RECORD)
    checks["rr012_record_valid"] = rr012.get("production_telemetry_dashboard_recorded") is True
    if not checks["rr012_record_valid"]:
        errors.append("RR-012 production telemetry dashboard must be recorded before RR-013")

    makefile = _read(root, MAKEFILE)
    for target in ("rr013-advanced-mastery-model-research-audit", "rr013-advanced-mastery-model-research-check"):
        ok = target in makefile
        checks[f"makefile_target:{target}"] = ok
        if not ok:
            errors.append(f"Makefile missing target: {target}")

    workflow = _read(root, WORKFLOW)
    checks["workflow_mentions_rr013"] = "RR-013 Advanced Mastery Model Research" in workflow
    if not checks["workflow_mentions_rr013"]:
        errors.append("RR-013 workflow must identify the RR-013 check")

    audit_result = audit(root, require_final=False)
    checks["authority_audit_valid"] = audit_result.get("authority_valid") is True
    if not checks["authority_audit_valid"]:
        errors.extend(audit_result.get("errors", []))

    record = _json(root, RECORD)
    if record.get("__json_error__"):
        errors.append(f"RR-013 record JSON invalid: {record['__json_error__']}")
        record = {}
    checks["record_rr_id"] = record.get("rr_id") == RR_ID
    if record and record.get("rr_id") != RR_ID:
        errors.append("RR-013 record must carry rr_id=RR-013")

    for key in BOUNDARY_FALSE_KEYS:
        value = record.get(key)
        checks[f"boundary_false:{key}"] = value is False
        if record and value is not False:
            errors.append(f"RR-013 boundary key must remain false: {key}")

    for key in REQUIRED_TRUE_KEYS:
        checks[f"record_true:{key}"] = record.get(key) is True
        if record and record.get("advanced_mastery_model_research_recorded") is True and record.get(key) is not True:
            errors.append(f"RR-013 recorded evidence missing true flag: {key}")

    if record and record.get("advanced_mastery_model_research_recorded") is not True:
        warnings.append("record is still pending evidence capture")

    final_audit = None
    if record.get("advanced_mastery_model_research_recorded") is True:
        final_audit = audit(root, require_final=True)
        checks["final_audit_valid"] = final_audit.get("valid") is True
        if not final_audit.get("valid"):
            errors.extend(final_audit.get("errors", []))
        embedded = record.get("advanced_mastery_model_research_audit", {})
        checks["record_embeds_valid_audit"] = isinstance(embedded, dict) and embedded.get("valid") is True
        if not checks["record_embeds_valid_audit"]:
            errors.append("RR-013 record must embed a valid advanced mastery-model research audit")

    authority_valid = not errors or (record and record.get("advanced_mastery_model_research_recorded") is not True and not [e for e in errors if "recorded evidence missing" not in e])
    # Recompute authority_valid from structural requirements only: before capture, missing final true flags should be warnings.
    structural_errors = []
    if errors:
        for e in errors:
            if "recorded evidence missing true flag" in e:
                continue
            structural_errors.append(e)
    authority_valid = len(structural_errors) == 0
    valid = authority_valid and record.get("advanced_mastery_model_research_recorded") is True and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "advanced_mastery_model_research_recorded": record.get("advanced_mastery_model_research_recorded") is True,
        "rr012_production_telemetry_dashboard_valid": record.get("rr012_production_telemetry_dashboard_valid") is True,
        "research_only_boundary_recorded": record.get("research_only_boundary_recorded") is True,
        "existing_mastery_model_preserved": record.get("existing_mastery_model_preserved") is True,
        "literature_review_recorded": record.get("literature_review_recorded") is True,
        "model_candidates_compared": record.get("model_candidates_compared") is True,
        "evaluation_protocol_recorded": record.get("evaluation_protocol_recorded") is True,
        "data_readiness_ethics_reviewed": record.get("data_readiness_ethics_reviewed") is True,
        "caps_alignment_evaluation_required": record.get("caps_alignment_evaluation_required") is True,
        "human_review_required_before_deployment": record.get("human_review_required_before_deployment") is True,
        "no_learner_pii_exported_for_research": record.get("no_learner_pii_exported_for_research") is True,
        "runtime_kg_north_star_boundary_preserved": record.get("runtime_kg_north_star_boundary_preserved") is True,
        "research_decision_memo_recorded": record.get("research_decision_memo_recorded") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr014_public_beta_expansion_remaining_visible": record.get("rr014_public_beta_expansion_remaining_visible") is True,
        "rr015_external_approvals_remaining_visible": record.get("rr015_external_approvals_remaining_visible") is True,
        "rr016_operational_drills_remaining_visible": record.get("rr016_operational_drills_remaining_visible") is True,
        "model_deployment_authorised": record.get("model_deployment_authorised"),
        "learner_facing_model_change_authorised": record.get("learner_facing_model_change_authorised"),
        "production_learner_data_retraining_authorised": record.get("production_learner_data_retraining_authorised"),
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed"),
        "production_release_authorised": record.get("production_release_authorised"),
        "deployment_authorised": record.get("deployment_authorised"),
        "release_tag_authorised": record.get("release_tag_authorised"),
        "public_beta_authorised": record.get("public_beta_authorised"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    if args.authority_only:
        result = dict(result)
        result["valid"] = result["authority_valid"]
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
