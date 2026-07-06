#!/usr/bin/env python3
"""Audit KG-6 product-alignment authority and final evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_product_alignment import validate_product_alignment_pack

REQUIRED_AUTHORITY_FILES = [
    "docs/roadmap/knowledge_graph/kg_006_tutor_study_plan_gamification_parent_alignment.md",
    "docs/roadmap/knowledge_graph/kg_006_tutor_study_plan_gamification_parent_alignment_record.json",
    "docs/knowledge_graph/product_alignment/kg006_product_alignment_manifest.json",
    "docs/knowledge_graph/product_alignment/kg006_product_alignment_policy.md",
    "docs/knowledge_graph/product_alignment/kg006_product_alignment_schema.md",
    "docs/knowledge_graph/product_alignment/kg006_tutor_alignment_contract.md",
    "docs/knowledge_graph/product_alignment/kg006_study_plan_alignment_contract.md",
    "docs/knowledge_graph/product_alignment/kg006_gamification_alignment_contract.md",
    "docs/knowledge_graph/product_alignment/kg006_parent_alignment_privacy_boundary.md",
    "docs/knowledge_graph/product_alignment/kg006_product_alignment_review_manifest.json",
]
FINAL_PACK = Path("data/knowledge_graph/product_alignment/grade4_mathematics_product_alignment_pack.json")
FINAL_SUMMARY = Path("data/knowledge_graph/product_alignment/grade4_mathematics_product_alignment_pack_summary.json")


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

    record = read_json(root / "docs/roadmap/knowledge_graph/kg_006_tutor_study_plan_gamification_parent_alignment_record.json")
    manifest = read_json(root / "docs/knowledge_graph/product_alignment/kg006_product_alignment_manifest.json")
    if record.get("kg_id") != "KG-6":
        errors.append("KG-6 record must have kg_id KG-6")
    if manifest.get("kg_id") != "KG-6":
        errors.append("KG-6 manifest must have kg_id KG-6")

    final_valid = False
    final_validation: dict[str, Any] = {}
    if (root / FINAL_PACK).exists() and (root / FINAL_SUMMARY).exists():
        pack = read_json(root / FINAL_PACK)
        final_validation = validate_product_alignment_pack(pack)
        final_valid = final_validation.get("valid") is True
        if not final_valid:
            errors.extend([f"final KG-6 product alignment pack invalid: {err}" for err in final_validation.get("errors", [])])

    return {
        "authority_valid": not missing and not [e for e in errors if not e.startswith("final KG-6 product alignment pack invalid")],
        "final_valid": final_valid,
        "errors": errors,
        "missing_authority_files": missing,
        "final_pack_path": str(FINAL_PACK),
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
