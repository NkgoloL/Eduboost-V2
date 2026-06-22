from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from app.services.curriculum.acquisition import AcquisitionRejectedError, ControlledAcquisitionService
from app.services.curriculum.object_storage import LocalImmutableObjectStore


def rights(**overrides):
    value = {"decision_status": "approved", "may_store_original": True}
    value.update(overrides)
    return value


def test_allowed_source_creates_immutable_object(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    store_root = tmp_path / "objects"
    source_root.mkdir()
    source = source_root / "caps.txt"
    source.write_text("Numbers, operations and relationships", encoding="utf-8")
    sha = hashlib.sha256(source.read_bytes()).hexdigest()

    service = ControlledAcquisitionService(object_store=LocalImmutableObjectStore(store_root))
    acquired = service.acquire_local_file(source, expected_sha256=sha, rights_decision=rights(), allowed_root=source_root)

    assert acquired.sha256 == sha
    assert acquired.size_bytes == source.stat().st_size
    assert acquired.storage_backend == "local-content-addressed"
    assert acquired.object_uri.startswith("local://phase02r/sources/")


def test_same_sha_acquisition_is_idempotent(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    store_root = tmp_path / "objects"
    source_root.mkdir()
    source = source_root / "caps.txt"
    source.write_text("Fractions", encoding="utf-8")
    sha = hashlib.sha256(source.read_bytes()).hexdigest()

    service = ControlledAcquisitionService(object_store=LocalImmutableObjectStore(store_root))
    first = service.acquire_local_file(source, expected_sha256=sha, rights_decision=rights(), allowed_root=source_root)
    second = service.acquire_local_file(source, expected_sha256=sha, rights_decision=rights(), allowed_root=source_root)

    assert second.object_uri == first.object_uri


def test_checksum_mismatch_fails(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    store_root = tmp_path / "objects"
    source_root.mkdir()
    source = source_root / "caps.txt"
    source.write_text("Measurement", encoding="utf-8")

    service = ControlledAcquisitionService(object_store=LocalImmutableObjectStore(store_root))
    with pytest.raises(AcquisitionRejectedError):
        service.acquire_local_file(source, expected_sha256="0" * 64, rights_decision=rights(), allowed_root=source_root)


def test_missing_or_denied_rights_fail(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    store_root = tmp_path / "objects"
    source_root.mkdir()
    source = source_root / "caps.txt"
    source.write_text("Data handling", encoding="utf-8")
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    service = ControlledAcquisitionService(object_store=LocalImmutableObjectStore(store_root))

    with pytest.raises(AcquisitionRejectedError):
        service.acquire_local_file(source, expected_sha256=sha, rights_decision=None, allowed_root=source_root)

    with pytest.raises(AcquisitionRejectedError):
        service.acquire_local_file(
            source,
            expected_sha256=sha,
            rights_decision=rights(may_store_original=False),
            allowed_root=source_root,
        )


def test_expired_rights_fail(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source = source_root / "caps.txt"
    source.write_text("Expired", encoding="utf-8")
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    service = ControlledAcquisitionService(object_store=LocalImmutableObjectStore(tmp_path / "objects"))

    with pytest.raises(AcquisitionRejectedError):
        service.acquire_local_file(
            source,
            expected_sha256=sha,
            rights_decision=rights(expires_at="2000-01-01T00:00:00+00:00"),
            allowed_root=source_root,
        )


def test_path_escape_fails(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    source_root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("escape", encoding="utf-8")
    sha = hashlib.sha256(outside.read_bytes()).hexdigest()

    service = ControlledAcquisitionService(object_store=LocalImmutableObjectStore(tmp_path / "objects"))
    with pytest.raises(AcquisitionRejectedError):
        service.acquire_local_file(outside, expected_sha256=sha, rights_decision=rights(), allowed_root=source_root)


def test_unsupported_extension_fails(tmp_path: Path) -> None:
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source = source_root / "caps.exe"
    source.write_bytes(b"nope")
    sha = hashlib.sha256(source.read_bytes()).hexdigest()

    service = ControlledAcquisitionService(object_store=LocalImmutableObjectStore(tmp_path / "objects"))
    with pytest.raises(AcquisitionRejectedError):
        service.acquire_local_file(source, expected_sha256=sha, rights_decision=rights(), allowed_root=source_root)


def test_pii_metadata_guard_rejects_forbidden_fields() -> None:
    from app.services.curriculum.acquisition import assert_no_learner_pii_in_source_metadata

    with pytest.raises(AcquisitionRejectedError):
        assert_no_learner_pii_in_source_metadata({"learner_id": "abc"})
