#!/usr/bin/env python3
"""Verify KG-0 formal KG roadmap approval authority and captured evidence."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
from scripts.knowledge_graph.audit_kg000_formal_kg_roadmap_approval import audit
RECORD = Path("docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval_record.json")
BOUNDARY_FALSE_KEYS = ["runtime_kg_implementation_claimed","runtime_kg_authority_switch_authorised","database_schema_migration_authorised","learner_facing_model_change_authorised","production_release_authorised","deployment_authorised","release_tag_authorised","public_beta_authorised","billing_launch_authorised","live_payment_processing_authorised"]
REQUIRED_CAPTURE_TRUE = ["formal_kg_roadmap_approval_recorded","final_roadmap_reconciliation_closure_valid","adr_030_recorded","kg_roadmap_register_recorded","kg_implementation_roadmap_recorded","kg_formalization_package_manifest_recorded","kg_0_to_kg_8_sequence_recorded","runtime_kg_boundary_recorded","kg_next_work_rule_recorded"]

def read_json(path: Path) -> dict[str, Any]:
    if not path.exists(): return {}
    return json.loads(path.read_text(encoding="utf-8"))

def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    audit_result = audit(root)
    record = read_json(root / RECORD)
    errors = list(audit_result.get("errors", []))
    warnings = list(audit_result.get("warnings", []))
    if not record:
        errors.append(f"missing KG-0 record: {RECORD}")
    elif record.get("kg_id") != "KG-0":
        errors.append("KG-0 record must have kg_id KG-0")
    captured = record.get("formal_kg_roadmap_approval_recorded") is True
    if captured:
        for key in REQUIRED_CAPTURE_TRUE:
            if record.get(key) is not True:
                errors.append(f"KG-0 captured record flag must be true: {key}")
    else:
        warnings.append("KG-0 record is still pending evidence capture")
    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"KG-0 boundary flag must remain false: {key}")
    authority_valid = audit_result.get("authority_valid") is True and bool(record) and record.get("kg_id") == "KG-0" and all(record.get(key) is False for key in BOUNDARY_FALSE_KEYS)
    valid = authority_valid and captured and not errors
    return {"valid": valid, "authority_valid": authority_valid, "kg_id": "KG-0", "record_path": str(RECORD), "errors": errors, "warnings": warnings, "formal_kg_roadmap_approval_recorded": captured, "final_roadmap_reconciliation_closure_valid": record.get("final_roadmap_reconciliation_closure_valid") is True, "adr_030_recorded": record.get("adr_030_recorded") is True, "kg_roadmap_register_recorded": record.get("kg_roadmap_register_recorded") is True, "kg_implementation_roadmap_recorded": record.get("kg_implementation_roadmap_recorded") is True, "kg_0_to_kg_8_sequence_recorded": record.get("kg_0_to_kg_8_sequence_recorded") is True, "runtime_kg_boundary_recorded": record.get("runtime_kg_boundary_recorded") is True, "kg_next_work_rule_recorded": record.get("kg_next_work_rule_recorded") is True, "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed") is True, "runtime_kg_authority_switch_authorised": record.get("runtime_kg_authority_switch_authorised") is True, "database_schema_migration_authorised": record.get("database_schema_migration_authorised") is True, "learner_facing_model_change_authorised": record.get("learner_facing_model_change_authorised") is True, "production_release_authorised": record.get("production_release_authorised") is True, "deployment_authorised": record.get("deployment_authorised") is True, "release_tag_authorised": record.get("release_tag_authorised") is True, "public_beta_authorised": record.get("public_beta_authorised") is True, "billing_launch_authorised": record.get("billing_launch_authorised") is True, "live_payment_processing_authorised": record.get("live_payment_processing_authorised") is True, "audit": audit_result}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(Path("."))
    if args.json: print(json.dumps(result, indent=2, sort_keys=True))
    else: print("valid=" + str(result["valid"]).lower())
    ok = result["authority_valid"] if args.authority_only else result["valid"]
    raise SystemExit(0 if ok else 1)
if __name__ == "__main__": main()
