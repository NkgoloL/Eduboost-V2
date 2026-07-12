"""Compatibility import for FastMCP across supported MCP packaging layouts."""
from __future__ import annotations

import importlib.util
import os
from types import SimpleNamespace

_ALLOW_TEST_STUB = os.getenv("EDUBOOST_ALLOW_MCP_TEST_STUB") == "1"


def resolve_supported_fastmcp_backend() -> str | None:
    """Return the supported FastMCP backend available in this environment."""
    for backend in ("mcp.server.fastmcp", "fastmcp"):
        try:
            if importlib.util.find_spec(backend) is not None:
                return backend
        except ModuleNotFoundError:
            continue
    return None


def _build_test_stub() -> type:
    class FastMCP:  # type: ignore[no-redef]
        """Small compatibility fallback for local test environments."""

        def __init__(self, name: str, *, json_response: bool = False, **kwargs) -> None:
            self.name = name
            self.settings = SimpleNamespace(
                json_response=json_response,
                host=kwargs.get("host", "127.0.0.1"),
                port=kwargs.get("port", 8000),
                log_level=kwargs.get("log_level", "INFO"),
                streamable_http_path=kwargs.get("streamable_http_path", "/mcp"),
            )
            self._registered_tools: list[tuple[str, str | None]] = []

        def _decorator(self, kind: str, name: str | None = None, **_kwargs):
            def wrapper(func):
                self._registered_tools.append((kind, name or func.__name__))
                return func

            return wrapper

        def tool(self, *args, **kwargs):
            if args and callable(args[0]) and len(args) == 1 and not kwargs:
                return self._decorator("tool")(args[0])
            name = kwargs.pop("name", None)
            return self._decorator("tool", name=name, **kwargs)

        def resource(self, *args, **kwargs):
            if args and callable(args[0]) and len(args) == 1 and not kwargs:
                return self._decorator("resource")(args[0])
            name = kwargs.pop("name", None)
            return self._decorator("resource", name=name, **kwargs)

        def prompt(self, *args, **kwargs):
            if args and callable(args[0]) and len(args) == 1 and not kwargs:
                return self._decorator("prompt")(args[0])
            name = kwargs.pop("name", None)
            return self._decorator("prompt", name=name, **kwargs)

        def run(self, *args, **kwargs):  # pragma: no cover - compatibility shim
            self._last_run = {"args": args, "kwargs": kwargs}
            return None

        def streamable_http_app(self):  # pragma: no cover - compatibility shim
            async def app(scope, receive, send):
                if scope.get("type") == "http":
                    await send(
                        {
                            "type": "http.response.start",
                            "status": 200,
                            "headers": [(b"content-type", b"application/json")],
                        }
                    )
                    await send(
                        {
                            "type": "http.response.body",
                            "body": b'{"jsonrpc":"2.0","result":null,"id":null}',
                        }
                    )

            return app

    FastMCP.__module__ = __name__
    return FastMCP


try:
    from mcp.server.fastmcp import FastMCP as FastMCP
    FASTMCP_BACKEND = "mcp.server.fastmcp"
except (ImportError, ModuleNotFoundError):
    try:
        from fastmcp import FastMCP as FastMCP
        FASTMCP_BACKEND = "fastmcp"
    except (ImportError, ModuleNotFoundError):
        if not _ALLOW_TEST_STUB:
            raise RuntimeError(
                "FastMCP is unavailable. Install the supported MCP dependency or set "
                "EDUBOOST_ALLOW_MCP_TEST_STUB=1 for local test-only stub execution."
            )
        FastMCP = _build_test_stub()
        FASTMCP_BACKEND = "test-stub"

__all__ = [
    "FastMCP",
    "FASTMCP_BACKEND",
    "resolve_supported_fastmcp_backend",
]
