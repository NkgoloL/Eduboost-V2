#!/usr/bin/env python3
"""Run Gate 2R.3 extraction for the controlled Phase 2R source slice.

Outputs are written to ignored local staging under var/ by default. The script
is evidence-friendly: it verifies the source checksum, emits page/section/chunk
metadata, and does not create corpus mappings or retrieval memberships.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.extraction import StructuredTextExtractor, validate_extraction_result

MANIFEST = ROOT / "data" / "caps" / "source_documents" / "manifest.json"
TARGET_DOCUMENT_ID = "caps_intermediate_phase_mathematics_grade4_6"
DEFAULT_OUTPUT_ROOT = ROOT / "var" / "phase02r" / "gate2r3" / "extractions"


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def manifest_document(document_id: str) -> dict[str, Any]:
    for document in read_manifest().get("documents", []):
        if document.get("document_id") == document_id:
            return document
    raise RuntimeError(f"{document_id} is missing from {MANIFEST.relative_to(ROOT)}")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def run_extraction(
    *,
    document_id: str,
    language: str,
    output_root: Path,
    max_pages: int | None,
    dry_run: bool,
) -> dict[str, Any]:
    document = manifest_document(document_id)
    source_rel = document.get("source_path")
    expected_sha = document.get("source_sha256") or document.get("source_hash")
    if not source_rel or not expected_sha:
        raise RuntimeError("manifest document lacks source_path or source_sha256")
    source_path = ROOT / source_rel
    if not source_path.is_file():
        raise RuntimeError(f"source PDF is missing: {source_rel}")
    actual_sha = sha256_file(source_path)
    if actual_sha != expected_sha:
        raise RuntimeError(f"source checksum mismatch: expected {expected_sha}, got {actual_sha}")

    extractor = StructuredTextExtractor(max_chunk_chars=1400, min_chunk_chars=80)
    result = extractor.extract_pdf(source_path, language=language, max_pages=max_pages)
    validation_errors = validate_extraction_result(result)
    output_dir = output_root / document_id
    payload = {
        "schema_version": "1.0",
        "gate": "2R.3",
        "generated_at": now_utc(),
        "document_id": document_id,
        "source_path": source_rel,
        "source_sha256": actual_sha,
        "language": language,
        "dry_run": dry_run,
        "extraction_mode": result.extraction_mode,
        "extractor_name": result.extractor_name,
        "extractor_version": result.extractor_version,
        "quality_score": result.quality_score,
        "text_sha256": result.text_sha256,
        "page_count": len(result.pages),
        "section_count": len(result.sections),
        "chunk_count": len(result.chunks),
        "warnings": result.warnings,
        "validation_errors": validation_errors,
        "passed": not validation_errors,
        "outputs": {
            "manifest": str((output_dir / "extraction_manifest.json").relative_to(ROOT)),
            "pages": str((output_dir / "pages.jsonl").relative_to(ROOT)),
            "sections": str((output_dir / "sections.jsonl").relative_to(ROOT)),
            "chunks": str((output_dir / "chunks.jsonl").relative_to(ROOT)),
        },
        "controls": {
            "corpus_membership_created": False,
            "retrieval_projection_updated": False,
            "mapping_approved": False,
            "gate_2r4_authorised": False,
        },
    }
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_json(output_dir / "extraction_manifest.json", payload)
        (output_dir / "pages.jsonl").write_text("\n".join(json.dumps(asdict(page), ensure_ascii=False, sort_keys=True) for page in result.pages) + "\n", encoding="utf-8")
        (output_dir / "sections.jsonl").write_text("\n".join(json.dumps(asdict(section), ensure_ascii=False, sort_keys=True) for section in result.sections) + "\n", encoding="utf-8")
        (output_dir / "chunks.jsonl").write_text("\n".join(json.dumps(asdict(chunk), ensure_ascii=False, sort_keys=True) for chunk in result.chunks) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document-id", default=TARGET_DOCUMENT_ID)
    parser.add_argument("--language", default="en", choices=["en", "af", "nso"])
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = run_extraction(
        document_id=args.document_id,
        language=args.language,
        output_root=Path(args.output_root),
        max_pages=args.max_pages,
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Gate 2R.3 extraction {'passed' if payload['passed'] else 'failed'} for {payload['document_id']}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
