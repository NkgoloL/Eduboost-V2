#!/usr/bin/env python3
"""Download official CAPS source PDFs and record their SHA-256 hashes."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.content_source import SourceDocumentStatus
from scripts.curriculum.validate_source_manifest import MANIFEST_PATH, validate_source_manifest

RAW_DIR = ROOT / "data" / "caps" / "source_documents" / "raw"
USER_AGENT = "Eduboost-CAPS-source-audit/1.0 (+https://github.com/NkgoloL/Eduboost-V2)"


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def relative_source_path(document_id: str) -> str:
    return f"data/caps/source_documents/raw/{document_id}.pdf"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(url: str, target: Path, *, timeout: int = 60) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        payload = response.read()
    if not payload.startswith(b"%PDF-"):
        preview = payload[:80].decode("utf-8", errors="replace").replace("\n", " ")
        raise RuntimeError(f"downloaded payload is not a PDF for {url}: {preview!r}")
    tmp = target.with_suffix(target.suffix + ".part")
    tmp.write_bytes(payload)
    tmp.replace(target)
    return len(payload)


def update_document(document: dict[str, Any], *, commit: bool, refresh: bool) -> dict[str, Any] | None:
    url = document.get("canonical_source_url")
    if not url or document.get("status") == SourceDocumentStatus.NOT_APPLICABLE.value:
        return None

    rel_path = relative_source_path(document["document_id"])
    target = ROOT / rel_path
    downloaded = False
    if refresh or not target.exists():
        byte_count = download_file(url, target)
        downloaded = True
    else:
        byte_count = target.stat().st_size

    checksum = sha256_file(target)
    changes: dict[str, Any] = {
        "document_id": document["document_id"],
        "source_path": rel_path,
        "source_sha256": checksum,
        "source_hash": checksum,
        "byte_count": byte_count,
        "downloaded": downloaded,
    }

    if commit:
        document["source_path"] = rel_path
        document["source_hash"] = checksum
        document["source_sha256"] = checksum
        if downloaded or not document.get("downloaded_at"):
            stamp = now_utc()
            document["downloaded_at"] = stamp
            document["retrieved_at"] = stamp
        if document.get("status") == SourceDocumentStatus.PLANNED.value:
            document["status"] = SourceDocumentStatus.SOURCE_LOADED.value
            changes["status"] = SourceDocumentStatus.SOURCE_LOADED.value
    return changes


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def write_manifest(manifest: dict[str, Any]) -> None:
    manifest["documents"] = sorted(manifest["documents"], key=lambda item: item["document_id"])
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="Update manifest after downloading files.")
    parser.add_argument("--refresh", action="store_true", help="Redownload existing raw files before hashing.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    manifest = load_manifest()
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for document in manifest["documents"]:
        try:
            result = update_document(document, commit=args.commit, refresh=args.refresh)
        except Exception as exc:  # pragma: no cover - CLI safety path
            errors.append(f"{document.get('document_id')}: {exc}")
            continue
        if result:
            results.append(result)

    if args.commit and not errors:
        write_manifest(manifest)

    validation_payload: dict[str, Any] | None = None
    if args.commit and not errors:
        validation = validate_source_manifest(verify_local_files=True)
        validation_payload = {
            "passed": validation.passed,
            "errors": validation.errors,
            "generation_ready_scope_ids": validation.generation_ready_scope_ids,
        }
        if not validation.passed:
            errors.extend(validation.errors)

    payload = {
        "downloadable_documents": len(results),
        "downloaded_documents": sum(1 for result in results if result["downloaded"]),
        "errors": errors,
        "results": results,
        "validation": validation_payload,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"CAPS source downloads: {payload['downloadable_documents']} documents, {payload['downloaded_documents']} downloaded")
        for error in errors:
            print(f"  error: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
