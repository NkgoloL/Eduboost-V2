#!/usr/bin/env python3
"""Upload downloaded CAPS sources to Azure Blob Storage and stamp object URIs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.content_source import SourceDocumentStatus
from scripts.curriculum.validate_source_manifest import MANIFEST_PATH, validate_source_manifest


def slug(value: str | None) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", (value or "unknown").lower()).strip("-")
    return cleaned or "unknown"


def primary_subject(document: dict[str, Any]) -> str:
    subjects = document.get("subjects") or []
    return str(subjects[0]) if subjects else "unknown"


def document_hash(document: dict[str, Any]) -> str | None:
    return document.get("source_sha256") or document.get("source_hash")


def blob_name(document: dict[str, Any]) -> str:
    checksum = document_hash(document)
    if not checksum:
        raise ValueError(f"{document['document_id']} has no source SHA-256")
    phase = slug(document.get("phase"))
    subject = slug(primary_subject(document))
    language = slug((document.get("languages") or ["unknown"])[0])
    return f"{phase}/{subject}/{language}/{document['document_id']}-{checksum[:16]}.pdf"


def object_store_uri(storage_account: str, container: str, blob: str) -> str:
    encoded_blob = "/".join(quote(part) for part in blob.split("/"))
    return f"https://{storage_account}.blob.core.windows.net/{container}/{encoded_blob}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_az(args: list[str]) -> None:
    subprocess.run(["az", *args], check=True)


def upload_document(
    document: dict[str, Any],
    *,
    storage_account: str,
    container: str,
    dry_run: bool,
    auth_mode: str,
) -> dict[str, Any]:
    status = document.get("status")
    if status not in {SourceDocumentStatus.SOURCE_LOADED.value, SourceDocumentStatus.TOPIC_MAP_APPROVED.value}:
        raise ValueError(f"{document['document_id']} is not source_loaded/topic_map_approved")
    source_path = document.get("source_path")
    checksum = document_hash(document)
    if not source_path or not checksum:
        raise ValueError(f"{document['document_id']} is missing source_path or source hash")
    absolute_path = ROOT / source_path
    if not absolute_path.exists():
        raise FileNotFoundError(f"{document['document_id']} source file missing: {source_path}")
    actual_hash = sha256_file(absolute_path)
    if actual_hash != checksum:
        raise ValueError(f"{document['document_id']} source hash mismatch before upload")

    blob = blob_name(document)
    uri = object_store_uri(storage_account, container, blob)
    if not dry_run:
        run_az([
            "storage", "blob", "upload",
            "--account-name", storage_account,
            "--container-name", container,
            "--name", blob,
            "--file", str(absolute_path),
            "--auth-mode", auth_mode,
            "--overwrite", "true",
            "--metadata",
            f"document_id={document['document_id']}",
            f"sha256={checksum}",
            f"curriculum={slug(document.get('curriculum'))}",
            f"phase={slug(document.get('phase'))}",
        ])
    return {
        "document_id": document["document_id"],
        "blob_name": blob,
        "object_store_uri": uri,
        "source_sha256": checksum,
        "uploaded": not dry_run,
    }


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def write_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage-account", required=True, help="Azure Storage account name.")
    parser.add_argument("--container", default="caps-sources", help="Azure Blob container name.")
    parser.add_argument("--auth-mode", choices=["login", "key"], default="login", help="Azure Storage auth mode for uploads.")
    parser.add_argument("--create-container", action="store_true", help="Create the container before uploading.")
    parser.add_argument("--commit", action="store_true", help="Upload files and update manifest object_store_uri values.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    manifest = load_manifest()
    errors: list[str] = []
    uploads: list[dict[str, Any]] = []

    if args.commit and args.create_container:
        try:
            run_az([
                "storage", "container", "create",
                "--account-name", args.storage_account,
                "--name", args.container,
                "--auth-mode", args.auth_mode,
            ])
        except subprocess.CalledProcessError as exc:
            errors.append(f"container create failed: {exc}")

    documents_by_id = {document["document_id"]: document for document in manifest["documents"]}
    if not errors:
        for document in manifest["documents"]:
            try:
                upload = upload_document(
                    document,
                    storage_account=args.storage_account,
                    container=args.container,
                    dry_run=not args.commit,
                    auth_mode=args.auth_mode,
                )
            except Exception as exc:
                errors.append(f"{document.get('document_id')}: {exc}")
                continue
            uploads.append(upload)
            if args.commit:
                documents_by_id[upload["document_id"]]["object_store_uri"] = upload["object_store_uri"]

    validation_payload: dict[str, Any] | None = None
    if args.commit and not errors:
        write_manifest(manifest)
        validation = validate_source_manifest()
        validation_payload = {
            "passed": validation.passed,
            "errors": validation.errors,
            "generation_ready_scope_ids": validation.generation_ready_scope_ids,
        }
        if not validation.passed:
            errors.extend(validation.errors)

    payload = {
        "storage_account": args.storage_account,
        "container": args.container,
        "commit": args.commit,
        "auth_mode": args.auth_mode,
        "uploadable_documents": len(uploads),
        "errors": errors,
        "uploads": uploads,
        "validation": validation_payload,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"CAPS source uploads: {len(uploads)} documents")
        for error in errors:
            print(f"  error: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
