#!/usr/bin/env python3
"""Validate CAPS source-document inventory and scope source readiness."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.content_source import SourceDocumentManifest, SourceDocumentStatus
from app.domain.content_scope import ContentScopeStatus
from app.services.content_scope_registry import ContentScopeRegistry

MANIFEST_PATH = ROOT / "data" / "caps" / "source_documents" / "manifest.json"


@dataclass
class SourceManifestValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    generation_ready_scope_ids: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors


def load_manifest(path: Path = MANIFEST_PATH) -> SourceDocumentManifest:
    return SourceDocumentManifest.model_validate_json(path.read_text(encoding="utf-8"))


def validate_source_manifest(
    *,
    manifest_path: Path = MANIFEST_PATH,
    registry: ContentScopeRegistry | None = None,
    require_planned_scope_sources: bool = True,
    verify_local_files: bool = False,
) -> SourceManifestValidationResult:
    registry = registry or ContentScopeRegistry()
    manifest = load_manifest(manifest_path)
    result = SourceManifestValidationResult()
    by_id = {document.document_id: document for document in manifest.documents}
    if len(by_id) != len(manifest.documents):
        result.errors.append("duplicate source document_id values")

    for document in manifest.documents:
        if document.status in {SourceDocumentStatus.SOURCE_LOADED, SourceDocumentStatus.TOPIC_MAP_APPROVED}:
            if not document.source_path:
                result.errors.append(f"source document {document.document_id} is {document.status.value} without source_path")
                continue
            if not document.source_hash:
                result.errors.append(f"source document {document.document_id} is {document.status.value} without source_hash")
            if document.source_sha256 and document.source_hash and document.source_sha256 != document.source_hash:
                result.errors.append(f"source document {document.document_id} source_sha256/source_hash mismatch")
            if verify_local_files:
                source_path = ROOT / document.source_path
                if not source_path.exists():
                    if getattr(document, "object_store_uri", None):
                        result.warnings.append(
                            f"source document {document.document_id} local cache missing; object store URI recorded"
                        )
                        continue
                    result.errors.append(f"source document {document.document_id} path does not exist: {document.source_path}")
                    continue
                actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
                if document.source_hash and document.source_hash != actual_hash:
                    result.errors.append(f"source document {document.document_id} source_hash mismatch")
        if document.status == SourceDocumentStatus.TOPIC_MAP_APPROVED:
            if not document.reviewed_at or not document.reviewer_id:
                result.errors.append(f"source document {document.document_id} is topic_map_approved without reviewer metadata")

    for scope in registry.list_scopes():
        if require_planned_scope_sources and not scope.source_documents:
            result.errors.append(f"scope {scope.scope_id} does not reference a source document")
            continue
        missing = [document_id for document_id in scope.source_documents if document_id not in by_id]
        if missing:
            result.errors.append(f"scope {scope.scope_id} references unknown source documents: {missing}")
            continue
        documents = [by_id[document_id] for document_id in scope.source_documents]
        has_approved_source = any(document.status == SourceDocumentStatus.TOPIC_MAP_APPROVED for document in documents)
        scope_generation_ready = bool(scope.topic_map_path and scope.caps_refs and has_approved_source)
        if scope_generation_ready:
            result.generation_ready_scope_ids.append(scope.scope_id)
        if scope.status == ContentScopeStatus.ACTIVE and not has_approved_source:
            result.errors.append(f"active scope {scope.scope_id} has no topic_map_approved source document")
        elif (
            scope_generation_ready
            and scope.status not in {ContentScopeStatus.ACTIVE, ContentScopeStatus.GENERATING, ContentScopeStatus.REVIEW}
        ):
            result.warnings.append(f"scope {scope.scope_id} has approved source material but is not in a generation-ready status")

    return result


def generation_ready(scope_id: str, *, registry: ContentScopeRegistry | None = None, manifest_path: Path = MANIFEST_PATH) -> bool:
    registry = registry or ContentScopeRegistry()
    manifest = load_manifest(manifest_path)
    by_id = {document.document_id: document for document in manifest.documents}
    scope = registry.get_scope(scope_id)
    if not scope.topic_map_path or not scope.caps_refs:
        return False
    documents = [by_id.get(document_id) for document_id in scope.source_documents]
    return any(document is not None and document.status == SourceDocumentStatus.TOPIC_MAP_APPROVED for document in documents)


def print_result(result: SourceManifestValidationResult) -> None:
    print("Source document manifest validation")
    print(f"  generation-ready scopes: {result.generation_ready_scope_ids}")
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    if result.errors:
        print("Failures:")
        for error in result.errors:
            print(f"  - {error}")
    else:
        print("  status: ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--verify-local-files", action="store_true", help="Verify ignored local source files exist and match hashes.")
    args = parser.parse_args()

    result = validate_source_manifest(verify_local_files=args.verify_local_files)
    if args.json:
        print(json.dumps({
            "passed": result.passed,
            "generation_ready_scope_ids": result.generation_ready_scope_ids,
            "warnings": result.warnings,
            "errors": result.errors,
        }, indent=2, ensure_ascii=False))
    else:
        print_result(result)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
