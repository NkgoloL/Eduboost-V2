#!/usr/bin/env python3
"""Audit KG-5 graph-grounded lesson/assessment generation authority and final evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_grounded_generation import validate_graph_grounded_generation_pack

REQUIRED_AUTHORITY_FILES = [
    "docs/roadmap/knowledge_graph/kg_005_graph_grounded_lesson_assessment_generation.md",
    "docs/roadmap/knowledge_graph/kg_005_graph_grounded_lesson_assessment_generation_record.json",
    "docs/knowledge_graph/grounded_generation/kg005_grounded_generation_manifest.json",
    "docs/knowledge_graph/grounded_generation/kg005_grounded_generation_policy.md",
    "docs/knowledge_graph/grounded_generation/kg005_grounded_generation_schema.md",
    "docs/knowledge_graph/grounded_generation/kg005_lesson_generation_contract.md",
    "docs/knowledge_graph/grounded_generation/kg005_assessment_generation_contract.md",
    "docs/knowledge_graph/grounded_generation/kg005_human_review_boundary.md",
    "docs/knowledge_graph/grounded_generation/kg005_grounded_generation_review_manifest.json",
]
FINAL_PACK = Path("data/knowledge_graph/grounded_generation/grade4_mathematics_graph_grounded_generation_pack.json")
FINAL_SUMMARY = Path("data/knowledge_graph/grounded_generation/grade4_mathematics_graph_grounded_generation_pack_summary.json")


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

    record = read_json(root / "docs/roadmap/knowledge_graph/kg_005_graph_grounded_lesson_assessment_generation_record.json")
    manifest = read_json(root / "docs/knowledge_graph/grounded_generation/kg005_grounded_generation_manifest.json")
    if record.get("kg_id") != "KG-5":
        errors.append("KG-5 record must have kg_id KG-5")
    if manifest.get("kg_id") != "KG-5":
        errors.append("KG-5 manifest must have kg_id KG-5")

    final_valid = False
    final_validation: dict[str, Any] = {}
    if (root / FINAL_PACK).exists() and (root / FINAL_SUMMARY).exists():
        pack = read_json(root / FINAL_PACK)
        final_validation = validate_graph_grounded_generation_pack(pack)
        final_valid = final_validation.get("valid") is True
        if not final_valid:
            errors.extend([f"final KG-5 generation pack invalid: {err}" for err in final_validation.get("errors", [])])

    return {
        "authority_valid": not missing and not [e for e in errors if not e.startswith("final KG-5 generation pack invalid")],
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
