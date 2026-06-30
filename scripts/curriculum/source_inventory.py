#!/usr/bin/env python3
"""Report CAPS source inventory gaps for all study-material scopes."""
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


@dataclass
class InventoryRow:
    scope_id: str
    grade: int
    phase: str | None
    subject: str
    document_id: str | None
    source_status: str
    has_url: bool
    has_hash: bool
    has_object_uri: bool
    has_reviewed_topic_map: bool
    is_generation_ready: bool
    gap_reason: str


def _document_hash(document: Any) -> str | None:
    return getattr(document, "source_sha256", None) or getattr(document, "source_hash", None)


def _gap_reason(document: Any | None, *, ready: bool) -> str:
    if document is None:
        return "missing_source_document"
    status = document.status.value
    if status == SourceDocumentStatus.NOT_APPLICABLE.value:
        return "not_applicable" if getattr(document, "evidence_notes", None) else "not_applicable_missing_evidence"
    if not getattr(document, "canonical_source_url", None) and not getattr(document, "source_path", None):
        return "missing_canonical_source_url"
    if not _document_hash(document):
        return "missing_sha256"
    if not getattr(document, "object_store_uri", None) and status in {SourceDocumentStatus.SOURCE_LOADED.value, SourceDocumentStatus.TOPIC_MAP_APPROVED.value}:
        return "missing_object_store_uri"
    if not ready:
        return "not_generation_ready"
    return "ok"


def build_inventory(*, filter_status: str | None = None) -> dict[str, Any]:
    registry = ContentScopeRegistry()
    manifest = load_manifest()
    validation = validate_source_manifest(registry=registry)
    documents = {document.document_id: document for document in manifest.documents}
    rows: list[InventoryRow] = []

    for scope in registry.list_scopes():
        ready = generation_ready(scope.scope_id, registry=registry)
        source_ids = scope.source_documents or [None]
        for document_id in source_ids:
            document = documents.get(document_id) if document_id else None
            status = document.status.value if document else "missing"
            if filter_status and status != filter_status:
                continue
            rows.append(
                InventoryRow(
                    scope_id=scope.scope_id,
                    grade=scope.grade,
                    phase=scope.phase,
                    subject=scope.subject,
                    document_id=document_id,
                    source_status=status,
                    has_url=bool(document and (document.canonical_source_url or document.source_path)),
                    has_hash=bool(document and _document_hash(document)),
                    has_object_uri=bool(document and document.object_store_uri),
                    has_reviewed_topic_map=bool(document and document.status == SourceDocumentStatus.TOPIC_MAP_APPROVED),
                    is_generation_ready=ready,
                    gap_reason=_gap_reason(document, ready=ready),
                )
            )

    summary = Counter(row.gap_reason for row in rows)
    status_summary = Counter(row.source_status for row in rows)
    return {
        "schema_version": "1.0",
        "validation_passed": validation.passed,
        "validation_errors": validation.errors,
        "summary": dict(sorted(summary.items())),
        "status_summary": dict(sorted(status_summary.items())),
        "rows": [asdict(row) for row in rows],
    }


def print_report(report: dict[str, Any]) -> None:
    print("CAPS source inventory")
    print(f"  validation_passed: {report['validation_passed']}")
    for key, value in report["summary"].items():
        print(f"  gaps.{key}: {value}")
    for key, value in report["status_summary"].items():
        print(f"  statuses.{key}: {value}")
    print("\nRows")
    for row in report["rows"]:
        print(
            f"  {row['scope_id']} -> {row['document_id']} "
            f"[{row['source_status']}] ready={row['is_generation_ready']} gap={row['gap_reason']}"
        )
    if report["validation_errors"]:
        print("\nValidation errors")
        for error in report["validation_errors"]:
            print(f"  - {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--filter-status", help="Only include rows for one source status.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any row has a gap other than ok/not_applicable.")
    args = parser.parse_args()

    report = build_inventory(filter_status=args.filter_status)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_report(report)

    blocking_gaps = [
        row for row in report["rows"]
        if row["gap_reason"] not in {"ok", "not_applicable"}
    ]
    return 1 if args.strict and (blocking_gaps or not report["validation_passed"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
