from __future__ import annotations

import importlib
import sys
import types
from collections.abc import Iterator

import pytest

MODULES_TO_CLEAR = (
    "tools.etl.mcp_compat",
    "tools.etl.etl_mcp_server",
    "tools.etl.etl_mcp_server_v2",
    "tools.etl.etl_mcp_server_v3_additions",
)


@pytest.fixture(autouse=True)
def clean_mcp_modules() -> Iterator[None]:
    for name in MODULES_TO_CLEAR:
        sys.modules.pop(name, None)
    yield
    for name in MODULES_TO_CLEAR:
        sys.modules.pop(name, None)


def _import_server(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("EDUBOOST_ALLOW_MCP_TEST_STUB", "1")
    return importlib.import_module("tools.etl.etl_mcp_server_v2")


def test_etl_mcp_server_uses_json_response_mode(monkeypatch: pytest.MonkeyPatch):
    server = _import_server(monkeypatch)

    assert server.mcp.settings.json_response is True


def test_start_streamable_http_falls_back_to_settings(monkeypatch: pytest.MonkeyPatch):
    server = _import_server(monkeypatch)

    class FakeSettings(types.SimpleNamespace):
        pass

    class FakeMCP:
        def __init__(self):
            self.settings = FakeSettings(host="127.0.0.1", port=8000, log_level="INFO", streamable_http_path="/mcp")
            self.calls = []

        def run(self, **kwargs):
            self.calls.append(kwargs)
            if "host" in kwargs or "port" in kwargs:
                raise TypeError("FastMCP.run() got an unexpected keyword argument 'host'")

    fake_mcp = FakeMCP()
    called = []

    def fake_run_streamable_http_app(mcp_server, host, port):
        called.append((mcp_server, host, port))

    monkeypatch.setattr(server, "_run_streamable_http_app", fake_run_streamable_http_app)

    server._start_mcp_server(fake_mcp, transport="streamable-http", host="0.0.0.0", port=8765)

    assert fake_mcp.calls == [{"transport": "streamable-http", "host": "0.0.0.0", "port": 8765}]
    assert fake_mcp.settings.host == "0.0.0.0"
    assert fake_mcp.settings.port == 8765
    assert called == [(fake_mcp, "0.0.0.0", 8765)]
