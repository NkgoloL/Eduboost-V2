from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_auth_lifecycle_routes_register_after_extraction():
    api_v2 = importlib.import_module("app.api_v2")
    app = api_v2.app
    paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}

    joined = " ".join(sorted(paths)).lower()
    assert "auth" in joined
    assert "register" in joined
    assert "login" in joined
    assert "refresh" in joined


def test_auth_route_endpoint_functions_are_thin_delegates():
    auth = importlib.import_module("app.api_v2_routers.auth")
    source = (ROOT / "app/api_v2_routers/auth.py").read_text(encoding="utf-8")
    assert hasattr(auth, "AuthApplicationService")
    assert "auth_service.register(" in source
    assert "auth_service.login(" in source
    assert "auth_service.refresh(" in source
