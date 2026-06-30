import types


def test_etl_mcp_server_uses_json_response_mode():
    import tools.etl.etl_mcp_server_v2 as server

    assert server.mcp.settings.json_response is True


def test_start_streamable_http_falls_back_to_settings(monkeypatch):
    import tools.etl.etl_mcp_server_v2 as server

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
