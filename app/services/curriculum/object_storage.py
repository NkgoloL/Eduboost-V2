"""Immutable local object storage for Phase 2R Gate 2R.2.

This module is intentionally small and deterministic so the Gate 2R.2
implementation can be verified locally and in CI without depending on a cloud
object store.  Production adapters can keep the same contract and store objects
in a managed immutable bucket/container.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass
from pathlib import Path


class ObjectStorageRejectedError(ValueError):
    """Raised when an object cannot be safely stored."""


@dataclass(frozen=True)
class StoredObject:
    object_uri: str
    path: Path
    sha256: str
    size_bytes: int
    storage_backend: str = "local-content-addressed"


class LocalImmutableObjectStore:
    """Content-addressed immutable local object store.

    Object layout:
        <root>/sha256/<first-two-hex>/<sha256><suffix>

    The implementation writes through a temporary file and atomically promotes
    only after checksum verification.  Existing objects are reused only when
    their bytes still hash to the requested digest.
    """

    allowed_suffixes = frozenset({".pdf", ".txt", ".md", ".json"})

    def __init__(self, root: str | Path = "var/object-store/phase02r/sources") -> None:
        self.root = Path(root).resolve()

    @staticmethod
    def _validate_sha256(value: str) -> str:
        if value != value.lower() or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise ObjectStorageRejectedError("sha256 must be 64 lowercase hexadecimal characters")
        return value

    @classmethod
    def _safe_suffix(cls, suffix: str) -> str:
        suffix = suffix.lower()
        if suffix not in cls.allowed_suffixes:
            raise ObjectStorageRejectedError(f"unsupported object suffix: {suffix}")
        return suffix

    @staticmethod
    def sha256_file(path: Path, *, max_bytes: int | None = None) -> tuple[str, int]:
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                size += len(chunk)
                if max_bytes is not None and size > max_bytes:
                    raise ObjectStorageRejectedError("source object exceeds maximum allowed size")
                digest.update(chunk)
        return digest.hexdigest(), size

    def object_path(self, sha256: str, suffix: str) -> Path:
        sha256 = self._validate_sha256(sha256)
        suffix = self._safe_suffix(suffix)
        path = (self.root / "sha256" / sha256[:2] / f"{sha256}{suffix}").resolve()
        try:
            path.relative_to(self.root)
        except ValueError as exc:
            raise ObjectStorageRejectedError("resolved object path escaped storage root") from exc
        return path

    def put_file(self, source: str | Path, *, expected_sha256: str, suffix: str, max_bytes: int | None = None) -> StoredObject:
        source_path = Path(source).resolve()
        if not source_path.is_file():
            raise ObjectStorageRejectedError(f"source file does not exist: {source_path}")

        expected_sha256 = self._validate_sha256(expected_sha256)
        actual_sha, size = self.sha256_file(source_path, max_bytes=max_bytes)
        if size <= 0:
            raise ObjectStorageRejectedError("source object is empty")
        if actual_sha != expected_sha256:
            raise ObjectStorageRejectedError(f"checksum mismatch: expected {expected_sha256}, got {actual_sha}")

        target = self.object_path(actual_sha, suffix)
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists():
            existing_sha, existing_size = self.sha256_file(target, max_bytes=max_bytes)
            if existing_sha != actual_sha:
                raise ObjectStorageRejectedError("existing object path contains different bytes")
            return StoredObject(object_uri=self.to_uri(target), path=target, sha256=existing_sha, size_bytes=existing_size)

        tmp = target.with_name(f".{target.name}.{uuid.uuid4().hex}.part")
        written = 0
        try:
            with source_path.open("rb") as src, tmp.open("wb") as dst:
                for chunk in iter(lambda: src.read(1024 * 1024), b""):
                    written += len(chunk)
                    if max_bytes is not None and written > max_bytes:
                        raise ObjectStorageRejectedError("source object exceeds maximum allowed size")
                    dst.write(chunk)
            copied_sha, copied_size = self.sha256_file(tmp, max_bytes=max_bytes)
            if copied_sha != actual_sha or copied_size != size:
                raise ObjectStorageRejectedError("temporary object verification failed")
            os.replace(tmp, target)
        finally:
            if tmp.exists():
                tmp.unlink()

        final_sha, final_size = self.sha256_file(target, max_bytes=max_bytes)
        if final_sha != actual_sha or final_size != size:
            raise ObjectStorageRejectedError("stored object checksum verification failed")
        return StoredObject(object_uri=self.to_uri(target), path=target, sha256=final_sha, size_bytes=final_size)

    def to_uri(self, path: Path) -> str:
        resolved = Path(path).resolve()
        try:
            rel = resolved.relative_to(self.root)
        except ValueError as exc:
            raise ObjectStorageRejectedError("object path is outside storage root") from exc
        return "local://phase02r/sources/" + rel.as_posix()
