#!/usr/bin/env python3
"""Audit KG-0 formal roadmap approval authority files."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

REQUIRED_DOCS = [
    "docs/adr/ADR-036-knowledge-graph-learning-state-core.md",
    "docs/architecture/knowledge_graph_learning_state_architecture.md",
    "docs/architecture/knowledge_graph_data_model.md",
    "docs/architecture/knowledge_graph_transition_plan.md",
    "docs/product/knowledge_graph_learning_model_brief.md",
    "docs/caps/knowledge_graph_mapping_contract.md",
    "docs/ai/knowledge_graph_grounding_contract.md",
    "docs/security/knowledge_graph_privacy_and_popia_contract.md",
    "docs/testing/knowledge_graph_verification_plan.md",
    "docs/roadmap/knowledge_graph_pivot_roadmap.md",
    "docs/roadmap/risk_register_knowledge_graph_pivot.md",
    "docs/roadmap/knowledge_graph/kg_implementation_roadmap.md",
    "docs/roadmap/knowledge_graph/kg_roadmap_register.json",
    "docs/roadmap/knowledge_graph/kg_formalization_package_manifest.json",
    "docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval.md",
]
INDEX_EXPECTATIONS = {
    "README.md": ["Knowledge Graph Roadmap", "ADR-030", "kg_implementation_roadmap.md"],
    "docs/README.md": ["Knowledge graph learning-state roadmap", "knowledge_graph_learning_state_architecture.md", "kg_implementation_roadmap.md"],
    "docs/architecture/README.md": ["Knowledge Graph Learning-State Architecture", "knowledge_graph_data_model.md"],
    "docs/adr/README.md": ["ADR-036", "Knowledge Graph Learning-State Core"],
    "docs/roadmap/README.md": ["KG-0", "kg_implementation_roadmap.md"],
}
KG_IDS = [f"KG-{i}" for i in range(0, 9)]
BOUNDARY_FALSE_KEYS = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "database_schema_migration_authorised",
    "learner_facing_model_change_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]

def read_text(root: Path, rel: str) -> str:
    path = root / rel
    return path.read_text(encoding="utf-8") if path.exists() else ""

def read_json(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []
    missing_docs = [rel for rel in REQUIRED_DOCS if not (root / rel).exists()]
    if missing_docs:
        errors.append("missing KG-0 docs: " + ", ".join(missing_docs))
    index_checks: dict[str, bool] = {}
    for rel, needles in INDEX_EXPECTATIONS.items():
        text = read_text(root, rel)
        ok = bool(text) and all(needle in text for needle in needles)
        index_checks[rel] = ok
        if not ok:
            errors.append(f"{rel} is missing KG-0 index references")
    register = read_json(root, "docs/roadmap/knowledge_graph/kg_roadmap_register.json")
    sequence = register.get("kg_sequence", [])
    kg_ids = [item.get("kg_id") for item in sequence]
    if kg_ids != KG_IDS:
        errors.append(f"kg_roadmap_register kg_sequence must be {KG_IDS}; got {kg_ids}")
    boundary = register.get("boundary", {})
    for key in BOUNDARY_FALSE_KEYS:
        if boundary.get(key) is not False:
            errors.append(f"KG roadmap register boundary must remain false: {key}")
    final_closure = read_json(root, "docs/roadmap/reconciliation/final_roadmap_reconciliation_closure_record.json")
    final_closure_valid = final_closure.get("final_roadmap_reconciliation_closure_recorded") is True and final_closure.get("all_reconciled_rr_items_addressed_through_rr018") is True
    if not final_closure_valid:
        errors.append("final roadmap reconciliation closure must be valid before KG-0")
    adr_text = read_text(root, "docs/adr/ADR-036-knowledge-graph-learning-state-core.md")
    roadmap_text = read_text(root, "docs/roadmap/knowledge_graph/kg_implementation_roadmap.md")
    package_manifest = read_json(root, "docs/roadmap/knowledge_graph/kg_formalization_package_manifest.json")
    authority_checks = {
        "required_docs_present": not missing_docs,
        "indexes_reference_kg0": all(index_checks.values()),
        "kg_sequence_kg0_to_kg8": kg_ids == KG_IDS,
        "kg_register_boundaries_false": all(boundary.get(key) is False for key in BOUNDARY_FALSE_KEYS),
        "final_rr_closure_valid": final_closure_valid,
        "adr_030_present": "Knowledge Graph" in adr_text and "ADR" in adr_text,
        "kg_implementation_roadmap_present": "KG-0" in roadmap_text and "KG-8" in roadmap_text,
        "kg_formalization_package_manifest_present": bool(package_manifest.get("files")),
    }
    for key, ok in authority_checks.items():
        if not ok and not any(key in e for e in errors):
            errors.append(f"authority check failed: {key}")
    return {"authority_valid": all(authority_checks.values()) and not errors, "errors": errors, "warnings": warnings, "authority_checks": authority_checks, "index_checks": index_checks, "kg_ids": kg_ids, "final_roadmap_reconciliation_closure_valid": final_closure_valid}

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("authority_valid=" + str(result["authority_valid"]).lower())
    raise SystemExit(0 if result["authority_valid"] else 1)
if __name__ == "__main__":
    main()
