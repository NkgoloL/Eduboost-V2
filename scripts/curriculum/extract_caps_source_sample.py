#!/usr/bin/env python3
"""Create a bounded Gate 2R.0 extraction-feasibility sample for one CAPS source."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.curriculum.validate_source_manifest import load_manifest, validate_source_manifest


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _formula_or_table_warnings(text: str) -> list[str]:
    warnings: list[str] = []
    if re.search(r"\d+\s*[+\-x×÷/]\s*\d+", text):
        warnings.append("formula_or_arithmetic_expression_detected")
    lines = [line for line in text.splitlines() if line.strip()]
    aligned = sum(1 for line in lines if len(re.split(r"\s{2,}", line.strip())) >= 3)
    if aligned >= 3:
        warnings.append("possible_table_or_aligned_columns_detected")
    if not text.strip():
        warnings.append("no_extractable_text")
    return warnings


def build_sample(document_id: str, *, start_page: int, page_count: int) -> dict[str, Any]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - environment guard
        raise RuntimeError("pypdf is required for extraction sampling") from exc

    validation = validate_source_manifest()
    manifest = load_manifest()
    documents = {document.document_id: document for document in manifest.documents}
    document = documents.get(document_id)
    if document is None:
        raise KeyError(f"unknown source document: {document_id}")
    if not document.source_path:
        raise ValueError(f"{document_id} has no source_path")

    source_path = ROOT / document.source_path
    reader = PdfReader(str(source_path))
    actual_hash = sha256_file(source_path)
    expected_hash = document.source_sha256 or document.source_hash
    pages: list[dict[str, Any]] = []
    sample_warnings: list[str] = []
    for page_number in range(start_page, min(start_page + page_count, len(reader.pages) + 1)):
        text = reader.pages[page_number - 1].extract_text() or ""
        page_warnings = _formula_or_table_warnings(text)
        sample_warnings.extend(f"page_{page_number}:{warning}" for warning in page_warnings)
        pages.append(
            {
                "page_number": page_number,
                "char_count": len(text),
                "text_sha256": sha256_text(text),
                "warnings": page_warnings,
            }
        )

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "passed": validation.passed and actual_hash == expected_hash and bool(pages),
        "document_id": document.document_id,
        "title": document.title,
        "authority_category": "Tier 1 official curriculum source",
        "canonical_source_url": document.canonical_source_url,
        "rights_scope": [
            "acquisition_for_controlled_review",
            "secure_storage",
            "bounded_extraction_test",
        ],
        "rights_exclusions": [
            "embeddings",
            "production_retrieval",
            "derivative_generation",
            "translation",
            "redistribution",
            "commercial_use",
        ],
        "source_path": document.source_path,
        "object_store_uri": document.object_store_uri,
        "original_sha256": actual_hash,
        "manifest_sha256": expected_hash,
        "hash_verified": actual_hash == expected_hash,
        "extraction_engine": "pypdf",
        "extraction_engine_identity": getattr(sys.modules.get("pypdf"), "__version__", "unknown"),
        "bounded_sample": {
            "start_page": start_page,
            "page_count": len(pages),
            "pages": pages,
            "warnings": sample_warnings,
        },
        "controls": {
            "corpus_activation_created": False,
            "production_retrieval_membership_created": False,
            "generated_or_published_lesson_created": False,
        },
        "validation_errors": validation.errors,
        "validation_warnings": validation.warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document-id", default="caps_intermediate_phase_mathematics_grade4_6")
    parser.add_argument("--start-page", type=int, default=40)
    parser.add_argument("--page-count", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = build_sample(args.document_id, start_page=args.start_page, page_count=args.page_count)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Extraction sample for {payload['document_id']}: {'PASS' if payload['passed'] else 'FAIL'}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
