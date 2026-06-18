"""Controlled acquisition primitives for Phase 2R Gate 2R.2."""
from __future__ import annotations

import hashlib
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ALLOWED_EXTENSIONS = frozenset({".pdf", ".txt", ".md", ".json"})
_ALLOWED_MEDIA_TYPES = frozenset({
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/json",
})


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
    storage_backend: str = "local-fixture"
    metadata: dict[str, Any] = field(default_factory=dict)


class ControlledAcquisitionService:
    """Validate and fingerprint a locally provided source file.

    This service deliberately does not perform arbitrary network downloads. URL
    acquisition must be wired through an approved downloader that records the
    redirect chain, HTTP metadata, checksum, and malware scan result.
    """

    def __init__(self, policy: AcquisitionPolicy | None = None) -> None:
        self.policy = policy or AcquisitionPolicy()

    def acquire_local_file(
        self,
        path: str | Path,
        *,
        expected_sha256: str | None,
        object_uri_prefix: str = "object://phase02r/local",
    ) -> AcquiredObject:
        source = Path(path)
        if not source.is_file():
            raise AcquisitionRejectedError(f"source file does not exist: {source}")
        suffix = source.suffix.lower()
        if suffix not in self.policy.allowed_extensions:
            raise AcquisitionRejectedError(f"file extension is not allowed: {suffix}")
        size = source.stat().st_size
        if size <= 0:
            raise AcquisitionRejectedError("source file is empty")
        if size > self.policy.max_file_size_bytes:
            raise AcquisitionRejectedError("source file exceeds maximum allowed size")
        sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
        if self.policy.require_expected_sha256 and not expected_sha256:
            raise AcquisitionRejectedError("expected_sha256 is required")
        if expected_sha256 and expected_sha256.lower() != sha256:
            raise AcquisitionRejectedError("source checksum does not match expected_sha256")
        media_type = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
        if media_type not in self.policy.allowed_media_types:
            # Text fixtures often map to text/plain correctly; refuse ambiguous
            # binary objects rather than relying on extension alone.
            raise AcquisitionRejectedError(f"media type is not allowed: {media_type}")
        return AcquiredObject(
            object_uri=f"{object_uri_prefix.rstrip('/')}/{sha256}{suffix}",
            sha256=sha256,
            size_bytes=size,
            media_type=media_type,
            metadata={"filename": source.name, "extension": suffix},
        )


def assert_no_learner_pii_in_source_metadata(metadata: dict[str, Any]) -> None:
    """Reject common learner-PII fields from entering corpus metadata."""
    forbidden = {"learner_id", "guardian_id", "email", "phone", "id_number", "conversation_id"}
    present = sorted(forbidden & set(metadata))
    if present:
        raise AcquisitionRejectedError(f"learner PII fields are forbidden in corpus metadata: {', '.join(present)}")
