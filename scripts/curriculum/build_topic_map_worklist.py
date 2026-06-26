#!/usr/bin/env python3
"""Build the outstanding CAPS topic-map implementation worklist."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.content_source import SourceDocumentStatus
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.validate_source_manifest import generation_ready, load_manifest, validate_source_manifest

DEFAULT_WORKLIST_PATH = ROOT / "data" / "content_factory" / "topic_map_worklist.json"
TEXT_EXTRACT_MANIFEST_PATH = ROOT / "data" / "content_factory" / "source_text_extracts_manifest.json"


@dataclass
class TopicMapWorkItem:
    scope_id: str
    grade: int
    phase: str | None
    subject: str
    subject_code: str
    language: str
    topic_map_path: str | None
    suggested_topic_map_path: str
    caps_refs_count: int
    source_document_ids: list[str]
    source_paths: list[str]
    source_sha256: list[str]
    canonical_source_urls: list[str]
    object_store_uris: list[str]
    text_extract_paths: list[str]
    text_sha256: list[str]
    generation_ready: bool
    outstanding_tasks: list[str]


@dataclass
class TopicMapWorklist:
    schema_version: str
    validation_passed: bool
    validation_errors: list[str]
    summary: dict[str, int]
    items: list[TopicMapWorkItem]


def _document_hash(document: Any) -> str | None:
    return getattr(document, "source_sha256", None) or getattr(document, "source_hash", None)


def _suggested_topic_map_path(scope_id: str) -> str:
    return f"data/caps/topic_maps/{scope_id}.json"


def _source_loaded(document: Any | None) -> bool:
    return bool(
        document
        and document.status in {SourceDocumentStatus.SOURCE_LOADED, SourceDocumentStatus.TOPIC_MAP_APPROVED}
        and getattr(document, "source_path", None)
        and _document_hash(document)
    )


def _outstanding_tasks(scope: Any, documents: list[Any | None], *, ready: bool) -> list[str]:
    tasks: list[str] = []
    if not documents or any(document is None for document in documents):
        tasks.append("resolve_source_document")
        return tasks
    if any(not _source_loaded(document) for document in documents):
        tasks.append("load_source_pdf_and_sha256")
    if any(not getattr(document, "object_store_uri", None) for document in documents):
        tasks.append("upload_source_pdf_to_object_store")
    topic_path = getattr(scope, "topic_map_path", None)
    if not topic_path or not (ROOT / topic_path).exists():
        tasks.append("extract_topic_map")
    if not getattr(scope, "caps_refs", None):
        tasks.append("approve_scope_caps_refs")
    if any(document.status != SourceDocumentStatus.TOPIC_MAP_APPROVED for document in documents if document is not None):
        tasks.append("approve_topic_map")
    if not ready and "activate_scope" not in tasks:
        tasks.append("activate_scope")
    return tasks


def _load_text_extract_records() -> dict[str, dict[str, Any]]:
    if not TEXT_EXTRACT_MANIFEST_PATH.exists():
        return {}
    payload = json.loads(TEXT_EXTRACT_MANIFEST_PATH.read_text(encoding="utf-8"))
    return {record["document_id"]: record for record in payload.get("records", [])}


def build_worklist() -> dict[str, Any]:
    registry = ContentScopeRegistry()
    manifest = load_manifest()
    validation = validate_source_manifest(registry=registry)
    documents_by_id = {document.document_id: document for document in manifest.documents}
    text_extracts_by_id = _load_text_extract_records()
    items: list[TopicMapWorkItem] = []
    task_counter: Counter[str] = Counter()

    for scope in registry.list_scopes():
        ready = generation_ready(scope.scope_id, registry=registry)
        documents = [documents_by_id.get(document_id) for document_id in scope.source_documents]
        tasks = _outstanding_tasks(scope, documents, ready=ready)
        task_counter.update(tasks)
        text_extracts = [
            text_extracts_by_id.get(document.document_id)
            for document in documents
            if document is not None
        ]
        items.append(
            TopicMapWorkItem(
                scope_id=scope.scope_id,
                grade=scope.grade,
                phase=scope.phase,
                subject=scope.subject,
                subject_code=scope.subject_code,
                language=scope.language,
                topic_map_path=scope.topic_map_path,
                suggested_topic_map_path=_suggested_topic_map_path(scope.scope_id),
                caps_refs_count=len(scope.caps_refs),
                source_document_ids=[document.document_id for document in documents if document is not None],
                source_paths=[document.source_path for document in documents if document is not None and document.source_path],
                source_sha256=[_document_hash(document) for document in documents if document is not None and _document_hash(document)],
                canonical_source_urls=[document.canonical_source_url for document in documents if document is not None and document.canonical_source_url],
                object_store_uris=[document.object_store_uri for document in documents if document is not None and document.object_store_uri],
                text_extract_paths=[record["text_extract_path"] for record in text_extracts if record and record.get("text_extract_path")],
                text_sha256=[
                    record["text_sha256"] if record and record.get("text_sha256") else _document_hash(document)
                    for document, record in zip(documents, text_extracts, strict=False)
                    if document is not None and ((record and record.get("text_sha256")) or _document_hash(document))
                ],
                generation_ready=ready,
                outstanding_tasks=tasks,
            )
        )

    summary = {
        "scopes_total": len(items),
        "scopes_generation_ready": sum(1 for item in items if item.generation_ready),
        "scopes_needing_topic_map": sum(1 for item in items if "extract_topic_map" in item.outstanding_tasks),
        "source_documents_distinct": len({doc_id for item in items for doc_id in item.source_document_ids}),
        **{f"tasks.{task}": count for task, count in sorted(task_counter.items())},
    }
    worklist = TopicMapWorklist(
        schema_version="1.0",
        validation_passed=validation.passed,
        validation_errors=validation.errors,
        summary=summary,
        items=items,
    )
    return {
        "schema_version": worklist.schema_version,
        "validation_passed": worklist.validation_passed,
        "validation_errors": worklist.validation_errors,
        "summary": worklist.summary,
        "items": [asdict(item) for item in worklist.items],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit worklist JSON to stdout.")
    parser.add_argument("--write", nargs="?", const=str(DEFAULT_WORKLIST_PATH), help="Write the worklist JSON to a path.")
    args = parser.parse_args()

    worklist = build_worklist()
    if args.write:
        path = Path(args.write)
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(worklist, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json or not args.write:
        print(json.dumps(worklist, indent=2, ensure_ascii=False))
    return 0 if worklist["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
