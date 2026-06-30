"""tests/unit/test_job_runtime_integrity.py
Unit tests for job runtime integrity validation.
"""
from __future__ import annotations

import pytest

from app.services.job_runtime_integrity import (
    JobRuntimeIntegrityError,
    UNSAFE_TYPE_NAME_FRAGMENTS,
    assert_json_serializable_payload,
    assert_no_runtime_objects,
    validate_arq_job_payload,
)


class MockSession:
    """Mock session object for testing unsafe type detection."""
    pass


class MockRepository:
    """Mock repository object for testing unsafe type detection."""
    pass


class MockService:
    """Mock service object for testing unsafe type detection."""
    pass


class MockRequest:
    """Mock request object for testing unsafe type detection."""
    pass


class MockResponse:
    """Mock response object for testing unsafe type detection."""
    pass


@pytest.mark.unit
def test_unsafe_type_name_fragments_contains_expected_types():
    """Verify UNSAFE_TYPE_NAME_FRAGMENTS contains expected runtime types."""
    assert "Session" in UNSAFE_TYPE_NAME_FRAGMENTS
    assert "AsyncSession" in UNSAFE_TYPE_NAME_FRAGMENTS
    assert "Repository" in UNSAFE_TYPE_NAME_FRAGMENTS
    assert "Service" in UNSAFE_TYPE_NAME_FRAGMENTS
    assert "Request" in UNSAFE_TYPE_NAME_FRAGMENTS
    assert "Response" in UNSAFE_TYPE_NAME_FRAGMENTS


@pytest.mark.unit
def test_assert_json_serializable_payload_with_dict():
    """Verify assert_json_serializable_payload accepts serializable dict."""
    payload = {"key": "value", "number": 123}
    assert_json_serializable_payload(payload)  # Should not raise


@pytest.mark.unit
def test_assert_json_serializable_payload_with_list():
    """Verify assert_json_serializable_payload accepts serializable list."""
    payload = [1, 2, 3, "test"]
    assert_json_serializable_payload(payload)  # Should not raise


@pytest.mark.unit
def test_assert_json_serializable_payload_with_nested_structures():
    """Verify assert_json_serializable_payload accepts nested structures."""
    payload = {"nested": {"list": [1, 2, 3]}, "value": "test"}
    assert_json_serializable_payload(payload)  # Should not raise




@pytest.mark.unit
def test_assert_no_runtime_objects_with_primitives():
    """Verify assert_no_runtime_objects accepts primitive types."""
    assert_no_runtime_objects(None)
    assert_no_runtime_objects("string")
    assert_no_runtime_objects(123)
    assert_no_runtime_objects(3.14)
    assert_no_runtime_objects(True)


@pytest.mark.unit
def test_assert_no_runtime_objects_with_dict():
    """Verify assert_no_runtime_objects accepts dict with primitives."""
    payload = {"key": "value", "number": 123}
    assert_no_runtime_objects(payload)  # Should not raise


@pytest.mark.unit
def test_assert_no_runtime_objects_with_list():
    """Verify assert_no_runtime_objects accepts list with primitives."""
    payload = [1, 2, 3, "test"]
    assert_no_runtime_objects(payload)  # Should not raise


@pytest.mark.unit
def test_assert_no_runtime_objects_with_tuple():
    """Verify assert_no_runtime_objects accepts tuple with primitives."""
    payload = (1, 2, 3, "test")
    assert_no_runtime_objects(payload)  # Should not raise


@pytest.mark.unit
def test_assert_no_runtime_objects_with_set():
    """Verify assert_no_runtime_objects accepts set with primitives."""
    payload = {1, 2, 3}
    assert_no_runtime_objects(payload)  # Should not raise


@pytest.mark.unit
def test_assert_no_runtime_objects_with_frozenset():
    """Verify assert_no_runtime_objects accepts frozenset with primitives."""
    payload = frozenset([1, 2, 3])
    assert_no_runtime_objects(payload)  # Should not raise


@pytest.mark.unit
def test_assert_no_runtime_objects_raises_on_session():
    """Verify assert_no_runtime_objects raises on Session object."""
    payload = {"session": MockSession()}
    with pytest.raises(JobRuntimeIntegrityError, match="Session"):
        assert_no_runtime_objects(payload)


@pytest.mark.unit
def test_assert_no_runtime_objects_raises_on_repository():
    """Verify assert_no_runtime_objects raises on Repository object."""
    payload = {"repo": MockRepository()}
    with pytest.raises(JobRuntimeIntegrityError, match="Repository"):
        assert_no_runtime_objects(payload)


@pytest.mark.unit
def test_assert_no_runtime_objects_raises_on_service():
    """Verify assert_no_runtime_objects raises on Service object."""
    payload = {"service": MockService()}
    with pytest.raises(JobRuntimeIntegrityError, match="Service"):
        assert_no_runtime_objects(payload)


@pytest.mark.unit
def test_assert_no_runtime_objects_raises_on_request():
    """Verify assert_no_runtime_objects raises on Request object."""
    payload = {"request": MockRequest()}
    with pytest.raises(JobRuntimeIntegrityError, match="Request"):
        assert_no_runtime_objects(payload)


@pytest.mark.unit
def test_assert_no_runtime_objects_raises_on_response():
    """Verify assert_no_runtime_objects raises on Response object."""
    payload = {"response": MockResponse()}
    with pytest.raises(JobRuntimeIntegrityError, match="Response"):
        assert_no_runtime_objects(payload)


@pytest.mark.unit
def test_assert_no_runtime_objects_handles_circular_reference():
    """Verify assert_no_runtime_objects handles circular references gracefully."""
    payload = {"key": "value"}
    payload["circular"] = payload
    assert_no_runtime_objects(payload)  # Should not raise due to identity tracking


@pytest.mark.unit
def test_assert_no_runtime_objects_handles_nested_unsafe_object():
    """Verify assert_no_runtime_objects detects unsafe objects in nested structures."""
    payload = {"outer": {"inner": MockRepository()}}
    with pytest.raises(JobRuntimeIntegrityError, match="Repository"):
        assert_no_runtime_objects(payload)


@pytest.mark.unit
def test_assert_no_runtime_objects_handles_list_with_unsafe_object():
    """Verify assert_no_runtime_objects detects unsafe objects in lists."""
    payload = [1, 2, MockService(), 3]
    with pytest.raises(JobRuntimeIntegrityError, match="Service"):
        assert_no_runtime_objects(payload)


@pytest.mark.unit
def test_assert_no_runtime_objects_handles_object_with_dict_attr():
    """Verify assert_no_runtime_objects inspects object __dict__."""
    class SimpleObject:
        def __init__(self):
            self.data = {"key": "value"}

    payload = SimpleObject()
    assert_no_runtime_objects(payload)  # Should not raise


@pytest.mark.unit
def test_assert_no_runtime_objects_handles_object_with_unsafe_attr():
    """Verify assert_no_runtime_objects detects unsafe objects in __dict__."""
    class Container:
        def __init__(self):
            self.service = MockService()

    payload = Container()
    with pytest.raises(JobRuntimeIntegrityError, match="Service"):
        assert_no_runtime_objects(payload)


@pytest.mark.unit
def test_validate_arq_job_payload_with_valid_args():
    """Verify validate_arq_job_payload accepts valid args and kwargs."""
    validate_arq_job_payload("arg1", "arg2", key="value", number=123)  # Should not raise


@pytest.mark.unit
def test_validate_arq_job_payload_with_dict_args():
    """Verify validate_arq_job_payload accepts dict args."""
    validate_arq_job_payload({"key": "value"}, {"nested": [1, 2, 3]})  # Should not raise


@pytest.mark.unit
def test_validate_arq_job_payload_raises_on_runtime_object_in_args():
    """Verify validate_arq_job_payload raises on runtime object in args."""
    with pytest.raises(JobRuntimeIntegrityError, match="runtime object"):
        validate_arq_job_payload(MockSession())


@pytest.mark.unit
def test_validate_arq_job_payload_raises_on_runtime_object_in_kwargs():
    """Verify validate_arq_job_payload raises on runtime object in kwargs."""
    with pytest.raises(JobRuntimeIntegrityError, match="runtime object"):
        validate_arq_job_payload(service=MockService())


@pytest.mark.unit
def test_validate_arq_job_payload_raises_on_unserializable():
    """Verify validate_arq_job_payload raises on unserializable payload."""
    with pytest.raises(JobRuntimeIntegrityError, match="runtime object"):
        validate_arq_job_payload(MockSession())


@pytest.mark.unit
def test_assert_no_runtime_objects_with_empty_structures():
    """Verify assert_no_runtime_objects accepts empty structures."""
    assert_no_runtime_objects({})
    assert_no_runtime_objects([])
    assert_no_runtime_objects(())
    assert_no_runtime_objects(set())
    assert_no_runtime_objects(frozenset())


@pytest.mark.unit
def test_assert_json_serializable_payload_with_datetime():
    """Verify assert_json_serializable_payload handles datetime with default=str."""
    from datetime import datetime
    payload = {"timestamp": datetime.now()}
    assert_json_serializable_payload(payload)  # Should not raise with default=str


@pytest.mark.unit
def test_assert_json_serializable_payload_raises_on_unserializable():
    """Verify assert_json_serializable_payload raises on truly unserializable object."""
    class Unserializable:
        def __str__(self):
            raise RuntimeError("Cannot convert to string")

    payload = {"item": Unserializable()}
    with pytest.raises(JobRuntimeIntegrityError, match="not JSON serializable"):
        assert_json_serializable_payload(payload)


@pytest.mark.unit
def test_module_exports_all_public_symbols():
    """Verify __all__ contains expected public symbols."""
    from app.services import job_runtime_integrity
    expected = {
        "JobRuntimeIntegrityError",
        "assert_json_serializable_payload",
        "assert_no_runtime_objects",
        "validate_arq_job_payload",
    }
    assert set(job_runtime_integrity.__all__) == expected
