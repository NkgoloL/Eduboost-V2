#!/usr/bin/env python3
"""Extract text from downloaded CAPS PDFs into ignored local staging."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.curriculum.validate_source_manifest import load_manifest, validate_source_manifest

TEXT_DIR = ROOT / "data" / "caps" / "source_documents" / "text"
TEXT_EXTRACT_MANIFEST_PATH = ROOT / "data" / "content_factory" / "source_text_extracts_manifest.json"


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def text_extract_path(document_id: str, *, text_dir: Path = TEXT_DIR) -> Path:
    return text_dir / f"{document_id}.txt"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def extract_pdf_text(path: Path) -> tuple[str, int]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - environment guard
        raise RuntimeError("pypdf is required; install requirements/base.txt") from exc

    reader = PdfReader(str(path))
    page_text: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        page_text.append(f"\n\n--- page {page_number} ---\n{text.strip()}")
    return "".join(page_text).strip() + "\n", len(reader.pages)


def build_extract_record(document: Any, *, commit: bool) -> dict[str, Any] | None:
    source_path = getattr(document, "source_path", None)
    checksum = getattr(document, "source_sha256", None) or getattr(document, "source_hash", None)
    if not source_path or not checksum:
        return None
    absolute_source_path = ROOT / source_path
    if not absolute_source_path.exists():
        raise FileNotFoundError(f"{document.document_id} source file missing: {source_path}")

    text, page_count = extract_pdf_text(absolute_source_path)
    target = text_extract_path(document.document_id)
    text_hash = sha256_text(text)
    if commit:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return {
        "document_id": document.document_id,
        "source_path": source_path,
        "source_sha256": checksum,
        "text_extract_path": str(target.relative_to(ROOT)),
        "text_sha256": text_hash,
        "page_count": page_count,
        "char_count": len(text),
        "extracted_at": now_utc(),
    }


def build_extract_manifest(*, commit: bool) -> dict[str, Any]:
    validation = validate_source_manifest()
    manifest = load_manifest()
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for document in manifest.documents:
        try:
            record = build_extract_record(document, commit=commit)
        except Exception as exc:
            errors.append(f"{document.document_id}: {exc}")
            continue
        if record:
            records.append(record)

    payload = {
        "schema_version": "1.0",
        "validation_passed": validation.passed,
        "validation_errors": validation.errors,
        "documents_extracted": len(records),
        "errors": errors,
        "records": sorted(records, key=lambda item: item["document_id"]),
    }
    if commit and not errors:
        TEXT_EXTRACT_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        TEXT_EXTRACT_MANIFEST_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="Write text files and extraction manifest.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    payload = build_extract_manifest(commit=args.commit)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"CAPS text extracts: {payload['documents_extracted']} documents")
        for error in payload["errors"]:
            print(f"  error: {error}")
    return 1 if payload["errors"] or not payload["validation_passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
