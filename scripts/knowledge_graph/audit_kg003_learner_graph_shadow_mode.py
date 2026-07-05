#!/usr/bin/env python3
"""Audit KG-3 learner graph shadow-mode authority and final evidence files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_learner_shadow import validate_learner_shadow_graph

REQUIRED_AUTHORITY_FILES = [
    "docs/roadmap/knowledge_graph/kg_003_learner_graph_shadow_mode.md",
    "docs/roadmap/knowledge_graph/kg_003_learner_graph_shadow_mode_record.json",
    "docs/knowledge_graph/learner_shadow/kg003_learner_graph_manifest.json",
    "docs/knowledge_graph/learner_shadow/kg003_learner_graph_shadow_policy.md",
    "docs/knowledge_graph/learner_shadow/kg003_learner_graph_shadow_schema.md",
    "docs/knowledge_graph/learner_shadow/kg003_shadow_observation_fixture_contract.md",
    "docs/knowledge_graph/learner_shadow/kg003_learner_graph_shadow_privacy_boundary.md",
    "docs/knowledge_graph/learner_shadow/kg003_learner_graph_shadow_runtime_boundary.md",
    "docs/knowledge_graph/learner_shadow/kg003_learner_graph_shadow_review_manifest.json",
    "data/knowledge_graph/learner_shadow_mode/kg003_shadow_observation_fixture.json",
]
FINAL_GRAPH = Path("data/knowledge_graph/learner_shadow_mode/grade4_mathematics_learner_shadow_graph.json")
FINAL_SUMMARY = Path("data/knowledge_graph/learner_shadow_mode/grade4_mathematics_learner_shadow_graph_summary.json")


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

    record = read_json(root / "docs/roadmap/knowledge_graph/kg_003_learner_graph_shadow_mode_record.json")
    manifest = read_json(root / "docs/knowledge_graph/learner_shadow/kg003_learner_graph_manifest.json")
    fixture = read_json(root / "data/knowledge_graph/learner_shadow_mode/kg003_shadow_observation_fixture.json")
    if record.get("kg_id") != "KG-3":
        errors.append("KG-3 record must have kg_id KG-3")
    if manifest.get("kg_id") != "KG-3":
        errors.append("KG-3 manifest must have kg_id KG-3")
    if fixture.get("privacy_boundary", {}).get("uses_live_learner_data") is not False:
        errors.append("KG-3 fixture must explicitly avoid live learner data")

    final_valid = False
    final_validation: dict[str, Any] = {}
    if (root / FINAL_GRAPH).exists() and (root / FINAL_SUMMARY).exists():
        graph = read_json(root / FINAL_GRAPH)
        final_validation = validate_learner_shadow_graph(graph)
        final_valid = final_validation.get("valid") is True
        if not final_valid:
            errors.extend([f"final learner shadow graph invalid: {err}" for err in final_validation.get("errors", [])])

    return {
        "authority_valid": not missing and not [e for e in errors if not e.startswith("final learner shadow graph invalid")],
        "final_valid": final_valid,
        "errors": errors,
        "missing_authority_files": missing,
        "final_graph_path": str(FINAL_GRAPH),
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
