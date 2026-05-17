from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


class JobRuntimeIntegrityError(ValueError):
    """Raised when a durable job payload contains unsafe runtime objects."""


UNSAFE_TYPE_NAME_FRAGMENTS = (
    "Session",
    "AsyncSession",
    "Repository",
    "Service",
    "Request",
    "Response",
)


def assert_json_serializable_payload(value: Any) -> None:
    try:
        json.dumps(value, default=str)
    except Exception as exc:
        raise JobRuntimeIntegrityError(f"Job payload is not JSON serializable: {exc}") from exc


def assert_no_runtime_objects(value: Any) -> None:
    seen: set[int] = set()

    def walk(item: Any) -> None:
        if item is None or isinstance(item, (str, int, float, bool)):
            return

        identity = id(item)
        if identity in seen:
            return
        seen.add(identity)

        type_name = type(item).__name__
        if any(fragment in type_name for fragment in UNSAFE_TYPE_NAME_FRAGMENTS):
            raise JobRuntimeIntegrityError(f"Durable job payload must not include runtime object {type_name}")

        if isinstance(item, Mapping):
            for child in item.values():
                walk(child)
            return

        if isinstance(item, (list, tuple, set, frozenset)):
            for child in item:
                walk(child)
            return

        if hasattr(item, "__dict__"):
            for child in vars(item).values():
                walk(child)

    walk(value)


def validate_arq_job_payload(*args: Any, **kwargs: Any) -> None:
    assert_no_runtime_objects({"args": args, "kwargs": kwargs})
    assert_json_serializable_payload({"args": args, "kwargs": kwargs})


__all__ = [
    "JobRuntimeIntegrityError",
    "assert_json_serializable_payload",
    "assert_no_runtime_objects",
    "validate_arq_job_payload",
]
