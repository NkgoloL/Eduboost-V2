"""Unit tests for content generation run lock."""
from __future__ import annotations

import pytest

from app.services.content_generation_run_lock import (
    ContentGenerationRunLock,
    DEFAULT_LOCK_TTL_MINUTES,
    LockAcquisitionResult,
)


@pytest.mark.unit
def test_lock_instantiation() -> None:
    """Lock can be instantiated."""
    lock = ContentGenerationRunLock()
    assert lock is not None
    assert lock.ttl_minutes == DEFAULT_LOCK_TTL_MINUTES


@pytest.mark.unit
def test_lock_instantiation_with_custom_ttl() -> None:
    """Lock can be instantiated with custom TTL."""
    lock = ContentGenerationRunLock(ttl_minutes=60)
    assert lock.ttl_minutes == 60
    assert lock.ttl_seconds == 3600


@pytest.mark.unit
def test_lock_has_acquire_method() -> None:
    """Lock has acquire method."""
    lock = ContentGenerationRunLock()
    assert hasattr(lock, "acquire")
    assert callable(getattr(lock, "acquire"))


@pytest.mark.unit
def test_lock_has_release_method() -> None:
    """Lock has release method."""
    lock = ContentGenerationRunLock()
    assert hasattr(lock, "release")
    assert callable(getattr(lock, "release"))


@pytest.mark.unit
def test_lock_acquisition_result_dataclass() -> None:
    """LockAcquisitionResult is a frozen dataclass."""
    result = LockAcquisitionResult(
        acquired=True,
        lock_holder="test_holder",
        lock_acquired_at="1234567890",
        lock_expires_at="1234567990",
    )
    assert result.acquired is True
    assert result.lock_holder == "test_holder"
    assert result.lock_acquired_at == "1234567890"
    assert result.lock_expires_at == "1234567990"
    assert result.error is None


@pytest.mark.unit
def test_lock_acquisition_result_with_error() -> None:
    """LockAcquisitionResult can include error."""
    result = LockAcquisitionResult(
        acquired=False,
        error="Lock already held",
    )
    assert result.acquired is False
    assert result.error == "Lock already held"
