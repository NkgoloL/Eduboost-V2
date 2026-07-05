#!/usr/bin/env python3
"""Audit KG-1 CAPS graph foundation authority and generated artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_caps import DEFAULT_SOURCE, build_caps_graph, validate_caps_graph
KG_ID = "KG-1"
KG0_RECORD = Path("docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval_record.json")
RECORD = Path("docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation_record.json")
ROADMAP = Path("docs/roadmap/knowledge_graph/kg_implementation_roadmap.md")
REGISTER = Path("docs/roadmap/knowledge_graph/kg_roadmap_register.json")
MANIFEST = Path("docs/knowledge_graph/caps_graph/kg001_caps_graph_manifest.json")
POLICY = Path("docs/knowledge_graph/caps_graph/kg001_caps_graph_foundation_policy.md")
SCHEMA = Path("docs/knowledge_graph/caps_graph/kg001_caps_graph_schema.md")
LOADER = Path("docs/knowledge_graph/caps_graph/kg001_caps_graph_loader_contract.md")
REVIEW = Path("docs/knowledge_graph/caps_graph/kg001_caps_graph_review_manifest.json")
BOUNDARY = Path("docs/knowledge_graph/caps_graph/kg001_caps_graph_runtime_boundary.md")
GRAPH = Path("data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph.json")
SUMMARY = Path("data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph_summary.json")

BOUNDARY_FALSE_KEYS = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "database_schema_migration_authorised",
    "learner_facing_model_change_authorised",
    "learner_graph_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
]

REQUIRED_POLICY_MARKERS = [
    "CAPS graph foundation recorded: true",
    "Source-grounded CAPS graph required: true",
    "Every CAPS node has source provenance: true",
    "Every CAPS edge has source provenance: true",
    "Runtime KG authority switch authorised: false",
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

    kg0_record = read_json(p(KG0_RECORD))
    kg0_valid = kg0_record.get("kg_id") == "KG-0" and kg0_record.get("formal_kg_roadmap_approval_recorded") is True
    authority_checks["kg0_valid"] = kg0_valid
    for path in [KG0_RECORD, RECORD, ROADMAP, REGISTER, MANIFEST, POLICY, SCHEMA, LOADER, REVIEW, BOUNDARY, DEFAULT_SOURCE]:
        authority_checks[f"exists:{path}"] = p(path).exists()
    record = read_json(p(RECORD))
    manifest = read_json(p(MANIFEST))
    review = read_json(p(REVIEW))
    policy_text = read(p(POLICY))
    boundary_text = read(p(BOUNDARY))

    authority_checks["record_kg_id"] = record.get("kg_id") == KG_ID
    authority_checks["record_pending_or_recorded"] = record.get("status") in {"pending_evidence_capture", "caps_graph_foundation_recorded"}
    for key in BOUNDARY_FALSE_KEYS:
        authority_checks[f"record_boundary_false:{key}"] = record.get(key) is False
        authority_checks[f"manifest_boundary_false:{key}"] = manifest.get("boundary", {}).get(key) is False
        authority_checks[f"boundary_doc_marker:{key}"] = _has(boundary_text, key.replace("_", " ").title().replace("Kg", "KG") + ": false") or _has(boundary_text, key.replace("_", " ") + ": false")
    for marker in REQUIRED_POLICY_MARKERS:
        authority_checks[f"policy_marker:{marker}"] = _has(policy_text, marker)
    authority_checks["review_manifest_grade4_mathematics"] = review.get("scope", {}).get("grade") == 4 and review.get("scope", {}).get("subject") == "mathematics"
    authority_checks["review_manifest_read_model_only"] = review.get("runtime_authority") == "read_model_only"

    try:
        graph = build_caps_graph(p(DEFAULT_SOURCE))
        validation = validate_caps_graph(graph)
        authority_checks["source_builds_valid_graph"] = validation.get("valid") is True
        authority_checks["graph_has_four_terms"] = graph["counts"].get("terms") == 4
        authority_checks["graph_has_minimum_nodes"] = graph["counts"].get("nodes", 0) >= 150
        authority_checks["graph_has_minimum_edges"] = graph["counts"].get("edges", 0) >= 150
    except Exception as exc:  # pragma: no cover - useful in CLI output
        authority_checks["source_builds_valid_graph"] = False
        errors.append(f"CAPS graph source build failed: {exc}")

    if p(GRAPH).exists():
        try:
            final_graph = read_json(p(GRAPH))
            final_validation = validate_caps_graph(final_graph)
            final_checks["graph_artifact_valid"] = final_validation.get("valid") is True
            final_checks["graph_id_correct"] = final_graph.get("graph_id") == "KG-1-CAPS-GRAPH-FOUNDATION-GRADE-4-MATHEMATICS"
            final_checks["summary_exists"] = p(SUMMARY).exists()
        except Exception as exc:
            final_checks["graph_artifact_valid"] = False
            errors.append(f"generated CAPS graph artifact invalid: {exc}")
    else:
        warnings.append("KG-1 graph artifact is not generated yet")
        final_checks["graph_artifact_valid"] = False
        final_checks["graph_id_correct"] = False
        final_checks["summary_exists"] = False

    authority_valid = all(authority_checks.values())
    final_valid = all(final_checks.values())
    errors.extend([name for name, ok in authority_checks.items() if not ok])
    if p(GRAPH).exists():
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
        print(f"KG-1 authority_valid: {result['authority_valid']}")
        print(f"KG-1 final_valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
