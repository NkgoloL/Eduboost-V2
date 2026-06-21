"""Controlled acquisition primitives for Phase 2R Gate 2R.2."""
from __future__ import annotations

import hashlib
import mimetypes
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.curriculum.object_storage import LocalImmutableObjectStore, ObjectStorageRejectedError

mimetypes.add_type("text/markdown", ".md")

_ALLOWED_EXTENSIONS = frozenset({".pdf", ".txt", ".md", ".json"})
_ALLOWED_MEDIA_TYPES = frozenset({"application/pdf", "text/plain", "text/markdown", "application/json"})


class AcquisitionRejectedError(ValueError):
    """Raised when a source cannot enter controlled acquisition."""


@dataclass(frozen=True)
class AcquisitionPolicy:
    max_file_size_bytes: int = 50 * 1024 * 1024
    allowed_extensions: frozenset[str] = _ALLOWED_EXTENSIONS
    allowed_media_types: frozenset[str] = _ALLOWED_MEDIA_TYPES
    require_expected_sha256: bool = True
    allow_network_downloads: bool = False


@dataclass(frozen=True)
class AcquiredObject:
    object_uri: str
    sha256: str
    size_bytes: int
    media_type: str
    storage_backend: str = "local-content-addressed"
    malware_scan_status: str = "not_required"
    metadata: dict[str, Any] = field(default_factory=dict)


def assert_no_learner_pii_in_source_metadata(metadata: dict[str, Any]) -> None:
    """Reject common learner-PII fields from entering corpus metadata."""
    forbidden = {"learner_id", "guardian_id", "email", "phone", "id_number", "conversation_id"}
    present = sorted(forbidden & set(metadata))
    if present:
        raise AcquisitionRejectedError(f"learner PII fields are forbidden in corpus metadata: {', '.join(present)}")


def validate_may_store_original(rights_decision: dict[str, Any] | None) -> None:
    """Fail closed unless rights explicitly allow storing the original source."""
    if not rights_decision:
        raise AcquisitionRejectedError("missing rights decision")
    if rights_decision.get("decision_status") not in {"approved", "approved_with_conditions"}:
        raise AcquisitionRejectedError("rights decision is not approved")
    if not rights_decision.get("may_store_original"):
        raise AcquisitionRejectedError("rights decision does not allow storing original")
    expires_at = rights_decision.get("expires_at")
    if expires_at:
        expires = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
        if expires <= datetime.now(timezone.utc):
            raise AcquisitionRejectedError("rights decision is expired")


class ControlledAcquisitionService:
    """Validate, fingerprint, and store locally provided source files.

    Network acquisition is intentionally outside this service and remains gated
    by a CLI flag.  Gate 2R.2 implementation tests use deterministic local
    files; closure evidence may then acquire the real approved source.
    """

    def __init__(
        self,
        policy: AcquisitionPolicy | None = None,
        object_store: LocalImmutableObjectStore | None = None,
    ) -> None:
        self.policy = policy or AcquisitionPolicy()
        self.object_store = object_store or LocalImmutableObjectStore()

    def _resolve_safe_source(self, path: str | Path, *, allowed_root: str | Path | None = None) -> Path:
        source = Path(path).resolve()
        if allowed_root is not None:
            root = Path(allowed_root).resolve()
            try:
                source.relative_to(root)
            except ValueError as exc:
                raise AcquisitionRejectedError("source path escaped allowed root") from exc
        if not source.is_file():
            raise AcquisitionRejectedError(f"source file does not exist: {source}")
        return source

    def _media_type_for(self, source: Path) -> str:
        if source.suffix.lower() == ".md":
            return "text/markdown"
        return mimetypes.guess_type(source.name)[0] or "application/octet-stream"

    def acquire_local_file(
        self,
        path: str | Path,
        *,
        expected_sha256: str | None,
        rights_decision: dict[str, Any] | None = None,
        allowed_root: str | Path | None = None,
        object_uri_prefix: str = "object://phase02r/local",
        persist_object: bool = True,
    ) -> AcquiredObject:
        validate_may_store_original(rights_decision)
        source = self._resolve_safe_source(path, allowed_root=allowed_root)
        suffix = source.suffix.lower()
        if suffix not in self.policy.allowed_extensions:
            raise AcquisitionRejectedError(f"file extension is not allowed: {suffix}")

        size = source.stat().st_size
        if size <= 0:
            raise AcquisitionRejectedError("source file is empty")
        if size > self.policy.max_file_size_bytes:
            raise AcquisitionRejectedError("source file exceeds maximum allowed size")

        digest = hashlib.sha256()
        with source.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        sha256 = digest.hexdigest()

        if self.policy.require_expected_sha256 and not expected_sha256:
            raise AcquisitionRejectedError("expected_sha256 is required")
        if expected_sha256 and expected_sha256.lower() != sha256:
            raise AcquisitionRejectedError("source checksum does not match expected_sha256")

        media_type = self._media_type_for(source)
        if media_type not in self.policy.allowed_media_types:
            raise AcquisitionRejectedError(f"media type is not allowed: {media_type}")

        if persist_object:
            try:
                stored = self.object_store.put_file(
                    source,
                    expected_sha256=sha256,
                    suffix=suffix,
                    max_bytes=self.policy.max_file_size_bytes,
                )
            except ObjectStorageRejectedError as exc:
                raise AcquisitionRejectedError(str(exc)) from exc
            object_uri = stored.object_uri
            storage_backend = stored.storage_backend
            size = stored.size_bytes
        else:
            object_uri = f"{object_uri_prefix.rstrip('/')}/{sha256}{suffix}"
            storage_backend = "local-fixture"

        metadata = {"filename": source.name, "extension": suffix}
        assert_no_learner_pii_in_source_metadata(metadata)
        return AcquiredObject(
            object_uri=object_uri,
            sha256=sha256,
            size_bytes=size,
            media_type=media_type,
            storage_backend=storage_backend,
            malware_scan_status="not_required",
            metadata=metadata,
        )
