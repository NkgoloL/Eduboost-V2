#!/usr/bin/env python3
"""Acquire Phase 2R Gate 2R.2 source originals into immutable local storage."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.acquisition import AcquisitionPolicy, ControlledAcquisitionService  # noqa: E402
from app.services.curriculum.object_storage import LocalImmutableObjectStore  # noqa: E402

MANIFEST = ROOT / "data" / "caps" / "source_documents" / "manifest.json"
TARGET_DOCUMENT_ID = "caps_intermediate_phase_mathematics_grade4_6"
USER_AGENT = "Eduboost-Phase02R-Gate2R2-acquisition/1.0"


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def target_document(manifest: dict[str, Any]) -> dict[str, Any]:
    for doc in manifest.get("documents", []):
        if doc.get("document_id") == TARGET_DOCUMENT_ID:
            return doc
    raise RuntimeError(f"{TARGET_DOCUMENT_ID} missing from {MANIFEST}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_pdf(url: str, target: Path, *, max_bytes: int) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    total = 0
    tmp = target.with_suffix(target.suffix + ".part")
    try:
        with urlopen(request, timeout=90) as response, tmp.open("wb") as handle:  # noqa: S310 - approved manifest URL only  # nosec B310
            first = response.read(5)
            total += len(first)
            if first != b"%PDF-":
                raise RuntimeError("downloaded source is not a PDF")
            handle.write(first)
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise RuntimeError("downloaded source exceeds maximum allowed size")
                handle.write(chunk)
        tmp.replace(target)
        return total
    finally:
        if tmp.exists():
            tmp.unlink()


def planned_uri(expected_sha: str, source_path: Path) -> str:
    return f"local://phase02r/sources/sha256/{expected_sha[:2]}/{expected_sha}{source_path.suffix.lower()}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--all-located", action="store_true")
    parser.add_argument("--source-version-id")
    parser.add_argument("--download-missing", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--object-store-root", default="var/object-store/phase02r/sources")
    parser.add_argument("--max-file-size-bytes", type=int, default=50 * 1024 * 1024)
    args = parser.parse_args()

    manifest = load_manifest()
    doc = target_document(manifest)
    source_path = ROOT / doc["source_path"]
    expected_sha = doc.get("source_sha256") or doc.get("source_hash")
    if not expected_sha:
        raise RuntimeError("source manifest has no expected SHA-256")

    result: dict[str, Any] = {
        "gate": "2R.2",
        "target_document_id": TARGET_DOCUMENT_ID,
        "source_path": str(source_path.relative_to(ROOT)),
        "expected_sha256": expected_sha,
        "dry_run": args.dry_run,
        "source_version_id": args.source_version_id,
        "planned_object_uri": planned_uri(expected_sha, source_path),
    }

    if not source_path.is_file():
        if args.download_missing and not args.dry_run:
            url = doc.get("canonical_source_url") or doc.get("object_store_uri")
            if not url:
                raise RuntimeError("source file missing and manifest has no approved download URL")
            bytes_downloaded = download_pdf(str(url), source_path, max_bytes=args.max_file_size_bytes)
            result["downloaded_missing_source"] = True
            result["bytes_downloaded"] = bytes_downloaded
        else:
            result.update({"source_available": False, "eligible": False, "reason": "source file missing"})
            if args.json:
                print(json.dumps(result, indent=2, sort_keys=True))
            else:
                print("Gate 2R.2 acquisition dry-run completed; source file missing")
            return 0 if args.dry_run else 1

    actual_sha = sha256_file(source_path)
    result.update({"source_available": True, "actual_sha256": actual_sha, "eligible": actual_sha == expected_sha})
    if args.dry_run:
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print("Gate 2R.2 acquisition dry-run completed")
        return 0

    rights_decision = {"decision_status": "approved", "may_store_original": True}
    service = ControlledAcquisitionService(
        policy=AcquisitionPolicy(max_file_size_bytes=args.max_file_size_bytes),
        object_store=LocalImmutableObjectStore(ROOT / args.object_store_root),
    )
    acquired = service.acquire_local_file(
        source_path,
        expected_sha256=expected_sha,
        rights_decision=rights_decision,
        allowed_root=ROOT / "data" / "caps" / "source_documents",
    )
    result.update({
        "acquired": True,
        "object_uri": acquired.object_uri,
        "sha256": acquired.sha256,
        "size_bytes": acquired.size_bytes,
        "media_type": acquired.media_type,
        "storage_backend": acquired.storage_backend,
        "malware_scan_status": acquired.malware_scan_status,
    })
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Gate 2R.2 acquisition passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
