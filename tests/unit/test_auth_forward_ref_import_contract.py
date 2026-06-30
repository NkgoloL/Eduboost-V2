from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_auth_router_exports_register_request_for_fastapi_forward_refs():
    auth = importlib.import_module("app.api_v2_routers.auth")
    assert hasattr(auth, "RegisterRequest")


def test_app_api_v2_imports_after_auth_forward_ref_repair():
    api_v2 = importlib.import_module("app.api_v2")
    app = api_v2.app
    paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}
    assert any("/register" in path for path in paths)


def test_auth_forward_ref_repair_report_exists():
    assert (ROOT / "docs/release/auth_forward_ref_repair_report.md").exists()


def test_makefile_contains_auth_forward_ref_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-forward-refs-repair:" in text
    assert "auth-forward-refs-check:" in text
    assert "backend-implementation-831-870R-forward-ref-check:" in text
