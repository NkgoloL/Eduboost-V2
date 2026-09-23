"""
verify_curriculum_registry_consistency.py
=========================================
Automated consistency and integrity verification across all CAPS curriculum manifests:
1. data/content_factory/scopes.json
2. data/content_factory/coverage_targets.json
3. data/curriculum/registries/caps_curriculum_source_completeness.json
4. data/content_factory/source_text_extracts_manifest.json
5. data/caps/source_documents/manifest.json
6. data/caps/topic_maps/*.json

Asserts exact set equivalence of all 51 curriculum scopes and zero manifest drift.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def verify_curriculum_registry_consistency(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    errors: list[str] = []

    # 1. Authoritative Scopes: data/content_factory/scopes.json
    scopes_path = repo_root / "data/content_factory/scopes.json"
    if not scopes_path.exists():
        errors.append(f"Missing authoritative scopes file: {scopes_path}")
        return {"verified": False, "errors": errors}

    scopes_data = json.loads(scopes_path.read_text(encoding="utf-8")).get("scopes", [])
    authoritative_scope_ids = set(s["scope_id"] for s in scopes_data)
    total_scopes = len(authoritative_scope_ids)

    if total_scopes != 51:
        errors.append(f"Expected 51 scopes in scopes.json, found {total_scopes}")

    # 2. Coverage Targets: data/content_factory/coverage_targets.json
    cov_path = repo_root / "data/content_factory/coverage_targets.json"
    cov_scope_ids: set[str] = set()
    if not cov_path.exists():
        errors.append(f"Missing coverage targets file: {cov_path}")
    else:
        cov_data = json.loads(cov_path.read_text(encoding="utf-8"))
        targets = cov_data.get("targets", [])
        if isinstance(targets, list):
            for t in targets:
                cov_scope_ids.add(t["scope_id"])
        elif isinstance(targets, dict):
            for k, v in targets.items():
                cov_scope_ids.add(v.get("scope_id", k))

        diff_cov = authoritative_scope_ids ^ cov_scope_ids
        if diff_cov:
            errors.append(f"coverage_targets.json scope mismatch (diff: {sorted(list(diff_cov))})")

    # 3. Source Completeness Registry: data/curriculum/registries/caps_curriculum_source_completeness.json
    comp_path = repo_root / "data/curriculum/registries/caps_curriculum_source_completeness.json"
    comp_scope_ids: set[str] = set()
    if not comp_path.exists():
        errors.append(f"Missing source completeness registry: {comp_path}")
    else:
        comp_data = json.loads(comp_path.read_text(encoding="utf-8"))
        comp_scopes = comp_data.get("scopes", [])
        comp_scope_ids = set(s["scope_id"] for s in comp_scopes)
        diff_comp = authoritative_scope_ids ^ comp_scope_ids
        if diff_comp:
            errors.append(f"caps_curriculum_source_completeness.json scope mismatch (diff: {sorted(list(diff_comp))})")

    # 4. Source Text Extracts: data/content_factory/source_text_extracts_manifest.json
    extracts_path = repo_root / "data/content_factory/source_text_extracts_manifest.json"
    extract_scope_ids: set[str] = set()
    if not extracts_path.exists():
        errors.append(f"Missing source text extracts manifest: {extracts_path}")
    else:
        extracts_data = json.loads(extracts_path.read_text(encoding="utf-8"))
        for rec in extracts_data.get("records", []):
            for sc in rec.get("scope_ids", []):
                extract_scope_ids.add(sc)
        diff_ext = authoritative_scope_ids ^ extract_scope_ids
        if diff_ext:
            errors.append(f"source_text_extracts_manifest.json scope mismatch (diff: {sorted(list(diff_ext))})")

    # 5. Source Documents Manifest: data/caps/source_documents/manifest.json
    src_manifest_path = repo_root / "data/caps/source_documents/manifest.json"
    if not src_manifest_path.exists():
        errors.append(f"Missing source documents manifest: {src_manifest_path}")
    else:
        src_manifest_data = json.loads(src_manifest_path.read_text(encoding="utf-8"))
        manifest_doc_ids = set(d["document_id"] for d in src_manifest_data.get("documents", []))
        for s in scopes_data:
            for s_doc in s.get("source_documents", []):
                if s_doc not in manifest_doc_ids:
                    errors.append(f"Scope {s['scope_id']} references unregistered source document: {s_doc}")

    # 6. Topic Map Files on Disk
    missing_topic_maps: list[str] = []
    for s in scopes_data:
        tm_path_rel = s.get("topic_map_path")
        if not tm_path_rel:
            missing_topic_maps.append(f"Scope {s['scope_id']} has no topic_map_path")
            continue
        tm_full_path = repo_root / tm_path_rel
        if not tm_full_path.exists():
            missing_topic_maps.append(f"Scope {s['scope_id']} topic map missing at {tm_path_rel}")
        else:
            try:
                tm_json = json.loads(tm_full_path.read_text(encoding="utf-8"))
                if "terms" not in tm_json or len(tm_json["terms"]) != 4:
                    errors.append(f"Topic map {tm_path_rel} does not contain exactly 4 terms")
            except Exception as e:
                errors.append(f"Topic map {tm_path_rel} invalid JSON: {e}")

    if missing_topic_maps:
        errors.extend(missing_topic_maps)

    verified = len(errors) == 0
    report = {
        "verified": verified,
        "total_scopes": total_scopes,
        "authoritative_scopes_count": len(authoritative_scope_ids),
        "coverage_targets_scopes_count": len(cov_scope_ids),
        "source_completeness_scopes_count": len(comp_scope_ids),
        "text_extracts_scopes_count": len(extract_scope_ids),
        "errors": errors,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify CAPS Curriculum Registry Consistency")
    parser.add_argument("--json", action="store_true", help="Print output as JSON")
    args = parser.parse_args()

    report = verify_curriculum_registry_consistency()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if report["verified"]:
            print(f"PASS: All {report['total_scopes']} curriculum scopes are in 100% exact agreement across all manifests.")
        else:
            print(f"FAIL: Registry consistency errors detected ({len(report['errors'])} errors):")
            for err in report["errors"]:
                print(f"  - {err}")

    sys.exit(0 if report["verified"] else 1)


if __name__ == "__main__":
    main()
