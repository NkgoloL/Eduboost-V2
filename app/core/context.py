"""Request / correlation ID context helper using contextvars.
Provides a small API to set/get the current request id from any async context.
"""
from __future__ import annotations

import contextvars
from typing import Optional

_request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)


def set_request_id(request_id: str | None) -> None:
    """Set the current request id for the running context."""
    if request_id is None:
        try:
            _request_id_var.set(None)
        except Exception:
            pass
    else:
        _request_id_var.set(request_id)


def get_request_id(default: str = "unknown") -> str:
    """Return the current request id or `default` when not set."""
    rid = _request_id_var.get()
    return rid if rid is not None else default


def clear_request_id() -> None:
    """Clear the request id from the current context."""
    try:
        _request_id_var.set(None)
    except Exception:
        pass
