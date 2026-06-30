#!/usr/bin/env python3
"""Verify Technical Audit Phase 02C Content Factory scope registry expansion.

This verifier is intentionally read-only. It proves that the file-backed
Content Factory registry contains the full generated source-backed scope set
required by the backend-fast tests while preserving the learner-visibility
boundary: only grade4_mathematics_en is active; the remaining generated scopes
are review/staging candidates.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCOPES_PATH = ROOT / "data" / "content_factory" / "scopes.json"
SOURCE_MANIFEST_PATH = ROOT / "data" / "caps" / "source_documents" / "manifest.json"
REQUIRED_ARTIFACT_LAYERS = {
    "diagnostic_items",
    "lessons",
    "assessment_blueprints",
    "study_plan_templates",
}
EXPECTED_SCOPE_COUNT = 51
EXPECTED_ACTIVE_SCOPE = "grade4_mathematics_en"
EXPECTED_GRADE5_SCOPE = "grade5_mathematics_en"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _topic_refs(topic_map_path: Path) -> list[str]:
    raw = _load_json(topic_map_path)
    refs: list[str] = []
    for term in raw.get("terms", []):
        for topic in term.get("topics", []):
            if topic.get("caps_ref"):
                refs.append(str(topic["caps_ref"]))
    return refs


def _source_statuses() -> dict[str, str]:
    raw = _load_json(SOURCE_MANIFEST_PATH)
    return {str(row["document_id"]): str(row.get("status")) for row in raw.get("documents", [])}


def verify(*, static_only: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    raw = _load_json(SCOPES_PATH)
    scopes = raw.get("scopes", [])
    by_id = {str(scope.get("scope_id")): scope for scope in scopes}

    if raw.get("schema_version") != "1.0":
        errors.append("data/content_factory/scopes.json schema_version must be 1.0")
    if len(scopes) != len(by_id):
        errors.append("data/content_factory/scopes.json contains duplicate scope_id values")
    if len(scopes) != EXPECTED_SCOPE_COUNT:
        errors.append(f"expected {EXPECTED_SCOPE_COUNT} Content Factory scopes, found {len(scopes)}")
    if EXPECTED_ACTIVE_SCOPE not in by_id:
        errors.append(f"missing active launch scope {EXPECTED_ACTIVE_SCOPE}")
    if EXPECTED_GRADE5_SCOPE not in by_id:
        errors.append(f"missing dominant backend-fast blocker scope {EXPECTED_GRADE5_SCOPE}")

    active_scopes = sorted(scope_id for scope_id, scope in by_id.items() if scope.get("status") == "active")
    if active_scopes != [EXPECTED_ACTIVE_SCOPE]:
        errors.append(f"expected only {EXPECTED_ACTIVE_SCOPE} to be active, found {active_scopes}")

    source_statuses = _source_statuses()
    generation_ready = 0
    staging_ready = 0
    for scope_id in sorted(by_id):
        scope = by_id[scope_id]
        topic_map_path = ROOT / str(scope.get("topic_map_path") or "")
        if not topic_map_path.exists():
            errors.append(f"{scope_id} topic_map_path is missing: {scope.get('topic_map_path')}")
            continue
        declared_refs = list(scope.get("caps_refs") or [])
        topic_refs = _topic_refs(topic_map_path)
        if not declared_refs:
            errors.append(f"{scope_id} must declare topic-level caps_refs")
        missing_refs = sorted(set(declared_refs) - set(topic_refs))
        if missing_refs:
            errors.append(f"{scope_id} declares refs not present in topic map: {missing_refs[:5]}")

        documents = list(scope.get("source_documents") or [])
        if not documents:
            errors.append(f"{scope_id} must reference source_documents")
        missing_documents = [doc for doc in documents if doc not in source_statuses]
        if missing_documents:
            errors.append(f"{scope_id} references unknown source documents: {missing_documents}")
        approved_source = any(source_statuses.get(doc) == "topic_map_approved" for doc in documents)
        if approved_source and declared_refs:
            generation_ready += 1
        else:
            warnings.append(f"{scope_id} is not generation-ready from approved source documents")

        artifact_paths = dict(scope.get("artifact_paths") or {})
        missing_layers = sorted(REQUIRED_ARTIFACT_LAYERS - set(artifact_paths))
        if missing_layers:
            errors.append(f"{scope_id} missing artifact path layers: {missing_layers}")
        layer_files_present = True
        for layer in sorted(REQUIRED_ARTIFACT_LAYERS):
            relative = artifact_paths.get(layer)
            if not relative:
                layer_files_present = False
                continue
            artifact_path = ROOT / str(relative)
            if not artifact_path.exists():
                layer_files_present = False
                errors.append(f"{scope_id} {layer} artifact does not exist: {relative}")
        if layer_files_present and approved_source and declared_refs:
            staging_ready += 1

    grade5 = by_id.get(EXPECTED_GRADE5_SCOPE) or {}
    if grade5:
        if grade5.get("status") != "review":
            errors.append("grade5_mathematics_en must be review, not active or planned")
        if grade5.get("topic_map_path") != "data/caps/topic_maps/grade5_mathematics_en.json":
            errors.append("grade5_mathematics_en must reference its deterministic topic map")
        if len(grade5.get("caps_refs") or []) != 16:
            errors.append(f"grade5_mathematics_en must expose 16 topic-level CAPS refs, found {len(grade5.get('caps_refs') or [])}")

    grade4 = by_id.get(EXPECTED_ACTIVE_SCOPE) or {}
    if grade4:
        if grade4.get("status") != "active":
            errors.append("grade4_mathematics_en must remain the only learner-visible active scope")
        if grade4.get("caps_refs") != ["4.M.1.1", "4.M.1.2", "4.M.1.3"]:
            errors.append("grade4_mathematics_en launch caps_refs changed unexpectedly")

    registry_import_valid: bool | None = None
    if not static_only:
        try:
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            from app.services.content_scope_registry import ContentScopeRegistry

            registry = ContentScopeRegistry()
            registry_scopes = registry.list_scopes()
            registry_import_valid = (
                len(registry_scopes) == EXPECTED_SCOPE_COUNT
                and registry.get_scope(EXPECTED_GRADE5_SCOPE).status.value == "review"
                and [scope.scope_id for scope in registry.list_active_scopes()] == [EXPECTED_ACTIVE_SCOPE]
            )
            if not registry_import_valid:
                errors.append("ContentScopeRegistry import contract did not match expanded registry expectations")
        except Exception as exc:  # pragma: no cover - surfaced in JSON output for CI diagnosis
            registry_import_valid = False
            errors.append(f"ContentScopeRegistry import verification failed: {type(exc).__name__}: {exc}")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "scope_count": len(scopes),
        "active_scopes": active_scopes,
        "generation_ready_scope_count": generation_ready,
        "staging_ready_scope_count": staging_ready,
        "grade5_status": grade5.get("status"),
        "grade5_caps_ref_count": len(grade5.get("caps_refs") or []),
        "registry_import_valid": registry_import_valid,
        "kg_boundary": "No runtime knowledge-graph implementation is introduced; registry metadata preserves future graph/source hooks.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--static-only", action="store_true", help="Do not import app registry code.")
    args = parser.parse_args()
    result = verify(static_only=args.static_only)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Content scope registry expansion verification")
        print(f"  valid: {result['valid']}")
        print(f"  scope_count: {result['scope_count']}")
        print(f"  active_scopes: {result['active_scopes']}")
        print(f"  generation_ready_scope_count: {result['generation_ready_scope_count']}")
        print(f"  staging_ready_scope_count: {result['staging_ready_scope_count']}")
        if result["errors"]:
            print("Errors:")
            for error in result["errors"]:
                print(f"  - {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
