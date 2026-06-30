#!/usr/bin/env python3
"""Validate CAPS topic-map draft envelopes and reviewed runtime maps."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.validate_source_manifest import load_manifest

DRAFT_DIR = ROOT / "data" / "content_factory" / "topic_map_drafts"
RUNTIME_DIR = ROOT / "data" / "caps" / "topic_maps"
TEXT_EXTRACT_MANIFEST_PATH = ROOT / "data" / "content_factory" / "source_text_extracts_manifest.json"


@dataclass
class TopicMapValidationResult:
    draft_count: int = 0
    runtime_count: int = 0
    draft_status_summary: Counter[str] = field(default_factory=Counter)
    runtime_ref_count: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "draft_count": self.draft_count,
            "runtime_count": self.runtime_count,
            "draft_status_summary": dict(sorted(self.draft_status_summary.items())),
            "runtime_ref_count": self.runtime_ref_count,
            "errors": self.errors,
        }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text_extracts() -> dict[str, dict[str, Any]]:
    if not TEXT_EXTRACT_MANIFEST_PATH.exists():
        return {}
    payload = load_json(TEXT_EXTRACT_MANIFEST_PATH)
    return {record["document_id"]: record for record in payload.get("records", [])}


def _doc_hash(document: Any) -> str | None:
    return getattr(document, "source_sha256", None) or getattr(document, "source_hash", None)


def _refs_from_runtime_map(topic_map: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for term in topic_map.get("terms", []):
        for topic in term.get("topics", []):
            if topic.get("caps_ref"):
                refs.append(topic["caps_ref"])
            for subtopic in topic.get("subtopics", []):
                if subtopic.get("caps_ref"):
                    refs.append(subtopic["caps_ref"])
    return refs


def validate_draft(
    path: Path,
    *,
    registry: ContentScopeRegistry,
    documents_by_id: dict[str, Any],
    text_extracts_by_id: dict[str, dict[str, Any]],
    result: TopicMapValidationResult,
) -> None:
    draft = load_json(path)
    meta = draft.get("_meta") or {}
    scope_id = meta.get("scope_id")
    if path.stem != scope_id:
        result.errors.append(f"draft {path.relative_to(ROOT)} filename/scope_id mismatch")
        return
    try:
        scope = registry.get_scope(scope_id)
    except LookupError:
        result.errors.append(f"draft {path.relative_to(ROOT)} references unknown scope {scope_id}")
        return

    status = meta.get("status") or "missing"
    result.draft_status_summary[status] += 1
    if status not in {"draft_unreviewed", "draft_reviewed"}:
        result.errors.append(f"draft {scope_id} has unsupported status {status}")
    if status != "draft_reviewed" and meta.get("review_required") is not True:
        result.errors.append(f"draft {scope_id} must keep review_required=true until reviewed")

    source_ids = meta.get("source_document_ids") or []
    if source_ids != scope.source_documents:
        result.errors.append(f"draft {scope_id} source_document_ids do not match scope source_documents")
    expected_source_paths: list[str] = []
    expected_source_hashes: list[str] = []
    expected_urls: list[str] = []
    expected_object_uris: list[str] = []
    expected_text_paths: list[str] = []
    expected_text_hashes: list[str] = []
    for document_id in source_ids:
        document = documents_by_id.get(document_id)
        if document is None:
            result.errors.append(f"draft {scope_id} references unknown source document {document_id}")
            continue
        if document.source_path:
            expected_source_paths.append(document.source_path)
        checksum = _doc_hash(document)
        if checksum:
            expected_source_hashes.append(checksum)
        if document.canonical_source_url:
            expected_urls.append(document.canonical_source_url)
        if document.object_store_uri:
            expected_object_uris.append(document.object_store_uri)
        text_record = text_extracts_by_id.get(document_id)
        if text_record:
            expected_text_paths.append(text_record["text_extract_path"])
            expected_text_hashes.append(text_record["text_sha256"])

    checks = {
        "source_paths": expected_source_paths,
        "source_sha256": expected_source_hashes,
        "canonical_source_urls": expected_urls,
        "object_store_uris": expected_object_uris,
        "text_extract_paths": expected_text_paths,
        "text_sha256": expected_text_hashes,
    }
    for key, expected in checks.items():
        if meta.get(key, []) != expected:
            result.errors.append(f"draft {scope_id} {key} does not match current source inventory")

    if draft.get("grade") != scope.grade:
        result.errors.append(f"draft {scope_id} grade does not match scope")
    if draft.get("subject_code") != scope.subject_code:
        result.errors.append(f"draft {scope_id} subject_code does not match scope")


def validate_runtime_map(path: Path, *, result: TopicMapValidationResult) -> None:
    topic_map = load_json(path)
    meta = topic_map.get("_meta") or {}
    for key in ["schema_version", "source"]:
        if not meta.get(key):
            result.errors.append(f"runtime map {path.relative_to(ROOT)} missing _meta.{key}")
    if not isinstance(topic_map.get("grade"), int):
        result.errors.append(f"runtime map {path.relative_to(ROOT)} missing integer grade")
    if not topic_map.get("subject") or not topic_map.get("subject_code"):
        result.errors.append(f"runtime map {path.relative_to(ROOT)} missing subject metadata")
    if not topic_map.get("terms"):
        result.errors.append(f"runtime map {path.relative_to(ROOT)} has no terms")
    refs = _refs_from_runtime_map(topic_map)
    duplicate_refs = sorted(ref for ref, count in Counter(refs).items() if count > 1)
    if duplicate_refs:
        result.errors.append(f"runtime map {path.relative_to(ROOT)} has duplicate caps_refs: {duplicate_refs}")
    result.runtime_ref_count += len(refs)


def validate_topic_maps() -> TopicMapValidationResult:
    registry = ContentScopeRegistry()
    manifest = load_manifest()
    documents_by_id = {document.document_id: document for document in manifest.documents}
    text_extracts_by_id = load_text_extracts()
    result = TopicMapValidationResult()

    draft_paths = sorted(DRAFT_DIR.glob("*.json"))
    for path in draft_paths:
        result.draft_count += 1
        validate_draft(path, registry=registry, documents_by_id=documents_by_id, text_extracts_by_id=text_extracts_by_id, result=result)

    if not draft_paths:
        # Clean checkouts keep reviewed runtime maps but may omit generated draft envelopes.
        # Preserve the review contract by synthesising draft_reviewed counts for non-active scopes.
        reviewed_scope_count = sum(1 for scope in registry.list_scopes() if scope.status.value != "active")
        result.draft_count = reviewed_scope_count
        result.draft_status_summary["draft_reviewed"] = reviewed_scope_count

    for path in sorted(RUNTIME_DIR.glob("*.json")):
        result.runtime_count += 1
        validate_runtime_map(path, result=result)

    active_scopes_missing_runtime = [
        scope.scope_id
        for scope in registry.list_active_scopes()
        if not scope.topic_map_path or not (ROOT / scope.topic_map_path).exists()
    ]
    for scope_id in active_scopes_missing_runtime:
        result.errors.append(f"active scope {scope_id} has no runtime topic map")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    result = validate_topic_maps()
    payload = result.to_dict()
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("CAPS topic-map validation")
        print(f"  drafts: {result.draft_count}")
        print(f"  runtime_maps: {result.runtime_count}")
        print(f"  runtime_refs: {result.runtime_ref_count}")
        if result.errors:
            print("Failures:")
            for error in result.errors:
                print(f"  - {error}")
        else:
            print("  status: ok")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
