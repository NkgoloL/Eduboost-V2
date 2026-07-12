from __future__ import annotations

import builtins
import importlib
import importlib.util
import sys
from collections.abc import Iterator
from contextlib import contextmanager

import pytest

MODULES_TO_CLEAR = (
    "tools.etl.mcp_compat",
    "tools.etl.etl_mcp_server",
    "tools.etl.etl_mcp_server_v2",
    "tools.etl.etl_mcp_server_v3_additions",
)
BLOCKED_IMPORT_PREFIXES = ("mcp", "fastmcp")


def _clear_mcp_modules() -> None:
    for name in MODULES_TO_CLEAR:
        sys.modules.pop(name, None)


@pytest.fixture(autouse=True)
def clean_mcp_modules() -> Iterator[None]:
    _clear_mcp_modules()
    yield
    _clear_mcp_modules()


@contextmanager
def _blocked_mcp_imports(monkeypatch: pytest.MonkeyPatch):
    original_import = builtins.__import__
    original_find_spec = importlib.util.find_spec

    def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):  # type: ignore[no-untyped-def]
        if any(name == prefix or name.startswith(f"{prefix}.") for prefix in BLOCKED_IMPORT_PREFIXES):
            raise ImportError(f"blocked test import: {name}")
        return original_import(name, globals, locals, fromlist, level)

    def blocked_find_spec(name, package=None):  # type: ignore[no-untyped-def]
        if any(name == prefix or name.startswith(f"{prefix}.") for prefix in BLOCKED_IMPORT_PREFIXES):
            return None
        return original_find_spec(name, package)

    monkeypatch.setattr(builtins, "__import__", blocked_import)
    monkeypatch.setattr(importlib.util, "find_spec", blocked_find_spec)
    yield


def _available_mcp_backend() -> str | None:
    for backend in ("mcp.server.fastmcp", "fastmcp"):
        try:
            if importlib.util.find_spec(backend) is not None:
                return backend
        except ModuleNotFoundError:
            continue
    return None


def test_mcp_compat_fails_closed_without_test_stub_flag(monkeypatch) -> None:
    monkeypatch.delenv("EDUBOOST_ALLOW_MCP_TEST_STUB", raising=False)

    with _blocked_mcp_imports(monkeypatch), pytest.raises(RuntimeError, match="EDUBOOST_ALLOW_MCP_TEST_STUB"):
        importlib.import_module("tools.etl.mcp_compat")


def test_mcp_compat_allows_test_stub_with_explicit_flag(monkeypatch) -> None:
    monkeypatch.setenv("EDUBOOST_ALLOW_MCP_TEST_STUB", "1")

    with _blocked_mcp_imports(monkeypatch):
        compat = importlib.import_module("tools.etl.mcp_compat")
        stub = compat.FastMCP("test", json_response=True)

    assert compat.resolve_supported_fastmcp_backend() is None
    assert stub.name == "test"
    assert stub.settings.json_response is True
    assert stub.settings.streamable_http_path == "/mcp"


def test_real_mcp_backend_is_resolvable_when_installed() -> None:
    backend = _available_mcp_backend()
    if backend is None:
        pytest.skip("Real MCP backend is not installed in this environment")

    compat = importlib.import_module("tools.etl.mcp_compat")
    resolved = compat.resolve_supported_fastmcp_backend()

    assert resolved in {"mcp.server.fastmcp", "fastmcp"}
    assert compat.FASTMCP_BACKEND == resolved
    assert compat.FastMCP is not None
