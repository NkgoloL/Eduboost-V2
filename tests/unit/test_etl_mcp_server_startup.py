from __future__ import annotations

import builtins
import importlib
import importlib.util
import sys
import types
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


@pytest.fixture
def forced_mcp_test_stub(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("EDUBOOST_ALLOW_MCP_TEST_STUB", "1")
    with _blocked_mcp_imports(monkeypatch):
        _clear_mcp_modules()
        server = importlib.import_module("tools.etl.etl_mcp_server")
        compat = importlib.import_module("tools.etl.mcp_compat")

        assert compat.FASTMCP_BACKEND == "test-stub"
        yield server

    _clear_mcp_modules()


def test_etl_mcp_server_uses_json_response_mode(forced_mcp_test_stub):
    server = forced_mcp_test_stub
    assert server.mcp.settings.json_response is True


def test_start_streamable_http_falls_back_to_settings(monkeypatch: pytest.MonkeyPatch, forced_mcp_test_stub):
    server = forced_mcp_test_stub

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


def test_etl_mcp_server_registers_all_32_tools(forced_mcp_test_stub):
    server = forced_mcp_test_stub
    tool_names = {name for kind, name in server.mcp._registered_tools if kind == "tool"}
    expected_tools = {
        "etl_ingest_document", "etl_get_document", "etl_list_documents", "etl_run_pipeline",
        "etl_run_stage", "etl_approve_document", "etl_reject_document", "etl_reprocess_document",
        "etl_get_review_queue", "etl_get_pipeline_stats", "etl_get_content_gaps", "etl_get_quality_report",
        "etl_get_document_chunks", "etl_update_metadata", "etl_create_document_version", "etl_search_fulltext",
        "etl_generate_training_data", "etl_list_training_datasets", "etl_export_dataset", "etl_submit_feedback",
        "etl_get_monitoring_report", "etl_get_completeness_report",
        "etl_get_audit_trail", "etl_deprecate_document", "etl_bulk_review", "etl_assign_reviewer",
        "etl_get_reviewer_workload", "etl_split_dataset", "etl_check_contamination",
        "etl_get_dataset_statistics", "etl_resolve_feedback", "etl_get_metric_window",
    }
    assert expected_tools.issubset(tool_names)
    assert len(tool_names) == 32


def test_etl_mcp_server_pipeline_is_v3(forced_mcp_test_stub, monkeypatch, tmp_path):
    server = forced_mcp_test_stub
    monkeypatch.setattr(server, "ETL_DB_URL", f"sqlite:///{tmp_path}/test_etl.db")
    monkeypatch.setattr(server, "ETL_STORAGE", str(tmp_path / "storage"))
    monkeypatch.setattr(server, "_pipeline", None)

    from app.services.etl.etl_pipeline_v3_additions import EduboostETLv3
    pipe = server.pipeline()
    assert isinstance(pipe, EduboostETLv3)


def test_etl_mcp_server_v2_shim_deprecation_warning(forced_mcp_test_stub):
    import warnings
    import importlib

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        # Ensure fresh import to observe module-level warning
        if "tools.etl.etl_mcp_server_v2" in sys.modules:
            del sys.modules["tools.etl.etl_mcp_server_v2"]
        v2_module = importlib.import_module("tools.etl.etl_mcp_server_v2")

        dep_warnings = [w for w in recorded if issubclass(w.category, DeprecationWarning)]
        assert len(dep_warnings) >= 1
        assert "tools.etl.etl_mcp_server_v2 is deprecated" in str(dep_warnings[0].message)
        assert v2_module.mcp is forced_mcp_test_stub.mcp
        assert hasattr(v2_module, "etl_get_metric_window")
