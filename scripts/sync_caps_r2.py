#!/usr/bin/env python3
"""Sync curated CAPS training assets between local disk and Cloudflare R2."""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit, urlunsplit

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOCAL_DIR = PROJECT_ROOT / "data" / "caps"
DEFAULT_PREFIX = "training-data/caps-curated"
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


def parse_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value


def load_env_file(path: Path, override: bool = False) -> dict[str, str]:
    loaded: dict[str, str] = {}
    if not path.exists():
        return loaded
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "").isalnum():
            continue
        parsed = parse_env_value(value)
        loaded[key] = parsed
        if override or key not in os.environ:
            os.environ[key] = parsed
    return loaded



@dataclass(frozen=True)
class SyncItem:
    local_path: Path
    key: str


def iter_local_items(local_dir: Path, prefix: str) -> list[SyncItem]:
    items = []
    for path in sorted(local_dir.rglob("*")):
        if path.is_file():
            rel = path.relative_to(local_dir).as_posix()
            items.append(SyncItem(path, f"{prefix.rstrip('/')}/{rel}"))
    return items



def normalise_r2_endpoint(endpoint_url: str) -> str:
    parts = urlsplit(endpoint_url.strip())
    if not parts.scheme or not parts.netloc:
        return endpoint_url.strip().rstrip("/")
    return urlunsplit((parts.scheme, parts.netloc, "", "", ""))


def create_r2_client(env_file: Path = DEFAULT_ENV_FILE) -> object:
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("boto3 is required for R2 sync") from exc

    load_env_file(env_file)
    required = ["R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing R2 environment variables: {', '.join(missing)}")
    return boto3.client(
        "s3",
        endpoint_url=normalise_r2_endpoint(os.environ["R2_ENDPOINT_URL"]),
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name=os.getenv("R2_REGION", "auto"),
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def upload_items(client: object, bucket: str, items: Iterable[SyncItem], dry_run: bool) -> list[dict[str, str]]:
    synced = []
    for item in items:
        synced.append({"local_path": str(item.local_path), "key": item.key})
        if not dry_run:
            content_type = mimetypes.guess_type(item.local_path.name)[0] or "application/octet-stream"
            client.upload_file(str(item.local_path), bucket, item.key, ExtraArgs={"ContentType": content_type})
    return synced


def download_prefix(client: object, bucket: str, local_dir: Path, prefix: str, dry_run: bool) -> list[dict[str, str]]:
    paginator = client.get_paginator("list_objects_v2")
    synced = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix.rstrip("/") + "/"):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            rel = key.removeprefix(prefix.rstrip("/") + "/")
            if not rel:
                continue
            local_path = local_dir / rel
            synced.append({"local_path": str(local_path), "key": key})
            if not dry_run:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                client.download_file(bucket, key, str(local_path))
    return synced


def run(args: argparse.Namespace) -> int:
    local_dir = Path(args.local_dir).resolve()
    prefix = args.prefix.strip("/")
    if args.direction == "upload":
        items = iter_local_items(local_dir, prefix)
        if args.dry_run:
            synced = [{"local_path": str(item.local_path), "key": item.key} for item in items]
        else:
            client = create_r2_client(Path(args.env_file).resolve())
            synced = upload_items(client, os.environ["R2_BUCKET_NAME"], items, dry_run=False)
    else:
        client = create_r2_client(Path(args.env_file).resolve())
        synced = download_prefix(client, os.environ["R2_BUCKET_NAME"], local_dir, prefix, args.dry_run)

    print(json.dumps({"direction": args.direction, "count": len(synced), "items": synced}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sync CAPS curated data with Cloudflare R2.")
    parser.add_argument("--direction", choices=["upload", "download"], default="upload")
    parser.add_argument("--local-dir", default=str(DEFAULT_LOCAL_DIR))
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="Local .env file to load R2 credentials from.")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    return run(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
