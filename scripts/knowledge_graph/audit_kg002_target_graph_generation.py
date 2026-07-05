#!/usr/bin/env python3
"""Audit KG-2 target graph generation authority and generated artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_target import DEFAULT_CAPS_GRAPH, build_target_graph, validate_target_graph

KG_ID = "KG-2"
KG1_RECORD = Path("docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation_record.json")
RECORD = Path("docs/roadmap/knowledge_graph/kg_002_target_graph_generation_record.json")
ROADMAP = Path("docs/roadmap/knowledge_graph/kg_implementation_roadmap.md")
REGISTER = Path("docs/roadmap/knowledge_graph/kg_roadmap_register.json")
MANIFEST = Path("docs/knowledge_graph/target_graph/kg002_target_graph_manifest.json")
POLICY = Path("docs/knowledge_graph/target_graph/kg002_target_graph_generation_policy.md")
SCHEMA = Path("docs/knowledge_graph/target_graph/kg002_target_graph_schema.md")
POLICY_CONTRACT = Path("docs/knowledge_graph/target_graph/kg002_target_graph_policy_contract.md")
REVIEW = Path("docs/knowledge_graph/target_graph/kg002_target_graph_review_manifest.json")
BOUNDARY = Path("docs/knowledge_graph/target_graph/kg002_target_graph_runtime_boundary.md")
TARGET_GRAPH = Path("data/knowledge_graph/target_graph/grade4_mathematics_target_graph.json")
SUMMARY = Path("data/knowledge_graph/target_graph/grade4_mathematics_target_graph_summary.json")

BOUNDARY_FALSE_KEYS = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "database_schema_migration_authorised",
    "learner_facing_model_change_authorised",
    "learner_graph_implementation_authorised",
    "target_graph_runtime_authority_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
]

REQUIRED_POLICY_MARKERS = [
    "Target graph generation recorded: true",
    "Target graph references approved CAPS nodes only: true",
    "Required mastery thresholds present: true",
    "Required confidence thresholds present: true",
    "Target graph runtime authority authorised: false",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _has(text: str, marker: str) -> bool:
    return marker.lower() in text.lower()


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    def p(path: Path) -> Path:
        return root / path

    errors: list[str] = []
    warnings: list[str] = []
    authority_checks: dict[str, bool] = {}
    final_checks: dict[str, bool] = {}

    kg1_record = read_json(p(KG1_RECORD))
    kg1_valid = kg1_record.get("kg_id") == "KG-1" and kg1_record.get("caps_graph_foundation_recorded") is True
    authority_checks["kg1_valid"] = kg1_valid
    for path in [KG1_RECORD, RECORD, ROADMAP, REGISTER, MANIFEST, POLICY, SCHEMA, POLICY_CONTRACT, REVIEW, BOUNDARY, DEFAULT_CAPS_GRAPH]:
        authority_checks[f"exists:{path}"] = p(path).exists()
    record = read_json(p(RECORD))
    manifest = read_json(p(MANIFEST))
    review = read_json(p(REVIEW))
    policy_text = read(p(POLICY))
    boundary_text = read(p(BOUNDARY))

    authority_checks["record_kg_id"] = record.get("kg_id") == KG_ID
    authority_checks["record_pending_or_recorded"] = record.get("status") in {"pending_evidence_capture", "target_graph_generation_recorded"}
    for key in BOUNDARY_FALSE_KEYS:
        authority_checks[f"record_boundary_false:{key}"] = record.get(key) is False
        authority_checks[f"manifest_boundary_false:{key}"] = manifest.get("boundary", {}).get(key) is False
        authority_checks[f"boundary_doc_marker:{key}"] = _has(boundary_text, key.replace("_", " ") + ": false") or _has(boundary_text, key.replace("_", " ").title().replace("Kg", "KG") + ": false")
    for marker in REQUIRED_POLICY_MARKERS:
        authority_checks[f"policy_marker:{marker}"] = _has(policy_text, marker)
    authority_checks["review_manifest_grade4_mathematics"] = review.get("scope", {}).get("grade") == 4 and review.get("scope", {}).get("subject") == "mathematics"
    authority_checks["review_manifest_read_model_only"] = review.get("runtime_authority") == "target_graph_read_model_only"

    try:
        graph = build_target_graph(p(DEFAULT_CAPS_GRAPH))
        validation = validate_target_graph(graph)
        authority_checks["source_builds_valid_target_graph"] = validation.get("valid") is True
        authority_checks["target_graph_has_minimum_states"] = graph["counts"].get("target_states", 0) >= 100
        authority_checks["target_graph_has_prerequisite_edges"] = graph["counts"].get("target_prerequisite_edges", 0) >= 20
    except Exception as exc:  # pragma: no cover - useful in CLI output
        authority_checks["source_builds_valid_target_graph"] = False
        errors.append(f"target graph source build failed: {exc}")

    if p(TARGET_GRAPH).exists():
        try:
            final_graph = read_json(p(TARGET_GRAPH))
            final_validation = validate_target_graph(final_graph)
            final_checks["target_graph_artifact_valid"] = final_validation.get("valid") is True
            final_checks["target_graph_id_correct"] = final_graph.get("graph_id") == "KG-2-TARGET-GRAPH-GRADE-4-MATHEMATICS"
            final_checks["summary_exists"] = p(SUMMARY).exists()
        except Exception as exc:
            final_checks["target_graph_artifact_valid"] = False
            errors.append(f"generated target graph artifact invalid: {exc}")
    else:
        warnings.append("KG-2 target graph artifact is not generated yet")
        final_checks["target_graph_artifact_valid"] = False
        final_checks["target_graph_id_correct"] = False
        final_checks["summary_exists"] = False

    authority_valid = all(authority_checks.values())
    final_valid = all(final_checks.values())
    errors.extend([name for name, ok in authority_checks.items() if not ok])
    if p(TARGET_GRAPH).exists():
        errors.extend([name for name, ok in final_checks.items() if not ok])
    return {
        "kg_id": KG_ID,
        "authority_valid": authority_valid,
        "final_valid": final_valid,
        "authority_checks": authority_checks,
        "final_checks": final_checks,
        "errors": errors,
        "warnings": warnings,
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
        print(f"KG-2 authority_valid: {result['authority_valid']}")
        print(f"KG-2 final_valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
