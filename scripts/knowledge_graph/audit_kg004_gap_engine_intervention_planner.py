#!/usr/bin/env python3
"""Audit KG-4 gap-engine and intervention-planner authority and final evidence files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_gap_engine import validate_gap_intervention_plan

REQUIRED_AUTHORITY_FILES = [
    "docs/roadmap/knowledge_graph/kg_004_gap_engine_intervention_planner.md",
    "docs/roadmap/knowledge_graph/kg_004_gap_engine_intervention_planner_record.json",
    "docs/knowledge_graph/gap_engine/kg004_gap_engine_manifest.json",
    "docs/knowledge_graph/gap_engine/kg004_gap_engine_policy.md",
    "docs/knowledge_graph/gap_engine/kg004_gap_engine_schema.md",
    "docs/knowledge_graph/gap_engine/kg004_intervention_planner_contract.md",
    "docs/knowledge_graph/gap_engine/kg004_gap_engine_advisory_boundary.md",
    "docs/knowledge_graph/gap_engine/kg004_gap_engine_review_manifest.json",
]
FINAL_PLAN = Path("data/knowledge_graph/gap_engine/grade4_mathematics_gap_intervention_plan.json")
FINAL_SUMMARY = Path("data/knowledge_graph/gap_engine/grade4_mathematics_gap_intervention_plan_summary.json")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    missing = [rel for rel in REQUIRED_AUTHORITY_FILES if not (root / rel).exists()]
    if missing:
        errors.extend([f"missing authority file: {rel}" for rel in missing])

    record = read_json(root / "docs/roadmap/knowledge_graph/kg_004_gap_engine_intervention_planner_record.json")
    manifest = read_json(root / "docs/knowledge_graph/gap_engine/kg004_gap_engine_manifest.json")
    if record.get("kg_id") != "KG-4":
        errors.append("KG-4 record must have kg_id KG-4")
    if manifest.get("kg_id") != "KG-4":
        errors.append("KG-4 manifest must have kg_id KG-4")

    final_valid = False
    final_validation: dict[str, Any] = {}
    if (root / FINAL_PLAN).exists() and (root / FINAL_SUMMARY).exists():
        plan = read_json(root / FINAL_PLAN)
        final_validation = validate_gap_intervention_plan(plan)
        final_valid = final_validation.get("valid") is True
        if not final_valid:
            errors.extend([f"final KG-4 plan invalid: {err}" for err in final_validation.get("errors", [])])

    return {
        "authority_valid": not missing and not [e for e in errors if not e.startswith("final KG-4 plan invalid")],
        "final_valid": final_valid,
        "errors": errors,
        "missing_authority_files": missing,
        "final_plan_path": str(FINAL_PLAN),
        "final_summary_path": str(FINAL_SUMMARY),
        "final_validation": final_validation,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"authority_valid={str(result['authority_valid']).lower()} final_valid={str(result['final_valid']).lower()}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
