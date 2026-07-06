#!/usr/bin/env python3
"""Audit KG-7 authority-switch readiness/legacy-cleanup authority and final evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_authority_switch import validate_authority_switch_readiness_pack

REQUIRED_AUTHORITY_FILES = [
    "docs/roadmap/knowledge_graph/kg_007_authority_switch_legacy_cleanup.md",
    "docs/roadmap/knowledge_graph/kg_007_authority_switch_legacy_cleanup_record.json",
    "docs/knowledge_graph/authority_switch/kg007_authority_switch_manifest.json",
    "docs/knowledge_graph/authority_switch/kg007_authority_switch_policy.md",
    "docs/knowledge_graph/authority_switch/kg007_authority_switch_schema.md",
    "docs/knowledge_graph/authority_switch/kg007_feature_flag_contract.md",
    "docs/knowledge_graph/authority_switch/kg007_legacy_projection_contract.md",
    "docs/knowledge_graph/authority_switch/kg007_rollback_boundary.md",
    "docs/knowledge_graph/authority_switch/kg007_authority_switch_review_manifest.json",
]
FINAL_PACK = Path("data/knowledge_graph/authority_switch/grade4_mathematics_authority_switch_readiness_pack.json")
FINAL_SUMMARY = Path("data/knowledge_graph/authority_switch/grade4_mathematics_authority_switch_readiness_pack_summary.json")


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

    record = read_json(root / "docs/roadmap/knowledge_graph/kg_007_authority_switch_legacy_cleanup_record.json")
    manifest = read_json(root / "docs/knowledge_graph/authority_switch/kg007_authority_switch_manifest.json")
    if record.get("kg_id") != "KG-7":
        errors.append("KG-7 record must have kg_id KG-7")
    if manifest.get("kg_id") != "KG-7":
        errors.append("KG-7 manifest must have kg_id KG-7")

    final_valid = False
    final_validation: dict[str, Any] = {}
    if (root / FINAL_PACK).exists() and (root / FINAL_SUMMARY).exists():
        pack = read_json(root / FINAL_PACK)
        final_validation = validate_authority_switch_readiness_pack(pack)
        final_valid = final_validation.get("valid") is True
        if not final_valid:
            errors.extend([f"final KG-7 authority-switch readiness pack invalid: {err}" for err in final_validation.get("errors", [])])

    authority_errors = [e for e in errors if not e.startswith("final KG-7 authority-switch readiness pack invalid")]
    return {
        "authority_valid": not missing and not authority_errors,
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
