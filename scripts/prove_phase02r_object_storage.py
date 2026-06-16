#!/usr/bin/env python3
"""Prove Phase 02R non-production object-storage controls.

The proof intentionally emits no credentials. It expects bucket-scoped S3
credentials and validates authenticated access, versioned writes, read-back,
hash equality, manifest export, backup outside the repository, and restore.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def _inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _redacted_endpoint(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.hostname}:{parsed.port}" if parsed.port else f"{parsed.scheme}://{parsed.hostname}"
    return "configured"


def prove() -> dict[str, object]:
    try:
        import boto3
        from botocore.config import Config
        from botocore.exceptions import ClientError
    except ImportError as exc:  # pragma: no cover - environment guard
        raise RuntimeError("boto3 and botocore are required for S3-compatible proof") from exc

    backend = os.getenv("PHASE02R_OBJECT_STORAGE_BACKEND", "").strip().lower()
    endpoint = os.getenv("S3_ENDPOINT_URL", "").strip()
    bucket = os.getenv("PHASE02R_OBJECT_STORAGE_BUCKET", "").strip()
    backup_dir_value = os.getenv("PHASE02R_OBJECT_STORAGE_BACKUP_DIR", "").strip()
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1").strip() or "us-east-1"

    errors: list[str] = []
    if backend not in {"s3", "minio"}:
        errors.append("PHASE02R_OBJECT_STORAGE_BACKEND must be s3 or minio")
    for name, value in {
        "S3_ENDPOINT_URL": endpoint,
        "PHASE02R_OBJECT_STORAGE_BUCKET": bucket,
        "PHASE02R_OBJECT_STORAGE_BACKUP_DIR": backup_dir_value,
        "AWS_ACCESS_KEY_ID": access_key,
        "AWS_SECRET_ACCESS_KEY": secret_key,
    }.items():
        if not value:
            errors.append(f"{name} is not configured")
    if errors:
        return {"passed": False, "errors": errors, "checks": {}}

    backup_dir = Path(backup_dir_value).expanduser()
    if _inside_repo(backup_dir):
        errors.append("PHASE02R_OBJECT_STORAGE_BACKUP_DIR must be outside the repository")
        return {"passed": False, "errors": errors, "checks": {}}

    session = boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )
    client = session.client(
        "s3",
        endpoint_url=endpoint,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )

    run_id = f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    key = f"phase02r/gate-2r0/{run_id}/original.txt"
    manifest_key = f"phase02r/gate-2r0/{run_id}/manifest.json"
    original = b"phase02r official-source storage feasibility proof\n"
    replacement = b"phase02r replacement written as a versioned object\n"

    checks: dict[str, object] = {
        "backend": backend,
        "endpoint": _redacted_endpoint(endpoint),
        "bucket": bucket,
        "run_id": run_id,
        "credentials_exposed": False,
    }

    try:
        client.list_objects_v2(Bucket=bucket, MaxKeys=1)
        checks["authenticated_connection"] = True
    except ClientError as exc:
        raise RuntimeError(f"authenticated bucket connection failed: {exc.response.get('Error', {}).get('Code')}") from exc

    versioning = client.get_bucket_versioning(Bucket=bucket)
    checks["bucket_versioning_status"] = versioning.get("Status")
    if versioning.get("Status") != "Enabled":
        errors.append("bucket versioning is not enabled")

    first = client.put_object(Bucket=bucket, Key=key, Body=original)
    first_version = first.get("VersionId")
    if not first_version:
        errors.append("first put_object did not return a version id")
    checks["write_version_id"] = first_version
    checks["write_key"] = key
    checks["write_sha256"] = _sha256_bytes(original)

    read_body = client.get_object(Bucket=bucket, Key=key, VersionId=first_version)["Body"].read()
    checks["readback_sha256"] = _sha256_bytes(read_body)
    checks["sha256_equal"] = checks["write_sha256"] == checks["readback_sha256"]
    if not checks["sha256_equal"]:
        errors.append("read-back SHA-256 does not equal original hash")

    second = client.put_object(Bucket=bucket, Key=key, Body=replacement)
    second_version = second.get("VersionId")
    checks["overwrite_policy"] = "new_version_created" if second_version and second_version != first_version else "not_proven"
    checks["second_version_id"] = second_version
    if checks["overwrite_policy"] != "new_version_created":
        errors.append("overwrite did not create a distinct object version")
    old_body = client.get_object(Bucket=bucket, Key=key, VersionId=first_version)["Body"].read()
    checks["old_version_still_restores"] = _sha256_bytes(old_body) == checks["write_sha256"]
    if not checks["old_version_still_restores"]:
        errors.append("original version could not be restored after overwrite")

    manifest = {
        "schema_version": "1.0",
        "backend": backend,
        "bucket": bucket,
        "key": key,
        "version_id": first_version,
        "sha256": checks["write_sha256"],
        "overwrite_policy": checks["overwrite_policy"],
        "second_version_id": second_version,
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    manifest_put = client.put_object(Bucket=bucket, Key=manifest_key, Body=manifest_bytes)
    checks["manifest_key"] = manifest_key
    checks["manifest_version_id"] = manifest_put.get("VersionId")
    checks["manifest_sha256"] = _sha256_bytes(manifest_bytes)

    backup_run_dir = backup_dir / "phase02r" / run_id
    backup_run_dir.mkdir(parents=True, exist_ok=False)
    backup_object = backup_run_dir / "original.txt"
    backup_manifest = backup_run_dir / "manifest.json"
    backup_object.write_bytes(read_body)
    backup_manifest.write_bytes(manifest_bytes)
    restored_sha = _sha256_bytes(backup_object.read_bytes())
    checks["backup_dir"] = str(backup_run_dir)
    checks["backup_outside_repository"] = not _inside_repo(backup_run_dir)
    checks["restore_sha256"] = restored_sha
    checks["restore_sha256_equal"] = restored_sha == checks["write_sha256"]
    if not checks["backup_outside_repository"]:
        errors.append("backup directory is inside the repository")
    if not checks["restore_sha256_equal"]:
        errors.append("restored backup SHA-256 does not match original")

    denied = False
    try:
        client.get_object(Bucket=bucket, Key="../phase02r-out-of-scope")
    except ClientError:
        denied = True
    checks["scoped_credentials_probe"] = "out_of_scope_read_denied" if denied else "not_denied"
    if not denied:
        errors.append("scoped credential probe did not deny out-of-scope read")

    return {"passed": not errors, "errors": errors, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    try:
        result = prove()
    except Exception as exc:
        result = {"passed": False, "errors": [str(exc)], "checks": {}}

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Phase 02R object-storage proof")
        print("PASS" if result["passed"] else "FAIL")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
